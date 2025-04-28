from tortoise.models import Model
from tortoise import fields


class ChatMessageModel(Model):
    id = fields.IntField(pk=True)
    from_user_id = fields.IntField()
    to_user_id = fields.IntField()
    contents = fields.CharField(max_length=800)

    send_time = fields.DatetimeField(auto_now_add=True)
    read_time = fields.DatetimeField(null=True)

    class Meta:
        table: str = "messages"
