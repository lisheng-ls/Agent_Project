from dataclasses import dataclass
from typing import Any


@dataclass
class ColumnInfo:
    id :str
    name :str | None
    type :str | None
    type: str  | None
    role :str | None
    examples :list[Any]
    description :str | None
    alias :list[str]
    table_id :str | None

