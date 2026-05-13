from umqtt.simple import MQTTClient
import digital

class AdafruitIO:

    def __init__(self, username, key):

        self.username = username
        self.key = key

        self.client = MQTTClient(
            "ESP32",
            "io.adafruit.com",
            user=username,
            password=key
        )

        self.devices = {}

    # ----------------------------------

    def addDevice(self, feed, pin):

        topic = self.username + "/feeds/" + feed

        digital.pinMode(pin, digital.OUTPUT)

        self.devices[topic] = pin

    # ----------------------------------

    def callback(self, topic, msg):

        topic = topic.decode()
        msg   = msg.decode()

        print(topic, msg)

        if topic in self.devices:

            pin = self.devices[topic]

            if msg == "ON":

                digital.digitalWrite(pin, 1)
                print("PIN", pin, "ON")

            else:

                digital.digitalWrite(pin, 0)
                print("PIN", pin, "OFF")

    # ----------------------------------

    def begin(self):

        self.client.set_callback(self.callback)

        self.client.connect()

        for topic in self.devices:

            self.client.subscribe(
                topic.encode()
            )

            print("Subscribed :", topic)

        print("Adafruit IO Ready")

    # ----------------------------------

    def run(self):

        self.client.check_msg()

