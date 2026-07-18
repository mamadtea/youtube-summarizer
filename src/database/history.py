from src.database.sqlite import Database


class History:
    """
    Manage user history.
    """

    def __init__(self):

        self.db = Database()

    # =====================================
    # ADD HISTORY
    # =====================================

    def add(
        self,
        user_id: int,
        video_id: str,
        title: str,
        channel: str
    ):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            INSERT INTO history
            (
                user_id,
                video_id,
                title,
                channel
            )

            VALUES
            (
                ?, ?, ?, ?
            )
            """,
            (
                user_id,
                video_id,
                title,
                channel
            )
        )

        self.db.connection.commit()

    # =====================================
    # GET HISTORY
    # =====================================

    def get_history(
        self,
        user_id: int,
        limit: int = 10
    ):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT
                title,
                channel,
                created_at

            FROM history

            WHERE user_id = ?

            ORDER BY created_at DESC

            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )

        return cursor.fetchall()

    # =====================================
    # CLEAR HISTORY
    # =====================================

    def clear(
        self,
        user_id: int
    ):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            DELETE FROM history

            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )

        self.db.connection.commit()

    # =====================================
    # HISTORY COUNT
    # =====================================

    def count(
        self,
        user_id: int
    ):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)

            FROM history

            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )

        result = cursor.fetchone()

        if result is None:
            return 0

        return result[0]
    # =====================================
# Singleton
# =====================================

_history = History()


def add(
    user_id: int,
    video_id: str,
    title: str,
    channel: str
):
    _history.add(
        user_id,
        video_id,
        title,
        channel
    )


def get_history(
    user_id: int,
    limit: int = 10
):
    return _history.get_history(
        user_id,
        limit
    )


def clear(
    user_id: int
):
    _history.clear(
        user_id
    )


def count(
    user_id: int
):
    return _history.count(
        user_id
    )