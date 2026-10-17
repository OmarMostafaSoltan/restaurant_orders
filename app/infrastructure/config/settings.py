from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    default_restaurant_id:  str = "r1"
    api_key: str = "change-me"



settings = Settings()