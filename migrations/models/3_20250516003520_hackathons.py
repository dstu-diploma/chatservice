from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DELETE FROM "requests";
        ALTER TABLE "requests" ADD "hackathon_id" INT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "requests" DROP COLUMN "hackathon_id";"""
