import sqlite3
import os



DB_PATH = "data/bot.db"



class Database:


    def __init__(self):


        os.makedirs(
            "data",
            exist_ok=True
        )


        self.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )


        self.create_tables()





    def create_tables(self):


        cursor = self.connection.cursor()



        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS users (

                user_id INTEGER PRIMARY KEY,

                language TEXT DEFAULT 'Persian',

                summary_type TEXT DEFAULT 'detailed',

                requests INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """
        )
        cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                video_id TEXT,

                title TEXT,

                channel TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """
)
        cursor.execute(
    """
                CREATE TABLE IF NOT EXISTS cache (

                video_id TEXT PRIMARY KEY,

                title TEXT,

                channel TEXT,

                summary TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """
)


        self.connection.commit()





    def execute(
        self,
        query,
        params=()
    ):


        cursor = self.connection.cursor()


        cursor.execute(
            query,
            params
        )


        self.connection.commit()



        return cursor