from pymongo import MongoClient, errors
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult

from typing import Optional, Union, Dict


class DataBase:
    def __init__(self, db_uri: str, db_name: str) -> None:
        try:
            self._client: MongoClient = MongoClient(
                host = db_uri,
                connect = False,
                serverSelectionTimeoutMS = 2000
            )

        except errors.ConnectionFailure:
            raise Exception("Can`t connect to server!")

        self._db: Database = self._client.get_database(db_name)
        self._users: Collection = self._db.get_collection("users")

    def add_user(self, user_id: int) -> str:
        return self._users.insert_one({
            "user_id": user_id
        }).inserted_id

    def get_user(self, user_id: Optional[int]=None) -> Union[Cursor, Dict]:
        if user_id:
            return self._users.find_one({
                "user_id": user_id
            })

        return self._users.find({})

    def get_users_count(self) -> int:
        return self._users.count_documents({})

    def edit_user(self, user_id: int, data: dict) -> int:
        return self._users.update_one(
            {"user_id": user_id},
            {"$set": data}
        ).modified_count

    def delete_user(self, user_id: Optional[int]=None) -> int:
        if user_id:
            result: DeleteResult = self._users.delete_one({
                "user_id": user_id
            })

        else:
            result: DeleteResult = self._users.delete_many({})

        return result.deleted_count

    def close(self) -> None:
        self._client.close()
