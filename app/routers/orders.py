from typing import List

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core import config
from app.core.deps import get_current_user
from app.database import get_db
from app.models import Order, OrderItem, Product, User
from app.schemas import CheckoutRequest, CheckoutResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["Pedidos"])

CURRENCY = "eur"

def mark_paid(order: Order, db: Session) -> None:
    if order.status == "paid":
        return
    for item in order.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock = max(product.stock - item.quantity, 0)
    order.status = "paid"
    db.commit()

@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not config.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe no está configurado (falta STRIPE_SECRET_KEY)")

    quantities: dict[int, int] = {}
    for it in data.items:
        quantities[it.product_id] = quantities.get(it.product_id, 0) + it.quantity

    order = Order(user_id=current_user.id, total_amount=0, status="pending")
    line_items = []
    total = 0.0
    for product_id, qty in quantities.items():
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no existe")
        if product.stock < qty:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")
        total += product.price * qty
        order.items.append(OrderItem(product_id=product.id, quantity=qty, unit_price=product.price))
        line_items.append({
            "quantity": qty,
            "price_data": {
                "currency": CURRENCY,
                "unit_amount": round(product.price * 100),
                "product_data": {"name": product.name},
            },
        })
    order.total_amount = round(total, 2)
    db.add(order)
    db.flush()

    stripe.api_key = config.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            customer_email=current_user.email,
            client_reference_id=str(order.id),
            success_url=f"{config.FRONTEND_URL}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{config.FRONTEND_URL}/?checkout=cancel",
        )
    except stripe.StripeError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Error de Stripe: {exc.user_message or exc}")

    order.stripe_session_id = session.id
    db.commit()
    return CheckoutResponse(order_id=order.id, checkout_url=session.url)

@router.post("/confirm/{session_id}", response_model=OrderResponse)
def confirm(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.stripe_session_id == session_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    stripe.api_key = config.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status == "paid":
        mark_paid(order, db)
    return order

@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, request.headers.get("stripe-signature", ""), config.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Firma inválida")
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order = db.query(Order).filter(Order.stripe_session_id == session["id"]).first()
        if order and session.get("payment_status") == "paid":
            mark_paid(order, db)
    return {"received": True}

@router.get("/", response_model=List[OrderResponse])
def my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())
        .all()
    )
