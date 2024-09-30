import sys
import json
import time
import logging
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GreenGrassV2HelloWorld:
    def __init__(self, config):
        self.publish_topic = config['PublishTopic']
        self.subscribe_topic = config['SubscribeTopic']
        
        logger.info(f"Publishing to topic: {self.publish_topic}")
        logger.info(f"Subscribing to topic: {self.subscribe_topic}")
        
        self.client = AwsGreengrassPubSubSdkClient(base_topic="GGHelloWorld", default_message_handler=self.message_handler)
        self.client.activate_ipc_pubsub()
        
        # Subscribe to the topic
        self.client.subscribe_to_topic("ipc", self.subscribe_topic)

    def message_handler(self, protocol, topic, message_id, status, route, message):
        logger.info(f"Received message on {topic}: {message}")

    def publish_message(self):
        while True:
            message = {"message": "Hello World, from GreenGrassCore V2"}
            self.client.publish_message("ipc", message, topic=self.publish_topic)
            logger.info(f"Published message to {self.publish_topic}: {message}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        config_str = sys.argv[1]
        config = json.loads(config_str)
        component = GreenGrassV2HelloWorld(config)
        component.publish_message()
    except Exception as e:
        logger.error(f"Error running the component: {e}")
