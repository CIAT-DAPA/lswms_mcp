from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        # env_prefix="lswms_",
        case_sensitive=False,
        )
    api_base_url:str = "https://webapi.waterpointsmonitoring.net/api/v1/"

    client_id: str | None = None
    client_secret: str | None = None
    
    #mcp parameters for a server to call
    server_name: str = "waterpoint"
    log_level:str = "INFO"
    mcp_transport: str
    mcp_host: str
    mcp_port: int


settings = Settings()

    



    