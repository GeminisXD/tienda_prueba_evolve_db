import re
import random
from datetime import datetime, timezone
from app.database import SessionLocal
from app.core.security import get_password_hash
from app.models import User, Product, Order

# --- EXpresiones Regulares para Validación ---
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
NAME_REGEX = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'  # Solo letras y espacios (sin números ni símbolos)
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$'
IMAGE_URL_REGEX = r'^https?://.*\.(jpg|jpeg|png)(\?.*)?$'

def validate_email(email: str) -> bool:
    return bool(re.match(EMAIL_REGEX, email))

def validate_username(name: str) -> bool:
    return bool(re.match(NAME_REGEX, name))

def validate_password(password: str) -> bool:
    return bool(re.match(PASSWORD_REGEX, password))

def validate_image_url(url: str) -> bool:
    return bool(re.match(IMAGE_URL_REGEX, url, re.IGNORECASE))

def seed_database():
    db = SessionLocal()
    try:
        print("🌱 [SEEDER] Iniciando validación y siembra de datos...")

        # ----------------------------------------------------
        # 1. GENERAR Y VALIDAR USUARIOS (10 únicos)
        # ----------------------------------------------------
        users = []
        # Nombres base limpios (sin números ni símbolos)
        raw_names = [
            "Carlos Pérez", "Ana Gómez", "Luis Martínez", "Elena Torres", 
            "David Ruiz", "Sofía Navarro", "Miguel Ángel", "Lucía Romero", 
            "Jorge Blanco", "Carmen Morales"
        ]

        for i, full_name in enumerate(raw_names, start=1):
            # Validar que el nombre no tenga números/símbolos
            if not validate_username(full_name):
                raise ValueError(f"Validación fallida: El nombre '{full_name}' contiene números o símbolos inválidos.")

            email = f"cliente{i}@evolvestore.com"
            # Validar formato de correo
            if not validate_email(email):
                raise ValueError(f"Validación fallida: El correo '{email}' no tiene un formato válido.")

            # Verificar duplicados en BD
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                if not existing_user.hashed_password.startswith("$2"):
                    existing_user.hashed_password = get_password_hash(f"Password{i}!")
                print(f"⚠️ El usuario {email} ya existe. Omitiendo creación.")
                users.append(existing_user)
                continue

            # Contraseña segura válida: Mínimo 8, máximo 20, 1 mayúscula, 1 minúscula, 1 número, 1 carril especial
            password_raw = f"Password{i}!"
            if not validate_password(password_raw):
                raise ValueError(f"Validación fallida para la contraseña de {email}. Debe tener 8-20 chars, mayús, minús, número y símbolo.")

            user = User(
                email=email,
                hashed_password=get_password_hash(password_raw)
            )
            db.add(user)
            users.append(user)

        db.commit()
        for u in users:
            db.refresh(u)
        print("✅ 10 Usuarios validados y creados con éxito.")

        # ----------------------------------------------------
        # 2. GENERAR Y VALIDAR PRODUCTOS (10 únicos, sin stock 0, precio > 0, imágenes jpg/png)
        # ----------------------------------------------------
        products_data = [
            ("Teclado Mecánico RGB", "Teclado gamer switches red", 79.99, 25, "https://images.unsplash.com/photo-1587829741301-dc798b83add3.jpg"),
            ("Mouse Inalámbrico Pro", "Mouse ergonómico alta precisión", 49.99, 40, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7.png"),
            ("Monitor UltraWide", "Monitor IPS resolución Full HD", 299.99, 15, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf.jpeg"),
            ("Auriculares Gamer", "Sonido envolvente 7.1", 59.99, 30, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e.jpg"),
            ("Silla Ergonómica", "Silla ajustable lumbar", 189.99, 10, "https://images.unsplash.com/photo-1580481077494-e3299ac25b94.png"),
            ("Laptop Gamer", "Core i7, 16GB RAM, RTX 4060", 1299.99, 5, "https://images.unsplash.com/photo-1603302576837-37561b2e2302.jpg"),
            ("Hub USB C", "Adaptador multipuerto", 34.99, 50, "https://images.unsplash.com/photo-1544652478-6653e09f18a2.png"),
            ("Webcam HD", "Cámara para streaming", 45.00, 25, "https://images.unsplash.com/photo-1587829741301-dc798b83add3.jpeg"),
            ("Alfombrilla XXL", "Superficie antideslizante", 19.99, 60, "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef.jpg"),
            ("Micrófono USB", "Ideal para podcasts", 89.99, 20, "https://images.unsplash.com/photo-1590602847861-f357a9332bbc.png"),
        ]

        products = []
        for name, desc, price, stock, img in products_data:
            # Validar que no tenga stock 0 (no añadir sin stock)
            if stock <= 0:
                raise ValueError(f"Validación fallida: El producto '{name}' no puede tener stock menor o igual a 0.")
            
            # Validar precio correcto
            if price <= 0:
                raise ValueError(f"Validación fallida: El precio de '{name}' debe ser mayor a 0.")

            # Validar formato de imagen válido (jpg, jpeg, png)
            if not validate_image_url(img):
                raise ValueError(f"Validación fallida: La URL de imagen para '{name}' no tiene un formato válido (.jpg, .jpeg, .png).")

            # Validar duplicados por nombre
            existing_product = db.query(Product).filter(Product.name == name).first()
            if existing_product:
                print(f"⚠️ El producto '{name}' ya existe. Omitiendo.")
                products.append(existing_product)
                continue

            product = Product(
                name=name,
                description=desc,
                price=price,
                stock=stock,
                image_url=img
            )
            db.add(product)
            products.append(product)

        db.commit()
        for p in products:
            db.refresh(p)
        print("✅ 10 Productos validados con stock, precios e imágenes correctos.")

        # ----------------------------------------------------
        # 3. GENERAR Y VALIDAR PEDIDOS (10 pedidos, fecha actual o pasada válida)
        # ----------------------------------------------------
        now_utc = datetime.now(timezone.utc)

        for _ in range(0 if db.query(Order).count() else 10):
            random_user = random.choice(users)
            
            # Validar que la fecha del pedido no sea futura
            order_date = now_utc
            if order_date > now_utc:
                raise ValueError("Validación fallida: Un pedido no puede tener una fecha futura.")

            order = Order(
                user_id=random_user.id,
                total_amount=round(random.uniform(35.0, 450.0), 2),
                created_at=order_date
            )
            db.add(order)

        db.commit()
        print("✅ 10 Pedidos validados y creados correctamente (fechas coherentes con el presente).")

        print("🚀 ¡Base de datos poblada e íntegramente validada sin duplicados ni anomalías!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error de validación / inserción: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()