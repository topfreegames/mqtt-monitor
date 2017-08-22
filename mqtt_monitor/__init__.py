import os
import argparse
import mqtt_monitor.monitor as monitor


def main():
    kube_token = None
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token'):
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
            kube_token = f.read()

    parser = argparse.ArgumentParser(
        prog="MQTT monitor",
        description='Monitors emqtt api and sends it to DatadogStatsd'
    )

    parser.add_argument('--mqtt-api-username', default=None)
    parser.add_argument('--mqtt-api-password', default=None)
    parser.add_argument('--statsd-host', default='localhost')
    parser.add_argument('--statsd-port', type=int, default=8125)
    parser.add_argument('--namespace', default='mqtt-broker')
    parser.add_argument('--kube-namespace', default='chat')
    parser.add_argument('--kube-router', default=None)
    parser.add_argument('--kube-token', default=kube_token)
    parser.add_argument('--kube-app-label', default='emqtt')
    parser.add_argument('--kube-api-url', default="https://{}:{}".format(
        os.environ.get('KUBERNETES_SERVICE_HOST', None),
        os.environ.get('KUBERNETES_PORT_443_TCP_PORT', None),
    ))
    args = parser.parse_args()
    monitor.Monitor(args).run()
