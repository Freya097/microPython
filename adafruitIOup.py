from umqtt.simple import MQTTClient
import digital
import analog
import time

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

        self.digitalPins = {}
        self.analogInputs = {}
        self.analogOutputs = {}

        self.lastSend = time.ticks_ms()

    # =====================================================
    # DIGITAL OUTPUT
    # =====================================================

    def addDevice(self, feed, pin):

        topic = self.username + "/feeds/" + feed

        digital.pinMode(pin, digital.OUTPUT)

        self.digitalPins[topic] = pin

    # =====================================================
    # ANALOG INPUT SEND
    # =====================================================

    def addAnalogSensor(self, feed, pin):

        topic = self.username + "/feeds/" + feed

        analog.analogPin(pin)

        self.analogInputs[topic] = pin

    # =====================================================
    # ANALOG OUTPUT RECEIVE
    # =====================================================

    def addAnalogOutput(self, feed, pin):

        topic = self.username + "/feeds/" + feed

        analog.dacPin(pin)

        self.analogOutputs[topic] = pin

    # =====================================================
    # MQTT CALLBACK
    # =====================================================

    def callback(self, topic, msg):

        topic = topic.decode()
        msg   = msg.decode()

        print(topic, msg)

        # ---------------- DIGITAL ----------------

        if topic in self.digitalPins:

            pin = self.digitalPins[topic]

            if msg == "ON" or msg == "1":

                digital.digitalWrite(pin, 1)

            else:

                digital.digitalWrite(pin, 0)

        # ---------------- ANALOG OUTPUT ----------------

        if topic in self.analogOutputs:

            pin = self.analogOutputs[topic]

            value = int(msg)

            analog.dacWrite(pin, value)

            print("DAC:", pin, value)

    # =====================================================
    # START MQTT
    # =====================================================

    def begin(self):

        self.client.set_callback(self.callback)

        self.client.connect()

        # Subscribe Digital

        for topic in self.digitalPins:

            self.client.subscribe(topic.encode())

            print("Subscribed:", topic)

        # Subscribe Analog Output

        for topic in self.analogOutputs:

            self.client.subscribe(topic.encode())

            print("Subscribed:", topic)

        print("Adafruit IO Ready")

    # =====================================================
    # SEND ANALOG SENSOR DATA
    # =====================================================

    def sendAnalog(self):

        for topic in self.analogInputs:

            pin = self.analogInputs[topic]

            value = analog.analogRead(pin)

            self.client.publish(
                topic.encode(),
                str(value).encode()
            )

            print("SEND:", topic, value)

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.client.check_msg()

        # Send every 2 seconds

        if time.ticks_diff(
            time.ticks_ms(),
            self.lastSend
        ) > 2000:

            self.sendAnalog()

            self.lastSend = time.ticks_ms()
            
# =====================================================
# SEND ANALOG SENSOR DATA
# =====================================================

def sendAnalog(self):

    for topic in self.analogInputs:

        pin = self.analogInputs[topic]

        # Convert ADC to 0-100%
        value = analog.analogPercent(pin)

        # Send percentage to Adafruit IO
        self.client.publish(
            topic.encode(),
            str(value).encode()
        )

        print("SEND:", topic, value, "%")

