import os
import typing
from datetime import datetime, timedelta, timezone

import aiosqlite

DB_PATH = "data/bot.db"

PLANS = {
    "basic": {
        "name": "Basic",
        "credits": 30,
    },
    "pro": {
        "name": "Pro",
        "credits": 100,
    },
    "premium": {
        "name": "Premium",
        "credits": 300,
    },
}


class SubscriptionManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._db = await aiosqlite.connect(self.db_path)

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan TEXT NOT NULL,
                credits_total INTEGER NOT NULL,
                credits_remaining INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE'
            )
            """
        )

        await self._db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status
            ON subscriptions (user_id, status)
            """
        )

        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def activate(
        self,
        user_id: int,
        plan: str,
    ) -> dict[str, typing.Any]:

        plan = plan.lower().strip()

        if plan not in PLANS:
            raise ValueError(
                f"Unknown subscription plan: {plan}"
            )

        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(days=30)

        credits = PLANS[plan]["credits"]

        # Expire previous active subscription
        await self._db.execute(
            """
            UPDATE subscriptions
            SET status = 'EXPIRED'
            WHERE user_id = ?
              AND status = 'ACTIVE'
            """,
            (user_id,),
        )

        cursor = await self._db.execute(
            """
            INSERT INTO subscriptions (
                user_id,
                plan,
                credits_total,
                credits_remaining,
                started_at,
                expires_at,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
            """,
            (
                user_id,
                plan,
                credits,
                credits,
                now.isoformat(),
                expires_at.isoformat(),
            ),
        )

        subscription_id = cursor.lastrowid

        await self._db.commit()

        return {
            "id": subscription_id,
            "user_id": user_id,
            "plan": plan,
            "credits_total": credits,
            "credits_remaining": credits,
            "started_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "status": "ACTIVE",
        }

    async def get_active(
        self,
        user_id: int,
    ) -> dict[str, typing.Any] | None:

        async with self._db.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                credits_total,
                credits_remaining,
                started_at,
                expires_at,
                status
            FROM subscriptions
            WHERE user_id = ?
              AND status = 'ACTIVE'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ) as cursor:

            row = await cursor.fetchone()

        if row is None:
            return None

        subscription = self._row_to_dict(row)

        expires_at = datetime.fromisoformat(
            subscription["expires_at"]
        )

        # Subscription expired
        if expires_at <= datetime.now(timezone.utc):

            await self._db.execute(
                """
                UPDATE subscriptions
                SET status = 'EXPIRED'
                WHERE id = ?
                """,
                (subscription["id"],),
            )

            await self._db.commit()

            return None

        return subscription

    async def has_credit(
        self,
        user_id: int,
    ) -> bool:

        subscription = await self.get_active(user_id)

        return bool(
            subscription
            and subscription["credits_remaining"] > 0
        )

    async def consume_credit(
        self,
        user_id: int,
    ) -> bool:

        subscription = await self.get_active(user_id)

        if (
            subscription is None
            or subscription["credits_remaining"] <= 0
        ):
            return False

        cursor = await self._db.execute(
            """
            UPDATE subscriptions
            SET credits_remaining = credits_remaining - 1
            WHERE id = ?
              AND status = 'ACTIVE'
              AND credits_remaining > 0
            """,
            (subscription["id"],),
        )

        await self._db.commit()

        return cursor.rowcount == 1

    @staticmethod
    def _row_to_dict(
        row: tuple,
    ) -> dict[str, typing.Any]:

        return {
            "id": row[0],
            "user_id": row[1],
            "plan": row[2],
            "credits_total": row[3],
            "credits_remaining": row[4],
            "started_at": row[5],
            "expires_at": row[6],
            "status": row[7],
        }


subscriptions = SubscriptionManager()


async def init() -> None:
    await subscriptions.init()


async def close() -> None:
    await subscriptions.close()


async def activate(
    user_id: int,
    plan: str,
) -> dict[str, typing.Any]:

    return await subscriptions.activate(
        user_id,
        plan,
    )


async def get_active(
    user_id: int,
) -> dict[str, typing.Any] | None:

    return await subscriptions.get_active(
        user_id,
    )


async def consume_credit(
    user_id: int,
) -> bool:

    return await subscriptions.consume_credit(
        user_id,
    )


async def has_credit(
    user_id: int,
) -> bool:

    return await subscriptions.has_credit(
        user_id,
    )