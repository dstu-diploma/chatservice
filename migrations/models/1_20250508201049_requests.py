from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "requests" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "author_user_id" INT NOT NULL,
            "subject" VARCHAR(150) NOT NULL,
            "closed_by_user_id" INT
        );

        CREATE TABLE IF NOT EXISTS "messagemodel" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "user_id" INT NOT NULL,
            "message" VARCHAR(500) NOT NULL,
            "send_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "request_id" INT NOT NULL REFERENCES "requests" ("id") ON DELETE CASCADE
        );

        DROP TABLE IF EXISTS "messages";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "requests";
        DROP TABLE IF EXISTS "messagemodel";"""
