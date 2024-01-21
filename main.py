# main.py
from fastapi import FastAPI,HTTPException,Depends
from api.endpoints import router as api_router
app = FastAPI()
app.include_router(api_router)

# Importing the exception handler from endpoints
from api.endpoints import http_exception_handler
app.add_exception_handler(HTTPException, http_exception_handler)
