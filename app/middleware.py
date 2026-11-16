import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configurar el logger básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tienda_logger")

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Generar o recuperar el Trace ID (si el cliente ya lo manda en los headers)
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # 2. Medir tiempo de la petición
        start_time = time.time()
        
        # 3. Adjuntar el trace_id al request state por si quieres usarlo en las rutas
        request.state.trace_id = trace_id
        
        logger.info(f"[TraceID: {trace_id}] Inicia petición: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 4. Añadir el Trace ID a los headers de la respuesta HTTP
            response.headers["X-Trace-ID"] = trace_id
            
            logger.info(f"[TraceID: {trace_id}] Petición completada con status {response.status_code} en {process_time:.4f}s")
            return response
            
        except Exception as e:
            logger.error(f"[TraceID: {trace_id}] Error crítico en la petición: {str(e)}")
            raise e