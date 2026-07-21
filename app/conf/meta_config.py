from dataclasses import dataclass
from typing import Optional




@dataclass
class Columns:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool

@dataclass
class Tables:
    name: str
    role: str
    description: str
    columns: list[Columns]

@dataclass
class Metrics:
    name: str
    description: str
    relevant_columns:list[str]
    alias: list[str]

@dataclass
class MetaConfig:
    tables: Optional[list[Tables]] = None
    metrics: Optional[list[Metrics]] = None