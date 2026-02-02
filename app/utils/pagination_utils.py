from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class Page(Generic[T]):
    def __init__(
        self,
        items: list[T],
        total: int,
        page: int,
        limit: int,
    ):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit
        self.pages = (total + limit - 1) // limit


def paginate(query: Query, page: int, limit: int) -> Page:
    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    offset = (page - 1) * limit
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return Page(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )
