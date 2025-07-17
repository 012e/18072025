from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Category(BaseModel):
    id: int
    url: str
    html_url: str
    position: int
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
    locale: str
    source_locale: str
    outdated: bool


class CategoriesResponse(BaseModel):
    categories: list[Category]
    page: int
    previous_page: Optional[int] = None
    next_page: Optional[int] = None
    per_page: int
    page_count: int
    count: int
    sort_by: str
    sort_order: str
