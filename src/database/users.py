import logging
from typing import Dict, Any, Optional

import aiosqlite

logger = logging.getLogger("youtube_summarizer")

DB_PATH = "data/bot.db"


class UserSettings:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT DEFAULT '',
                language TEXT DEFAULT 'Persian',
                summary_type TEXT DEFAULT 'detailed',
                requests INTEGER DEFAULT 0
            )
        """)
        await self._db.commit()
        logger.info("User database initialized.")

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def create_user(self, user_id: int, first_name: str = "") -> None:
        await self._db.execute(
            "INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)",
            (user_id, first_name)
        )
        await self._db.commit()

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        async with self._db.execute(
            "SELECT language, summary_type, requests FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()

        if result is None:
            await self.create_user(user_id)
            return {
                "language": "Persian",
                "summary_type": "detailed",
                "requests": 0
            }

        return {
            "language": result[0],
            "summary_type": result[1],
            "requests": result[2]
        }

    async def update_language(self, user_id: int, language: str) -> None:
        await self.create_user(user_id)
        await self._db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        await self._db.commit()

    async def update_summary_type(self, user_id: int, summary_type: str) -> None:
        await self.create_user(user_id)
        await self._db.execute(
            "UPDATE users SET summary_type = ? WHERE user_id = ?",
            (summary_type, user_id)
        )
        await self._db.commit()

    async def increase_requests(self, user_id: int) -> None:
        await self.create_user(user_id)
        await self._db.execute(
            "UPDATE users SET requests = requests + 1 WHERE user_id = ?",
            (user_id,)
        )
        await self._db.commit()

    async def create_if_not_exists(self, user_id: int, first_name: str = "") -> None:
        await self.create_user(user_id, first_name)

    async def set_language(self, user_id: int, language: str) -> None:
        await self.update_language(user_id, language)

    async def set_summary_type(self, user_id: int, summary_type: str) -> None:
        await self.update_summary_type(user_id, summary_type)


_users = UserSettings()

async def init() -> None:
    await _users.init()
    
async def create_if_not_exists(user_id: int, first_name: str = "") -> None:
    await _users.create_if_not_exists(user_id, first_name)

async def get_user(user_id: int) -> Dict[str, Any]:
    return await _users.get_user(user_id)

async def increase_requests(user_id: int) -> None:
    await _users.increase_requests(user_id)

async def set_language(user_id: int, language: str) -> None:
    await _users.set_language(user_id, language)

async def set_summary_type(user_id: int, summary_type: str) -> None:
    await _users.set_summary_type(user_id, summary_type)