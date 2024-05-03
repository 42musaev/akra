from contextlib import asynccontextmanager
from functools import partial
from typing import Dict

import strawberry
from strawberry.types import Info
from fastapi import FastAPI
from strawberry.fastapi import BaseContext, GraphQLRouter
from databases import Database

from settings import settings, CONN_TEMPLATE


class Context(BaseContext):
    def __init__(
            self,
            db: Database,
    ) -> None:
        self.db = db


@strawberry.type
class Author:
    name: str


@strawberry.type
class Book:
    title: str
    author: Author


@strawberry.type
class Query:

    @strawberry.field
    async def books(
            self,
            info: Info[Context, None],
            author_ids: list[int] | None = None,
            search: str | None = None,
            limit: int | None = None,
    ) -> list[Book]:
        where_conditions = []
        params: Dict = {}

        if author_ids:
            where_conditions.append("author_id = ANY(:author_ids)")
            params |= {"author_ids": author_ids}

        if search:
            where_conditions.append("title ILIKE :search")
            params |= {"search": search}

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        limit_clause = ""
        if limit:
            limit_clause = "LIMIT :limit"
            params |= {"limit": limit}

        sql = f"""
            SELECT b.title as title, a.name as author_name
            FROM books b
            JOIN authors a ON b.author_id = a.id
            {where_clause}
            {limit_clause}
        """
        rows = await info.context.db.fetch_all(sql, params)
        return [Book(title=row['title'], author=Author(name=row['author_name'])) for row in rows]


db = Database(
    CONN_TEMPLATE.format(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        port=settings.DB_PORT,
        host=settings.DB_SERVER,
        name=settings.DB_NAME,
    ),
)


@asynccontextmanager
async def lifespan(
        app: FastAPI,
        db: Database,
):
    async with db:
        yield
    await db.disconnect()


schema = strawberry.Schema(query=Query)
graphql_app: GraphQLRouter = GraphQLRouter(
    schema,
    context_getter=partial(Context, db),
)

app = FastAPI(lifespan=partial(lifespan, db=db))
app.include_router(graphql_app, prefix="/graphql")
