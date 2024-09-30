import sys
import json
import time
import logging
import numpy as np
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# initialize data
num_vehicles = 5
max_co2_levels_by_vehicle = np.ones(num_vehicles) * -1
class MyAwsGreengrassV2Component():
    def __init__(self):
        # initialize client
        base_topic = "GGHW" # only used if no topic is provided to client.publish_message. We don't use it in this simple example
        self.client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=self.message_handler)
        self.client.activate_mqtt_pubsub()
        self.client.activate_ipc_pubsub()

        # message formatter for consistent messaging API (starting point for routes etc)
        self.message_formatter = PubSubMessageFormatter()

        # Expose the client methods as class methods
        self.subscribe_to_topic  = self.client.subscribe_to_topic

    def publish_message(self, message, topic=None):
        sdk_message = self.message_formatter.get_message(message=message)
        self.client.publish_message('ipc_mqtt', sdk_message, topic=topic)  # Publish using MQTT and IPC protocol
        return sdk_message
    
    def message_handler(self, protocol, topic, message_id, status, route, message_payload):
            # logger.info(f"Received message on {topic}: {message_payload}")
            global max_co2_levels_by_vehicle
            # {'device_id': '3', 'data': {'timestep_time': 2.0, 'vehicle_CO': 164.78,
            #  'vehicle_CO2': 2624.72, 'vehicle_HC': 0.81, 'vehicle_NOx': 1.2, 
            # 'vehicle_PMx': 0.07, 'vehicle_angle': 125.41, 'vehicle_eclass': 'HBEFA3/PC_G_EU4', 
            # 'vehicle_electricity': 0.0, 'vehicle_fuel': 1.13, 'vehicle_id': 'veh3', 'vehicle_lane': '724636540#2_0',
            #  'vehicle_noise': 55.94, 'vehicle_pos': 5.1, 'vehicle_route': '!veh3!var#1', 'vehicle_speed': 0.0, 
            # 'vehicle_type': 'veh_passenger', 'vehicle_waiting': 0.0, 'vehicle_x': 26221.37, 'vehicle_y': 26484.93, 
            # 'data_send_complete': False}}
            # logger.info(f"Received message on {topic}: {message_payload}")
            if route == "vehicle_data":
                data_idx = message_payload["device_id"]
                msg_data = message_payload["data"]
                if msg_data["data_send_complete"]:
                    message = {"device_id": data_idx, 
                               "data": {"max_co2": max_co2_levels_by_vehicle[int(data_idx)]}}
                    logger.info(f"Sending max CO2 level for vehicle {data_idx}: {message}")
                    self.publish_message(message, topic="GGHelloWorld/outbox/vehicle"+str(data_idx))
                else:
                    if max_co2_levels_by_vehicle[int(data_idx)] < 0:
                        max_co2_levels_by_vehicle[int(data_idx)] = msg_data["vehicle_CO2"]
                    else:
                        max_co2_levels_by_vehicle[int(data_idx)] = max(msg_data["vehicle_CO2"],
                                                                   max_co2_levels_by_vehicle[int(data_idx)])

if __name__ == "__main__":
    # define topics
    subscribe_topic = "GGHelloWorld/inbox"
    publish_topic = "GGHelloWorld/outbox"

    # Initialize client
    client = MyAwsGreengrassV2Component()

    # subscribe to topic
    # NOTE since we are using the sdk here, the client requires messages json formatted
    # as show below, where the contents of "message" is the actual payload/custom data.
    # {
    # "sdk_version": "0.1.4",
    # "message_id": "20240930180857201116",
    # "status": 200,
    # "route": "default_message_handler",
    # "message": { "user_msg": "Hello World, from IoT CONSOLE" }
    # }
    client.subscribe_to_topic("ipc_mqtt", subscribe_topic)
    while True:
        my_message = {"user_msg": "Hello World, from GreenGrassCore V2"}
        sdk_message = client.publish_message(my_message, topic=publish_topic)
        logger.info(f"Published sdk message to {publish_topic}: {sdk_message}")
        time.sleep(10)