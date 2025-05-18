from app.ports.event_consumer import IEventConsumerPort
from app.events.emitter import Emitter, ExternalEvents
from asyncio import Task


async def __event_callback(payload: dict):
    Emitter.emit(payload["event_name"], payload)


async def register_events(consumer: IEventConsumerPort) -> Task:
    return await consumer.create_consuming_loop(
        [e.value for e in ExternalEvents], __event_callback
    )
