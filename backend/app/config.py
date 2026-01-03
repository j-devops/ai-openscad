"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    APP_NAME: str = "AI-OpenSCAD"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # OpenAI Configuration
    OPENAI_API_KEY: str

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # Data paths
    DATA_PATH: str = "./data"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost"

    # Rendering
    MAX_CODE_SIZE: int = 100000  # 100KB
    RENDER_TIMEOUT: int = 120  # seconds

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
