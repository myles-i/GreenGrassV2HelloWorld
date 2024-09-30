import sys
import json
import time
import logging
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def message_handler(self, protocol, topic, message_id, status, route, message):
    logger.info(f"Received message on {topic}: {message}")


if __name__ == "__main__":
    base_topic = "GGHW" # only used if no topic is provided to client.publish_message
    subscribe_topic = "GGHelloWorld/inbox"
    publish_topic = "GGHelloWorld/outbox"

    # Initialize MQTT client
    client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=message_handler)
    client.activate_mqtt_pubsub()
        
    # Subscribe to the MQTT topic
    client.subscribe_to_topic("mqtt", subscribe_topic)

    try:
        while True:
            message = {"message": "Hello World, from GreenGrassCore V2"}
            client.publish_message("mqtt", message, topic=publish_topic)  # Publish using MQTT protocol
            logger.info(f"Published hello world message to {publish_topic}: {message}")
            time.sleep(5)
    except Exception as e:
        logger.error(f"Error running the component: {e}")
