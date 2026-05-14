from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

client: AsyncIOMotorClient | None = None
memory_db: "InMemoryDatabase" | None = None


@dataclass
class InsertOneResult:
    inserted_id: str


class InMemoryCursor:
    def __init__(self, documents: list[dict[str, Any]]):
        self._documents = documents
        self._index = 0

    def sort(self, key: str, direction: int):
        reverse = direction == -1
        self._documents.sort(key=lambda item: item.get(key, datetime.min), reverse=reverse)
        return self

    def limit(self, count: int):
        self._documents = self._documents[:count]
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._documents):
            raise StopAsyncIteration
        document = self._documents[self._index]
        self._index += 1
        return document


class InMemoryCollection:
    def __init__(self):
        self._documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]):
        for document in self._documents:
            if all(str(document.get(key)) == str(value) for key, value in query.items()):
                return document
        return None

    async def insert_one(self, document: dict[str, Any]):
        stored = dict(document)
        stored.setdefault("_id", str(uuid4()))
        self._documents.append(stored)
        return InsertOneResult(inserted_id=str(stored["_id"]))

    def find(self, query: dict[str, Any]):
        documents = [
            document
            for document in self._documents
            if all(str(document.get(key)) == str(value) for key, value in query.items())
        ]
        return InMemoryCursor(documents)


@dataclass
class InMemoryDatabase:
    users: InMemoryCollection = field(default_factory=InMemoryCollection)
    predictions: InMemoryCollection = field(default_factory=InMemoryCollection)
    reports: InMemoryCollection = field(default_factory=InMemoryCollection)


async def connect_to_mongo() -> None:
    global client, memory_db
    settings = get_settings()
    memory_db = InMemoryDatabase()
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        await client.admin.command("ping")
    except Exception:
        client = None


async def close_mongo_connection() -> None:
    global client
    if client is not None:
        client.close()
        client = None


def get_database() -> AsyncIOMotorDatabase:
    if client is not None:
        settings = get_settings()
        return client[settings.mongodb_db]
    if memory_db is None:
        raise RuntimeError("Database has not been initialized")
    return memory_db


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield get_database()
