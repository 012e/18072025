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
    previous_page: Optional[str] = None
    next_page: Optional[str] = None
    per_page: int
    page_count: int
    count: int
    sort_by: str
    sort_order: str


class Section(BaseModel):
    id: int
    url: str
    html_url: str
    category_id: int
    position: int
    sorting: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: str
    locale: str
    source_locale: str
    outdated: bool
    parent_section_id: Optional[int] = None
    theme_template: str


class SectionsResponse(BaseModel):
    sections: list[Section]
    page: int
    previous_page: Optional[str] = None
    next_page: Optional[str] = None
    per_page: int
    page_count: int
    count: int
    sort_by: str
    sort_order: str


class Article(BaseModel):
    id: int
    url: str
    html_url: str
    author_id: int
    comments_disabled: bool
    draft: bool
    promoted: bool
    position: int
    vote_sum: int
    vote_count: int
    section_id: int
    created_at: datetime
    updated_at: datetime
    name: str
    title: str
    source_locale: str
    locale: str
    outdated: bool
    outdated_locales: list[str]
    edited_at: datetime
    user_segment_id: Optional[int] = None
    permission_group_id: int
    content_tag_ids: list[str]
    label_names: list[str]
    body: str

    file_path: Optional[str] = None
    openai_file_id: Optional[str] = None


class ArticlesResponse(BaseModel):
    articles: list[Article]
    page: int
    previous_page: Optional[str] = None
    next_page: Optional[str] = None
    per_page: int
    page_count: int
    count: int
    sort_by: str
    sort_order: str
