import argparse
import mqtt_monitor.monitor as monitor


def main():
    parser = argparse.ArgumentParser(
        prog="MQTT monitor",
        description='Monitors $SYS tree and sends it to DatadogStatsd'
    )
    parser.add_argument('--exclude-mqtt-server-name', default=True)
    parser.add_argument('--mqtt-host', default='localhost')
    parser.add_argument('--mqtt-port', type=int, default=1883)
    parser.add_argument('--mqtt-username', default=None)
    parser.add_argument('--mqtt-password', default=None)
    parser.add_argument('--ca-file', default=False)
    parser.add_argument('--insecure', action='store_true')
    parser.add_argument('--statsd-host', default='localhost')
    parser.add_argument('--statsd-port', type=int, default=8125)
    parser.add_argument('--namespace', default='mqtt-broker')
    parser.add_argument('--client-name', default='mqtt-monitor')
    args = parser.parse_args()
    monitor.Monitor(args).run()
