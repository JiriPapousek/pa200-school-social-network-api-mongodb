from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

import os
import schemas

SERVICE_BUS_CONN_STRING = os.getenv("CUSTOMCONNSTR_SERVICE_BUS")


async def send_failed_auth_message(user: schemas.User):
    try:
        message = ServiceBusMessage(user.username)
        async with ServiceBusClient.from_connection_string(
                conn_str=SERVICE_BUS_CONN_STRING,
                logging_enable=True) as servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name="failed_auth")
            async with sender:
                await sender.send_messages(message)

    except Exception as e:
        print(e)
        return str(e)
