from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "messages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "from_user_id" INT NOT NULL,
    "to_user_id" INT NOT NULL,
    "contents" VARCHAR(800) NOT NULL,
    "send_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "read_time" TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
