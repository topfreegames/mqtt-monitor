import argparse
import mqtt_monitor.monitor as monitor


def main():
    parser = argparse.ArgumentParser(
        prog="MQTT monitor",
        description='Monitors emqtt api and sends it to DatadogStatsd'
    )
    parser.add_argument('--mqtt-api-url', default='http://localhost:8080')
    parser.add_argument('--mqtt-api-username', default=None)
    parser.add_argument('--mqtt-api-password', default=None)
    parser.add_argument('--statsd-host', default='localhost')
    parser.add_argument('--statsd-port', type=int, default=8125)
    parser.add_argument('--namespace', default='mqtt-broker')
    args = parser.parse_args()
    monitor.Monitor(args).run()
