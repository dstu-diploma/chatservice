from tortoise.models import Model
from tortoise import fields


class RequestModel(Model):
    id = fields.IntField(pk=True)
    author_user_id = fields.IntField()
    subject = fields.CharField(max_length=150)
    closed_by_user_id = fields.IntField(null=True)

    class Meta:
        table: str = "requests"


class MessageModel(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    message = fields.CharField(max_length=500)
    send_date = fields.DatetimeField(auto_now_add=True)

    request: fields.ForeignKeyRelation[RequestModel] = fields.ForeignKeyField(
        model_name="models.RequestModel",
        related_name="request_messages",
        on_delete=fields.CASCADE,
    )
