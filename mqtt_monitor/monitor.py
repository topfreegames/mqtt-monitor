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

    def run(self):
        while True:
            try:
                for api in API:
                    url = self.get_url(api)
                    logger.info(
                        "requesting - {}".format(url)
                    )
                    r = requests.get(
                        url, auth=(
                            self.args.mqtt_api_username,
                            self.args.mqtt_api_password,
                        )
                    )
                    self.send_metrics(r.json())
            except Exception as e:
                logger.error(e)
            finally:
                time.sleep(15)

    def get_url(self, uri):
        return "{}/{}".format(self.args.mqtt_api_url, uri)

    def send_metrics(self, metrics):
        for k, v in metrics.items():
            metric = self.transform_metric(k)
            value = float(v)
            logger.info(
                "sending metrics - {}: {}".format(metric, value)
            )
            self.statsd.gauge(metric, value)

    def transform_metric(self, metric):
        return "{}.{}".format(
            self.args.namespace, metric.replace("/", ".")
        )
