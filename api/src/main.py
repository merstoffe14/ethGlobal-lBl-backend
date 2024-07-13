from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import logic_routes, control_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logic_routes.router, prefix='/logic', tags=["logic"])
app.include_router(control_routes.router, prefix='/control', tags=["control"])


