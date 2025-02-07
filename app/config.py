from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Tom.Camp"
    mongo_db: str
    mongo_host: str
    mongo_pass: str
    mongo_port: str
    mongo_user: str
    secret_key: str
    hash_algorithm: str
    initial_user_name: str
    initial_user_mail: str
    initial_user_pass: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def mongodb_uri(self):
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_pass}@{self.mongo_host}:{self.mongo_port}/"
            f"{self.mongo_db}?authSource=admin"
        )


settings = Settings()
