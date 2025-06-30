from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Server Configuration
    agent_server_host: str = "localhost"
    agent_server_port: int = 8001
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8002
    mcp_server_name: str = "photo-triage-mcp"
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = True
    langchain_project: str = "photo-triage-agent"
    langchain_endpoint: str = "https://api.smith.langchain.com"
    
    # Image Processing Configuration
    max_image_size_mb: int = 10
    supported_image_formats: str = "jpg,jpeg,png,bmp,tiff"
    image_quality_threshold: float = 0.7
    
    # LangGraph Configuration
    max_retry_attempts: int = 3
    reflection_enabled: bool = True
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    cors_origins: str = '["http://localhost:3000","http://localhost:8080","http://localhost:5173"]'
    
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Development
    debug: bool = False
    testing: bool = False
    environment: str = "development"
    
    # FastAPI Configuration
    title: str = "Photo Triage Agent API"
    description: str = "ReAct Agent with LangGraph for photo triage and quality analysis"
    version: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def supported_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.supported_image_formats.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        import json
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, ValueError):
            return ["http://localhost:3000"]
    
    
    def setup_langsmith(self) -> None:
        """Configure LangSmith environment variables"""
        if self.langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
        os.environ["LANGCHAIN_TRACING_V2"] = str(self.langchain_tracing_v2).lower()
        os.environ["LANGCHAIN_PROJECT"] = self.langchain_project
        os.environ["LANGCHAIN_ENDPOINT"] = self.langchain_endpoint


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()