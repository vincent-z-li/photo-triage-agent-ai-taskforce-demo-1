from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings


def add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to the FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        # TODO: fix this CORS bugs
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )