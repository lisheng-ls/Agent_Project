from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf


@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str

@dataclass
class Console:
    enable: bool
    level: str

@dataclass
class LoggingConfig:
    file:File
    console:Console

@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


@dataclass
class EsConfig:
    host: str
    port: int
    index_name: str

@dataclass
class LlmConfig:
    model_name: str
    api_key: str
    base_url: str

@dataclass
class AppConfig:
    logging:LoggingConfig
    db_meta:DbConfig
    db_dw:DbConfig
    qdrant:QdrantConfig
    embedding:EmbeddingConfig
    es:EsConfig
    llm:LlmConfig


def load_app_config():
    #__file__获取当前文件的绝对路径
    #Path(__file__).parent：获取当前文件的上一级目录的绝对路径
    #Path(__file__).parents[n]: 获取当前文件的上n级目录的绝对路径

    #获取yaml文件的路径
    config_path = Path(__file__).parents[2]/'conf'/'app_config.yaml'

    #读取yaml文件内容
    content = OmegaConf.load(config_path)

    #构造配置文件结构，按照AppConfig结构构造
    schema = OmegaConf.structured(AppConfig)

    # 合并结构+内容
    merge_config = OmegaConf.merge(schema,content)

    # 转换为AppConfig的对象
    app_config: AppConfig = OmegaConf.to_object(merge_config)

    return app_config

