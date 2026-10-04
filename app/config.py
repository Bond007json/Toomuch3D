from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TOOMUCH3D_", extra="ignore")
    hi3d_root: Path = Path("/opt/Hi3D-Official")
    first_stage_checkpoint: Path = Path("/opt/Hi3D-Official/ckpts/first_stage.pt")
    second_stage_checkpoint: Path = Path("/opt/Hi3D-Official/ckpts/second_stage.pt")
    cuda_device: int = 0
    data_dir: Path = Path("./data")

settings = Settings()
