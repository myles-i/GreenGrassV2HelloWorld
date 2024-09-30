import sys
import json
import time
import logging
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def message_handler(protocol, topic, message_id, status, route, message_payload):
    logger.info(f"Received message on {topic}: {message_payload}")


if __name__ == "__main__":
    base_topic = "GGHW" # only used if no topic is provided to client.publish_message
    subscribe_topic = "GGHelloWorld/inbox"
    publish_topic = "GGHelloWorld/outbox"

    # Initialize client (both mqtt and ipc pubsub - i.e. "ipc_mqtt")
    client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=message_handler)
    client.activate_mqtt_pubsub()
    client.activate_ipc_pubsub()
        
    # Subscribe to topic
    client.subscribe_to_topic("ipc_mqtt", subscribe_topic)

    # use sdk message formatter for consistent messaging API (starting point for routes etc
    message_formatter = PubSubMessageFormatter()

    try:
        while True:
            my_message = {"user_msg": "Hello World, from GreenGrassCore V2"}
            sdk_message = message_formatter.get_message(message=my_message)
            client.publish_message('ipc_mqtt', sdk_message, topic=publish_topic)  # Publish using MQTT and IPC protocol
            
            logger.info(f"Published sdk message to {publish_topic}: {sdk_message}")
            time.sleep(5)
    except Exception as e:
        logger.error(f"Error running the component: {e}")
