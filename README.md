# Evolve Store

Tienda online de ejemplo: API en FastAPI + PostgreSQL y frontend en React (Vite + Tailwind), con carrito de la compra y pago mediante Stripe Checkout.

## Estructura

```
app/
  main.py            Aplicación FastAPI, CORS y routers
  database.py        Motor y sesión de SQLAlchemy
  models.py          User, Product, Order, OrderItem
  schemas.py         Esquemas Pydantic
  middleware.py      X-Trace-ID y log de peticiones
  core/config.py     Variables de entorno
  core/security.py   Hash bcrypt y JWT
  core/deps.py       Usuario autenticado (get_current_user)
  routers/           auth, products, orders
alembic/             Migraciones
seed_data.py         Datos de prueba (usuarios, productos, pedidos)
docker-compose.yml   PostgreSQL, Elasticsearch y Kibana
filebeat/            Configuración de Filebeat (no está en el compose)
frontend/            Aplicación React
```

## Puesta en marcha

### 1. Configuración

Copia `.env.example` a `.env` y rellénalo:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión a PostgreSQL (por defecto, la del compose) |
| `SECRET_KEY` | Clave para firmar los JWT; usa un valor largo y aleatorio |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe (`sk_test_...` en modo prueba) |
| `STRIPE_WEBHOOK_SECRET` | Opcional; solo si usas el webhook |
| `FRONTEND_URL` | Origen del frontend (CORS y redirecciones de Stripe) |

`.env` está en `.gitignore`: no subas nunca claves al repositorio.

### 2. Base de datos y backend

```bash
docker compose up -d db
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload
```

API en http://localhost:8000, documentación interactiva en http://localhost:8000/docs.

Usuarios de prueba del seed: `cliente1@evolvestore.com` ... `cliente10@evolvestore.com`, contraseña `PasswordN!` (con N el número del cliente).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173. Si la API no está en `http://localhost:8000`, define `VITE_API_URL`.

## Flujo de compra

1. El usuario añade productos al carrito (se guarda en `localStorage`).
2. Para pagar debe iniciar sesión o registrarse.
3. `POST /orders/checkout` valida stock y precios en el servidor, crea un pedido `pending` y una sesión de Stripe Checkout, y devuelve su URL.
4. El navegador va a Stripe. Con una clave de prueba, usa la tarjeta `4242 4242 4242 4242`, cualquier fecha futura y cualquier CVC.
5. Stripe redirige a `/?checkout=success&session_id=...`; el frontend llama a `POST /orders/confirm/{session_id}`, el servidor consulta a Stripe y, si está pagado, marca el pedido como `paid` y descuenta el stock.
6. `POST /orders/webhook` hace lo mismo a partir del evento `checkout.session.completed` (requiere `STRIPE_WEBHOOK_SECRET`; en local, `stripe listen --forward-to localhost:8000/orders/webhook`).

La moneda es EUR (constante `CURRENCY` en `app/routers/orders.py`).

## Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/products/` | No | Lista de productos |
| GET | `/products/{id}` | No | Detalle |
| POST | `/products/` | Sí | Crear producto |
| POST | `/auth/register` | No | Alta de usuario |
| POST | `/auth/login` | No | Formulario OAuth2 (`username` = email); devuelve JWT |
| GET | `/auth/me` | Sí | Usuario actual |
| POST | `/orders/checkout` | Sí | Crea pedido y sesión de Stripe |
| POST | `/orders/confirm/{session_id}` | Sí | Confirma el pago y actualiza el pedido |
| GET | `/orders/` | Sí | Pedidos del usuario |
| POST | `/orders/webhook` | Firma Stripe | Webhook de Stripe |

## Migraciones

```bash
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

La URL de la base de datos se toma de `DATABASE_URL` (`alembic/env.py`).

## Observabilidad

Cada petición recibe un `X-Trace-ID` (o conserva el enviado) y se registra con su duración. `docker-compose.yml` incluye Elasticsearch y Kibana (sin seguridad, solo para desarrollo). `filebeat/filebeat.yml` existe pero Filebeat no está definido en el compose.

## Pendiente

- Pruebas automáticas.
- Roles: ahora cualquier usuario autenticado puede crear productos.
- Pantalla de historial de pedidos en el frontend (el endpoint ya existe).
