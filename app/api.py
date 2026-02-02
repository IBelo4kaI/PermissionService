from fastapi import FastAPI

from app.database import init_db
from app.routes import main_router

init_db()
app = FastAPI(title="PermissionServiceAndAuth", debug=True)
app.include_router(main_router)
