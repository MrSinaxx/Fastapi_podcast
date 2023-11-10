PODCASTLIST_ENDPOINT = "http://127.0.0.1:8000/api/podcasts/"
EPISODELIST_ENDPOINT = "http://127.0.0.1:8000/episode/episodes/"

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=".env", env_file_encoding="utf-8", extra="ignore"
    # )
    ACCOUNT_ENDPOINT: str = "http://127.0.0.1:8001"
    CREATE_OTP_ENDPOINT: str = "http://127.0.0.1:8004/create_otp"
    VERIFY_OTP_ENDPOINT: str = "http://127.0.0.1:8004/verify_otp"

    JWT_SECRET_KEY: str = (
        "693364d5ccaf48dd5ad582fef7bd190591401694551819386b62ee9bd41ccf01"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    PODCASTLIST_ENDPOINT: str = "http://127.0.0.1:8000/api/podcasts/"
    EPISODELIST_ENDPOINT: str = "http://127.0.0.1:8000/episode/episodes/"

    class Config:
        env_file = ".env"


settings = Settings()
