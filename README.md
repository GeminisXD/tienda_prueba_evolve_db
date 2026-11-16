# Evolve Store

Tienda online de ejemplo: **FastAPI + PostgreSQL** en el backend, **React + Vite + Tailwind** en el frontend, carrito persistente y pago con **Stripe Checkout**.

## Funcionalidades

- Catálogo de productos con imágenes y avisos de stock.
- Carrito que se conserva al recargar (localStorage).
- Registro e inicio de sesión con JWT (bcrypt).
- Pago real mediante Stripe Checkout; al confirmarse, el pedido se marca como pagado y se descuenta el stock.
- Trazabilidad: cada petición lleva su `X-Trace-ID`.

## Arranque rápido

Necesitas Python 3.13+, Node 20+ y Docker con Docker Desktop en marcha.

**1. Configuración.** Copia `.env.example` a `.env` y rellénalo:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL (por defecto, la del compose) |
| `SECRET_KEY` | Clave para firmar los JWT; usa un valor largo y aleatorio |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe (`sk_test_...`); sin ella, el resto funciona igual |
| `STRIPE_WEBHOOK_SECRET` | Opcional; solo si usas el webhook |
| `FRONTEND_URL` | Origen del frontend (CORS y redirecciones de Stripe) |

Nunca subas `.env` al repositorio: está en `.gitignore`.

**2. Backend** (terminal 1, en la raíz):

```bash
docker compose up -d db
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload
```

API en http://localhost:8000 · documentación interactiva en `/docs`.

**3. Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173. Si tu API no está en `http://localhost:8000`, define `VITE_API_URL` en un `.env` dentro de `frontend/`.

**Usuarios de prueba** (los crea el seed): `cliente1@evolvestore.com` … `cliente10@evolvestore.com`, contraseña `PasswordN!` (con N el número).

## Pago con Stripe

1. Pon tu `sk_test_...` en `.env` y reinicia la API.
2. Añade productos al carrito, inicia sesión y pulsa **Pagar con Stripe**.
3. Con la clave de prueba, usa la tarjeta `4242 4242 4242 4242`, cualquier fecha futura y cualquier CVC.
4. Stripe redirige de vuelta; el backend consulta a Stripe, marca el pedido como `paid` y descuenta el stock. El webhook (`POST /orders/webhook`) hace lo mismo de forma asíncrona si está configurado.

La moneda es EUR (constante `CURRENCY` en `app/routers/orders.py`).

## Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/products/` | No | Lista de productos |
| GET | `/products/{id}` | No | Detalle |
| POST | `/products/` | Sí | Crear producto |
| POST | `/auth/register` | No | Alta de usuario |
| POST | `/auth/login` | No | Devuelve JWT (formulario OAuth2, `username` = email) |
| GET | `/auth/me` | Sí | Usuario actual |
| POST | `/orders/checkout` | Sí | Crea pedido y sesión de Stripe |
| POST | `/orders/confirm/{session_id}` | Sí | Confirma el pago al volver de Stripe |
| GET | `/orders/` | Sí | Pedidos del usuario |
| POST | `/orders/webhook` | Firma Stripe | Webhook de Stripe |

## Estructura

```
app/
  main.py            Aplicación FastAPI, CORS y routers
  database.py        Motor y sesión de SQLAlchemy
  models.py          User, Product, Order, OrderItem
  schemas.py         Esquemas Pydantic
  middleware.py      X-Trace-ID y log de peticiones
  core/              Config por entorno, seguridad y dependencias
  routers/           auth, products, orders
alembic/             Migraciones
seed_data.py         Datos de prueba
docker-compose.yml   PostgreSQL, Elasticsearch y Kibana
frontend/            Aplicación React
```

Migraciones nuevas: `alembic revision --autogenerate -m "descripción"` y `alembic upgrade head`.

## Pendiente

- Pruebas automáticas.
- Roles: ahora cualquier usuario autenticado puede crear productos.
- Historial de pedidos en el frontend (el endpoint ya existe).
