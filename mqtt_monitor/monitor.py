import datadog.dogstatsd as dogstatsd
import paho.mqtt.client as mqtt


class Monitor:
    def __init__(self, args):
        self.args = args
        self.statsd = dogstatsd.DogStatsd(
            host=self.args.statsd_host,
            port=self.args.statsd_port,
            namespace=self.args.namespace,
        )

    def run(self):
        client = mqtt.Client(client_id=self.args.client_name)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        if self.args.mqtt_username and self.args.mqtt_password:
            client.username_pw_set(
                self.args.mqtt_username,
                self.args.mqtt_password,
            )
        if self.args.ca_file:
            client.tls_set(
                ca_certs=self.args.ca_file
            )
        if self.args.insecure:
            client.tls_insecure_set(self.args.insecure)
        client.connect(self.args.mqtt_host, self.args.mqtt_port, 60)

        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    def transform_topic(self, topic):
        start_metric = 1
        server_name = 'common-mqtt-broker'
        splitted_topic = topic.split("/")
        if self.args.exclude_mqtt_server_name:
            start_metric = 2
            server_name = splitted_topic[1]
        metric = '.'.join(splitted_topic[start_metric:])
        return (metric, server_name)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        try:
            value = float(msg.payload)
            metric, server_name = self.transform_topic(msg.topic)
            self.statsd.gauge(
                metric,
                value,
                tags=["server_name:{}".format(server_name)]
            )
            print(
                "{} {}".format(
                    self.transform_topic(msg.topic),
                    value
                )
            )
        except ValueError:
            print("Error sending data: {} value:{}".format(
                msg.topic,
                msg.payload
            ))
