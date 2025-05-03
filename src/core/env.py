from pathlib import Path

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


# Constants loaded from .env file or just constants
class Settings(BaseSettings):
    PROJECT_NAME: str = 'TEMNOMOR ACCEES TELEGRAM BOT'

    SUBSCRIPTION_PRICE_RUBLES: int = 200

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_ADMIN_ID: int
    TELEGRAM_BOT_ADMIN_USERNAME: str
    TELEGRAM_BOT_URL: AnyHttpUrl

    TELEGRAM_BOT_ADMIN_SECRET: str = secrets.token_hex(16)

    TELEGRAM_LOGGING_BOT_TOKEN: str
    TELEGRAM_LOGGING_CHAT_ID: int | str
    TELEGRAM_LOGGER_FORMAT: str = (
        f'{PROJECT_NAME}\n\n'
        '{level} {time:DD.MM.YYYY HH:mm:ss}\n'
        '{name}:{function}\n\n'
        '{message}'
    )

    X_UI_DOMAIN_BASE_URL: AnyHttpUrl
    X_UI_LOGIN_URL: AnyHttpUrl
    X_UI_API_URL: AnyHttpUrl
    X_UI_SUBSCRIPTION_URL: AnyHttpUrl
    X_UI_INBOUND_ID: int
    X_UI_INBOUND_NAME: str
    X_UI_USERNAME: str
    X_UI_PASSWORD: str

    YOOMONEY_ACCESS_TOKEN: str

    @field_validator(
        'TELEGRAM_BOT_URL',
        'X_UI_DOMAIN_BASE_URL',
        'X_UI_LOGIN_URL',
        'X_UI_API_URL',
        'X_UI_SUBSCRIPTION_URL',
        mode='after',
    )
    @classmethod
    def stringify_all_urls(cls, url: AnyHttpUrl):
        return str(url)

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=Path('../.env')
    )


env = Settings()
