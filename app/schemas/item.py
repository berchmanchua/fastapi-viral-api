from typing import List, Optional
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., max_length=100, examples=["Sub-millisecond FastAPI Setup"])
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        examples=["High-throughput Python API backed by asyncpg and Valkey"],
    )
    platform: str = Field(..., max_length=50, examples=["youtube"])
    viral_score: float = Field(default=0.0, ge=0.0)
    tags: List[str] = Field(default_factory=list, examples=[["python", "fastapi", "valkey"]])


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    platform: Optional[str] = Field(default=None, max_length=50)
    viral_score: Optional[float] = Field(default=None, ge=0.0)
    tags: Optional[List[str]] = None


class Item(ItemCreate):
    id: int
