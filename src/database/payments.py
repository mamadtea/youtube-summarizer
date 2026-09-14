
import os
import typing
from datetime import datetime, timezone

import aiosqlite

DB_PATH = "data/bot.db"


PAYMENT_STATUSES = {
    "PENDING",
    "PAID",
    "REJECTED",
    "CANCELED",
}


class PaymentManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        os.makedirs(
            os.path.dirname(self.db_path),
            exist_ok=True,
        )

        self._db = await aiosqlite.connect(
            self.db_path
        )

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan TEXT NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                receipt_file_id TEXT,
                created_at TEXT NOT NULL,
                reviewed_at TEXT
            )
            """
        )

        await self._db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_user
            ON payments (user_id)
            """
        )

        await self._db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_status
            ON payments (status)
            """
        )

        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def create_payment(
        self,
        user_id: int,
        plan: str,
        amount: int,
    ) -> dict[str, typing.Any]:

        plan = plan.lower().strip()

        if amount <= 0:
            raise ValueError(
                "Payment amount must be greater than zero"
            )

        now = datetime.now(
            timezone.utc
        ).isoformat()

        cursor = await self._db.execute(
            """
            INSERT INTO payments (
                user_id,
                plan,
                amount,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'PENDING', ?)
            """,
            (
                user_id,
                plan,
                amount,
                now,
            ),
        )

        await self._db.commit()

        return {
            "id": cursor.lastrowid,
            "user_id": user_id,
            "plan": plan,
            "amount": amount,
            "status": "PENDING",
            "receipt_file_id": None,
            "created_at": now,
            "reviewed_at": None,
        }

    async def attach_receipt(
        self,
        payment_id: int,
        receipt_file_id: str,
    ) -> bool:

        cursor = await self._db.execute(
            """
            UPDATE payments
            SET receipt_file_id = ?
            WHERE id = ?
              AND status = 'PENDING'
            """,
            (
                receipt_file_id,
                payment_id,
            ),
        )

        await self._db.commit()

        return cursor.rowcount == 1

    async def get_payment(
        self,
        payment_id: int,
    ) -> dict[str, typing.Any] | None:

        async with self._db.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                amount,
                status,
                receipt_file_id,
                created_at,
                reviewed_at
            FROM payments
            WHERE id = ?
            """,
            (payment_id,),
        ) as cursor:

            row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    async def get_pending_payments(
        self,
    ) -> list[dict[str, typing.Any]]:

        async with self._db.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                amount,
                status,
                receipt_file_id,
                created_at,
                reviewed_at
            FROM payments
            WHERE status = 'PENDING'
            ORDER BY id ASC
            """
        ) as cursor:

            rows = await cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    async def get_latest_pending_payment(
        self,
        user_id: int,
    ) -> dict[str, typing.Any] | None:
        """
        Return the latest pending payment for a user.
        """

        async with self._db.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                amount,
                status,
                receipt_file_id,
                created_at,
                reviewed_at
            FROM payments
            WHERE user_id = ?
              AND status = 'PENDING'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ) as cursor:

            row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    async def update_status(
        self,
        payment_id: int,
        status: str,
    ) -> bool:

        status = status.upper().strip()

        if status not in PAYMENT_STATUSES:
            raise ValueError(
                f"Invalid payment status: {status}"
            )

        reviewed_at = None

        if status in {
            "PAID",
            "REJECTED",
            "CANCELED",
        }:
            reviewed_at = datetime.now(
                timezone.utc
            ).isoformat()

        cursor = await self._db.execute(
            """
            UPDATE payments
            SET
                status = ?,
                reviewed_at = ?
            WHERE id = ?
              AND status = 'PENDING'
            """,
            (
                status,
                reviewed_at,
                payment_id,
            ),
        )

        await self._db.commit()

        return cursor.rowcount == 1

    async def get_user_payments(
        self,
        user_id: int,
    ) -> list[dict[str, typing.Any]]:

        async with self._db.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                amount,
                status,
                receipt_file_id,
                created_at,
                reviewed_at
            FROM payments
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ) as cursor:

            rows = await cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    @staticmethod
    def _row_to_dict(
        row: tuple,
    ) -> dict[str, typing.Any]:

        return {
            "id": row[0],
            "user_id": row[1],
            "plan": row[2],
            "amount": row[3],
            "status": row[4],
            "receipt_file_id": row[5],
            "created_at": row[6],
            "reviewed_at": row[7],
        }


payments = PaymentManager()


async def init() -> None:
    await payments.init()


async def close() -> None:
    await payments.close()


async def create_payment(
    user_id: int,
    plan: str,
    amount: int,
) -> dict[str, typing.Any]:

    return await payments.create_payment(
        user_id,
        plan,
        amount,
    )


async def attach_receipt(
    payment_id: int,
    receipt_file_id: str,
) -> bool:

    return await payments.attach_receipt(
        payment_id,
        receipt_file_id,
    )


async def get_payment(
    payment_id: int,
) -> dict[str, typing.Any] | None:

    return await payments.get_payment(
        payment_id,
    )


async def get_pending_payments() -> list[dict[str, typing.Any]]:

    return await payments.get_pending_payments()


async def get_latest_pending_payment(
    user_id: int,
) -> dict[str, typing.Any] | None:

    return await payments.get_latest_pending_payment(
        user_id
    )


async def update_status(
    payment_id: int,
    status: str,
) -> bool:

    return await payments.update_status(
        payment_id,
        status,
    )


async def get_user_payments(
    user_id: int,
) -> list[dict[str, typing.Any]]:

    return await payments.get_user_payments(
        user_id,
    )
