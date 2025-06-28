import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="test12345", env="NEO4J_PASSWORD")
    
    # Anthropic Configuration
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # API Configuration
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    
    # Model Configuration
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME")
    anthropic_model: str = Field(default="claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    
    # Search Configuration
    similarity_threshold: float = Field(default=0.1, env="SIMILARITY_THRESHOLD")
    max_tokens: int = Field(default=300, env="MAX_TOKENS")
    temperature: float = Field(default=0.3, env="TEMPERATURE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    return Settings()