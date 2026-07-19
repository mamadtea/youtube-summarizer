import json
import time
import logging
from typing import Optional, Dict, Any

import aiosqlite

logger = logging.getLogger("youtube_summarizer")


class SummaryCache:
    def __init__(self, db_path: str = "data/cache.db", expire_seconds: int = 86400):
        self.db_path = db_path
        self.expire_seconds = expire_seconds
        self._db: Optional[aiosqlite.Connection] = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS summary_cache (
                video_id TEXT,
                language TEXT,
                summary_type TEXT,
                summary_json TEXT,
                created_at REAL,
                PRIMARY KEY (video_id, language, summary_type)
            )
        """)
        await self._db.commit()
        logger.info("SQLite Cache database initialized.")

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def get(self, video_id: str, language: str, summary_type: str) -> Optional[Dict[str, Any]]:
        if not self._db:
            await self.init()

        async with self._db.execute(
            "SELECT summary_json, created_at FROM summary_cache WHERE video_id = ? AND language = ? AND summary_type = ?",
            (video_id, language, summary_type)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        summary_json, created_at = row

        if time.time() - created_at > self.expire_seconds:
            await self.delete(video_id, language, summary_type)
            return None

        try:
            return json.loads(summary_json)
        except json.JSONDecodeError:
            await self.delete(video_id, language, summary_type)
            return None

    async def set(self, video_id: str, language: str, summary_type: str, value: Dict[str, Any]) -> None:
        if not self._db:
            await self.init()

        summary_json = json.dumps(value, ensure_ascii=False)
        created_at = time.time()

        await self._db.execute(
            """
            INSERT OR REPLACE INTO summary_cache (video_id, language, summary_type, summary_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (video_id, language, summary_type, summary_json, created_at)
        )
        await self._db.commit()

    async def delete(self, video_id: str, language: str, summary_type: str) -> None:
        if not self._db:
            await self.init()

        await self._db.execute(
            "DELETE FROM summary_cache WHERE video_id = ? AND language = ? AND summary_type = ?",
            (video_id, language, summary_type)
        )
        await self._db.commit()

    async def clear(self) -> None:
        if not self._db:
            await self.init()

        await self._db.execute("DELETE FROM summary_cache")
        await self._db.commit()