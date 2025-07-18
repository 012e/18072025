import os

from pydantic import BaseModel, Field, HttpUrl, ValidationError


class Settings(BaseModel):
    grafana_loki_url: HttpUrl = Field(alias="GRAFANA_LOKI_URL")
    grafana_loki_user: str = Field(alias="GRAFANA_LOKI_USER")
    grafana_loki_password: str = Field(alias="GRAFANA_LOKI_PASSWORD")

    scrape_output_path: str = Field(default="./.tmp", alias="SCRAPE_OUTPUT_PATH")


def load_config() -> Settings:
    config_data = {
        "GRAFANA_LOKI_URL": os.getenv("GRAFANA_LOKI_URL"),
        "GRAFANA_LOKI_USER": os.getenv("GRAFANA_LOKI_USER"),
        "GRAFANA_LOKI_PASSWORD": os.getenv("GRAFANA_LOKI_PASSWORD"),
    }

    try:
        settings = Settings(
            **config_data
        )  # This will raise ValidationError if any field is invalid
        print("Configuration validated successfully with Pydantic.")
        return settings
    except ValidationError as e:
        print("Configuration validation failed with Pydantic errors:")
        print(e.json(indent=2))
        raise
