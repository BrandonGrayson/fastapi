from pydantic import BaseSettings

class Settings(BaseSettings):
    fastapi_database_host: str
    fastapi_database_username: str 
    fastapi_database_password: str 
    fastapi_database_port: str 

    class Config:
        env_file = ".env"



settings = Settings()