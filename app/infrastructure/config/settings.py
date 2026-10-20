from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    default_restaurant_id:  str = "r1"
    api_key: str = "change-me"
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""   # أي نص تختاره بنفسك، بتكتبه في لوحة Meta
    whatsapp_app_secret: str = ""     # من إعدادات التطبيق في Meta
    whatsapp_api_version: str = "v25.0"



settings = Settings()