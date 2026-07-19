import logging
from typing import List, Tuple, Optional

import aiosqlite

logger = logging.getLogger("youtube_summarizer")

DB_PATH = "data/bot.db"


class History:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_id TEXT,
                title TEXT,
                channel TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.commit()
        logger.info("History database initialized.")

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def add(self, user_id: int, video_id: str, title: str, channel: str) -> None:
        await self._db.execute(
            "INSERT INTO history (user_id, video_id, title, channel) VALUES (?, ?, ?, ?)",
            (user_id, video_id, title, channel)
        )
        await self._db.commit()

    async def get_history(self, user_id: int, limit: int = 10) -> List[Tuple]:
        async with self._db.execute(
            "SELECT title, channel, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            return await cursor.fetchall()

    async def clear(self, user_id: int) -> None:
        await self._db.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
        await self._db.commit()

    async def count(self, user_id: int) -> int:
        async with self._db.execute(
            "SELECT COUNT(*) FROM history WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


_history = History()

async def init() -> None:
    await _history.init()

async def add(user_id: int, video_id: str, title: str, channel: str) -> None:
    await _history.add(user_id, video_id, title, channel)

async def get_history(user_id: int, limit: int = 10) -> List[Tuple]:
    return await _history.get_history(user_id, limit)

async def clear(user_id: int) -> None:
    await _history.clear(user_id)

async def count(user_id: int) -> int:
    return await _history.count(user_id)