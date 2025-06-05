import sqlite3

from config.config import settings

DB_PATH = settings.DB_PATH


class DB:
    def __init__(self):
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                user_id TEXT PRIMARY KEY,
                file_name TEXT,
                total_tokens INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    async def create_token_record(self, user_id: str, file_name: str, total_tokens: int = 0):
        """
        创建一条新的 token 记录
        :param user_id: 用户 ID
        :param file_name: 文件名
        :param total_tokens: token 数量
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tokens (user_id, file_name, total_tokens)
                VALUES (?, ?, ?)
            """, (user_id, file_name, total_tokens))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"文件 {file_name} 已存在！")
        finally:
            conn.close()

    async def update_token_record(self, user_id: str, file_name: str, tokens):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tokens (user_id, file_name, total_tokens)
            VALUES (?, ?, ?)
            ON CONFLICT(file_name) DO UPDATE SET
            total_tokens = total_tokens + ?
        """, (user_id, file_name, tokens))
        conn.commit()
        conn.close()

    async def read_token_record(self, user_id: str, file_name: str) -> dict or None:
        """
        查询指定文件名的 token 记录
        :param user_id: 用户 ID
        :param file_name: 文件名
        :return: 包含记录的字典或 None
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tokens WHERE user_id=? AND file_name=?", (user_id, file_name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            # return {
            #     "user_id": result[0],
            #     "file_name": result[1],
            #     "total_tokens": result[2]
            # }
            return result[2]
        return None

    async def delete_token_record(self, user_id: str):
        """
        删除指定文件名的 token 记录
        :param user_id: 用户id
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tokens WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

    async def list_user_records(self,  user_id: str):
        """
        列出所有 token 记录
        :return: 所有记录的列表
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tokens WHERE user_id=?", (user_id,))
        results = cursor.fetchall()
        conn.close()

        # 将结果转为 dict 格式
        columns = [column[0] for column in cursor.description]
        result_dicts = [dict(zip(columns, row)) for row in results]

        return result_dicts


    async def list_all_records(self):
        """
        列出所有 token 记录
        :return: 所有记录的列表
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tokens")
        results = cursor.fetchall()
        conn.close()

        return [
            {"user_id": r[0], "file_name": r[1], "total_tokens": r[2]}
            for r in results
        ]


db = DB()
