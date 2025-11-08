"""
Configuration management for Lineage Lens
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    anthropic_api_key: Optional[str] = Field(None, env='ANTHROPIC_API_KEY')
    anthropic_base_url: Optional[str] = Field(None, env='ANTHROPIC_BASE_URL')
    claude_model: Optional[str] = Field('claude-3-haiku-20240307', env='CLAUDE_MODEL')
    claude_temperature: Optional[float] = Field(0.7, env='CLAUDE_TEMPERATURE')
    
    # Application Configuration  
    app_title: str = Field("Lineage Lens", env='APP_TITLE')
    app_description: str = Field("Intelligent Data Lineage Analysis Platform", env='APP_DESCRIPTION')
    debug_mode: bool = Field(False, env='DEBUG_MODE')
    
    # Streamlit Configuration
    page_title: str = "🔍 Lineage Lens"
    page_icon: str = "🔍"
    layout: str = "wide"
    
    # File Upload Configuration
    max_file_size: int = Field(10, description="Max file size in MB")  # 10MB
    allowed_extensions: list = Field(default_factory=lambda: ['.sql', '.txt'])
    
    # Visualization Configuration
    default_layout: str = "spring"
    max_nodes_display: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
