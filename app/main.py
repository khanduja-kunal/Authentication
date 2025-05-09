import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.auth import endpoints as auth_endpoints
from app.api.v1.user import endpoints as user_endpoints

app = FastAPI()

# Ensure the directory exists
os.makedirs("profile_pictures", exist_ok=True)

# Mount static file route
app.mount("/profile_pictures", StaticFiles(directory="profile_pictures"), name="profile_pictures")

app.include_router(auth_endpoints.router, tags=["Auth"])
app.include_router(user_endpoints.router, tags=["Users"])
