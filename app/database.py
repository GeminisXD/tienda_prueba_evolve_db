from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión usando tus credenciales exactas
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://tiendadb:tiendadb@localhost:5432/tiendadb"

# Motor de SQLAlchemy para PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos (MVC)
Base = declarative_base()

# Dependencia para obtener la sesión de BD en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()