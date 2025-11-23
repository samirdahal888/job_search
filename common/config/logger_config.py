from common.config.base_config import BaseConfig
from pydantic import Field, field_validator


class loggerConfig(BaseConfig):
    # Logging settings (shared across all modules)
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging Level")
    LOG_TO_FILE: bool = Field(default=False, description="Enable file logging")
    LOG_TO_CONSOLE: bool = Field(default=True, description="Enable console logging")

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper
