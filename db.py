from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from typing import TypedDict


class User(TypedDict):
    user_id: int


class DataBase:
    def __init__(self, db_uri: str, db_name: str) -> None:
        self._client: AsyncMongoClient[User] = AsyncMongoClient(
            host = db_uri,
            serverSelectionTimeoutMS = 2000
        )

        self._users: AsyncCollection[User] = self._client.get_database(db_name).get_collection("users")

    async def add_user(self, user_id: int) -> None:
        await self._users.update_one(
            filter = {"user_id": user_id},
            update = {"$setOnInsert": {"user_id": user_id}},
            upsert = True
        )
