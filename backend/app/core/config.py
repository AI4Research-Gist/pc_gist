"""项目配置中心。"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/ 目录作为后端运行根目录。
BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """集中管理应用运行时需要的环境变量。"""

    app_name: str = Field(default="Gist Backend", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=10080, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(
        default="mysql+pymysql://root:1234@127.0.0.1:3306/gist_backend",
    )
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"], alias="ALLOWED_ORIGINS")
    siliconflow_api_key: str | None = Field(default="sk-cgoyljmdamccnilwyayaabeccgqzmocvtwwjbughcgipysky", alias="SILICONFLOW_API_KEY")
    siliconflow_base_url: str = Field(default="https://api.siliconflow.cn/v1", alias="SILICONFLOW_BASE_URL")
    siliconflow_text_model: str = Field(
        default="Qwen/Qwen3.5-397B-A17B",
        alias="SILICONFLOW_TEXT_MODEL",
    )
    siliconflow_vision_model: str = Field(
        default="Pro/moonshotai/Kimi-K2.5",
        alias="SILICONFLOW_VISION_MODEL",
    )
    siliconflow_audio_model: str = Field(
        default="FunAudioLLM/SenseVoiceSmall",
        alias="SILICONFLOW_AUDIO_MODEL",
    )
    siliconflow_request_timeout: int = Field(default=120, alias="SILICONFLOW_REQUEST_TIMEOUT")

    model_config = SettingsConfigDict(
        # 兼容从 backend/ 或仓库根目录启动服务的两种场景。
        env_file=(BASE_DIR / ".env", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # 配置对象只初始化一次，避免重复读取环境变量。
    return Settings()


settings = get_settings()
