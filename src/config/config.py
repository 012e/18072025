import functools
import os

from pydantic import BaseModel, Field, HttpUrl, ValidationError


class Settings(BaseModel):
    grafana_loki_url: HttpUrl = Field(alias="GRAFANA_LOKI_URL")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    scrape_output_path: str = Field(default="./.tmp", alias="SCRAPE_OUTPUT_PATH")
    redis_host : str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")
    redis_password: str = Field(alias="REDIS_PASSWORD")


@functools.lru_cache()
def load_config() -> Settings:
    config_data = {
        "GRAFANA_LOKI_URL": os.getenv("GRAFANA_LOKI_URL"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD"),
    }
    
    # Add SCRAPE_OUTPUT_PATH only if it's set (to allow default to be used)
    scrape_output_path = os.getenv("SCRAPE_OUTPUT_PATH")
    if scrape_output_path is not None:
        config_data["SCRAPE_OUTPUT_PATH"] = scrape_output_path
    try:
        settings = Settings(
            **config_data # type: ignore
        )  # This will raise ValidationError if any field is invalid
        print("Configuration validated successfully with Pydantic.")
        return settings
    except ValidationError as e:
        print("Configuration validation failed with Pydantic errors:")
        print(e.json(indent=2))
        raise
