import functools
import os

from pydantic import BaseModel, Field, HttpUrl, ValidationError


class Settings(BaseModel):
    grafana_loki_url: HttpUrl = Field(alias="GRAFANA_LOKI_URL")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    scrape_output_path: str = Field(default="./.tmp", alias="SCRAPE_OUTPUT_PATH")


@functools.lru_cache()
def load_config() -> Settings:
    config_data = {
        "GRAFANA_LOKI_URL": os.getenv("GRAFANA_LOKI_URL"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
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
