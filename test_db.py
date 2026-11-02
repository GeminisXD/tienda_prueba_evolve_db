from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        for row in result:
            print(" ¡Conexión exitosa a PostgreSQL!")
            print(f" Versión de la Base de Datos: {row[0]}")
except Exception as e:
    print(f" Error al conectar a la base de datos: {e}")