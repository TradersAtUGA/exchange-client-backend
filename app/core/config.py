from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #Database
    DATABASE_URL: str

    #App
    DEBUG: bool = False
    PROJECT_NAME: str = "Exchange Client Backend"
    API_PREFIX: str = "/api"

    #Auth / JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MIN: int = 30


    class Config:
        env_file = ".env"

#Create a single settings object you can import anywhere
settings = Settings()
