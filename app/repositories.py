import psycopg2

from psycopg2.extras import DictCursor

from config import DATABASE_CONFIG


class Face:

    def __conn(self):
        return psycopg2.connect(**DATABASE_CONFIG)

    def all(self):
        with self.__conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "select id, name, encode(image, 'base64') as image, image_extension, embedding "
                    "from faces "
                    "order by name")
                return cur.fetchall()

    def store(self, face):
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "insert into faces values (%s, %s, %s, %s, %s)",
                    (face['id'], face['name'], face['image'], face['image_extension'], face['embedding'])
                )
            conn.commit()

    def search_by_name(self, name):
        with self.__conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                like_pattern = f'%{name}%'
                cur.execute(
                    "select id, name, encode(image, 'base64') as image, image_extension "
                    "from faces "
                    "where name like %s "
                    "order by name",
                    (like_pattern,)
                )
                return cur.fetchall()

    def similar_by_name(self, name):
        with self.__conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                like_pattern = f'%{name}%'
                cur.execute(
                    "select id from faces where name like %s order by name limit 1", (like_pattern,)
                )
                first_row = cur.fetchone()
                if first_row:
                    cur.execute(
                        "select id, name, encode(image, 'base64') as image, image_extension, embedding, "
                        "1 - (embedding <-> (SELECT embedding FROM faces WHERE id = %s)) as similarity "
                        "from faces "
                        "order by embedding <-> (SELECT embedding FROM faces WHERE id = %s) LIMIT 5",
                        (first_row['id'], first_row['id'])
                    )
                    return cur.fetchall()
                else:
                    return []
