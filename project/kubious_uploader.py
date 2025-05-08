import network
from time import sleep, ticks_ms, ticks_diff
from umqtt.simple import MQTTClient
import ujson

class KubiosUploader:
    def __init__(self, ssid, password, broker_ip, topic="kubios-request", client_id="pico-client"):
        self.ssid = ssid
        self.password = password
        self.broker_ip = broker_ip
        self.topic = topic
        self.client_id = client_id
        self.mqtt_client = None
        self.analysis_result = None
        self.response_received = False

    def connect_wlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)
        while not wlan.isconnected():
            print("Connecting to WiFi...")
            sleep(1)
        print("Connected. IP:", wlan.ifconfig()[0])

    def connect_mqtt(self):
        self.mqtt_client = MQTTClient(self.client_id, self.broker_ip, 21883)
        self.mqtt_client.set_callback(self.on_message)
        self.mqtt_client.connect(clean_session=True)
        self.mqtt_client.subscribe(b"kubios-response")
        print("Connected to MQTT broker.")

    def send_data(self, rri_data, user_id=123):
        if not self.mqtt_client:
            raise Exception("MQTT client not connected")

        message = {
            "id": user_id,
            "type": "RRI",
            "data": rri_data,
            "analysis": {"type": "readiness"}
        }

        json_message = ujson.dumps(message)
        self.mqtt_client.publish(self.topic, json_message)
        print(f"Published to {self.topic}: {json_message}")

    def on_message(self, topic, msg):
        print("[Kubios] Received message on:", topic)
        try:
            data = ujson.loads(msg)
            analysis = data.get("data", {}).get("analysis", {})
            print("[Kubios] Analysis:", analysis)
            self.analysis_result = analysis
            self.response_received = True
        except Exception as e:
            print("Error parsing response:", e)
            self.analysis_result = None
            self.response_received = False

    def check_for_response(self):
        if self.mqtt_client:
            try:
                self.mqtt_client.check_msg()
            except Exception as e:
                print("MQTT check_msg failed:", e)

    def upload_ppis(self, rri_data):
        try:
            if len(rri_data) < 10:
                print("Not enough RRI data")
                return False

            self.analysis_result = None
            self.response_received = False

            self.connect_wlan()
            self.connect_mqtt()
            self.send_data(rri_data)

            # Wait up to 7 seconds for a response
            start_wait = ticks_ms()
            while not self.response_received and ticks_diff(ticks_ms(), start_wait) < 7000:
                self.check_for_response()
                sleep(0.2)

            self.mqtt_client.disconnect()
            print("Disconnected from MQTT broker.")

            return self.analysis_result is not None

        except Exception as e:
            print("Upload to Kubios failed:", e)
            return False



