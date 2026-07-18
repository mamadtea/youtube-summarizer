from src.database.sqlite import Database


class UserSettings:
    """
    Manage Telegram user settings.
    """

    def __init__(self):
        self.db = Database()

    # =====================================
    # CREATE USER
    # =====================================

    def create_user(
        self,
        user_id: int
    ):

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (
                user_id
            )
            VALUES
            (?)
            """,
            (
                user_id,
            )
        )

        self.db.connection.commit()

    # =====================================
    # GET USER
    # =====================================

    def get_user(
        self,
        user_id: int
    ):

        self.create_user(
            user_id
        )

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT
                language,
                summary_type,
                requests

            FROM users

            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )

        result = cursor.fetchone()

        if result is None:

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

    # =====================================
    # UPDATE LANGUAGE
    # =====================================

    def update_language(
        self,
        user_id: int,
        language: str
    ):

        self.create_user(
            user_id
        )

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            UPDATE users

            SET language = ?

            WHERE user_id = ?
            """,
            (
                language,
                user_id
            )
        )

        self.db.connection.commit()

    # =====================================
    # UPDATE SUMMARY TYPE
    # =====================================

    def update_summary_type(
        self,
        user_id: int,
        summary_type: str
    ):

        self.create_user(
            user_id
        )

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            UPDATE users

            SET summary_type = ?

            WHERE user_id = ?
            """,
            (
                summary_type,
                user_id
            )
        )

        self.db.connection.commit()

    # =====================================
    # INCREASE REQUESTS
    # =====================================

    def increase_requests(
        self,
        user_id: int
    ):

        self.create_user(
            user_id
        )

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            UPDATE users

            SET requests = requests + 1

            WHERE user_id = ?
            """,
            (
                user_id,
            )
        )

        self.db.connection.commit()

    # =====================================
    # GET REQUESTS
    # =====================================

    def get_requests(
        self,
        user_id: int
    ):

        self.create_user(
            user_id
        )

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            SELECT requests

            FROM users

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

_users = UserSettings()


def create_if_not_exists(
    user_id: int,
    first_name: str = ""
):
    _users.create_user(user_id)


def get_user(
    user_id: int
):
    return _users.get_user(user_id)


def update_language(
    user_id: int,
    language: str
):
    _users.update_language(
        user_id,
        language
    )


def update_summary_type(
    user_id: int,
    summary_type: str
):
    _users.update_summary_type(
        user_id,
        summary_type
    )


def increase_requests(
    user_id: int
):
    _users.increase_requests(
        user_id
    )


def get_requests(
    user_id: int
):
    return _users.get_requests(
        user_id
    )
    # =====================================
# Compatibility API
# =====================================

def set_language(
    user_id: int,
    language: str
):
    _users.update_language(
        user_id,
        language
    )


def get_language(
    user_id: int
):
    return _users.get_user(
        user_id
    )["language"]


def set_summary_type(
    user_id: int,
    summary_type: str
):
    _users.update_summary_type(
        user_id,
        summary_type
    )


def get_summary_type(
    user_id: int
):
    return _users.get_user(
        user_id
    )["summary_type"]


def increment_requests(
    user_id: int
):
    _users.increase_requests(
        user_id
    )
