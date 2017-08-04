import logging
import time

import datadog.dogstatsd as dogstatsd
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


API = [
    'api/stats',
    'api/metrics',
]


class Monitor:
    def __init__(self, args):
        logger.info("|-o-| Starting |-o-|")
        self.args = args
        self.statsd = dogstatsd.DogStatsd(
            host=self.args.statsd_host,
            port=self.args.statsd_port,
            namespace=self.args.namespace,
        )

    def do_request(self, url):
        logger.info(
            "requesting - {}".format(url)
        )
        return requests.get(
            url, auth=(
                self.args.mqtt_api_username,
                self.args.mqtt_api_password,
            )
        )

    def get_cluster_info(self):
        url = self.get_url("api/nodes")
        running_servers = []
        r = self.do_request(url)
        servers = r.json()
        for server in servers:
            if server["cluster_status"] == "Running":
                server["url"] = "http://{}:18083".format(
                    server["name"].split("@")[1]
                )
                running_servers.append(server)
                self.check_service(server["name"])
                continue
            self.check_service(server["name"], self.statsd.CRITICAL)
        return running_servers

    def check_service(self, server, status=None):
        if not status:
            status = self.statsd.OK
        self.statsd.service_check(
            "mqtt.broker",
            status,
            hostname=server,
        )

    def run(self):
        while True:
            try:
                servers = self.get_cluster_info()
                for server in servers:
                    for api in API:
                        url = self.get_url(api, server=server['url'])
                        r = self.do_request(url)
                        self.send_metrics(r.json(), server['name'])
            except Exception as e:
                logger.error(e)
            finally:
                time.sleep(15)

    def get_url(self, uri, server=None):
        if not server:
            server = self.args.mqtt_api_url
        return "{}/{}".format(server, uri)

    def send_metrics(self, metrics, server):
        for k, v in metrics.items():
            metric = k.replace("/", ".")
            value = float(v)
            logger.info(
                "sending metrics - {}: {}".format(metric, value)
            )
            self.statsd.gauge(
                metric, value,
                tags=["server:{}".format(server)]
            )
