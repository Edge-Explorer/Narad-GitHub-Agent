from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    """
    Industry-grade configuration management using Pydantic.
    Handles environment variables, validation, and secret masking.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core API Keys
    github_token: str = Field(..., alias="GITHUB_TOKEN")
    gemini_api_key: SecretStr = Field(..., alias="GEMINI_API_KEY")

    # App Settings
    app_name: str = "Narad-GitHub-Agent"
    log_level: str = "INFO"
    gemini_model: str = "gemini-2.0-flash-exp"

    # GitHub Settings
    github_base_url: str = "https://api.github.com"
    default_commit_limit: int = 5

settings = Settings()
