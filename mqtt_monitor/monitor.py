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

    def do_kubeapi_request(self, uri):
        logger.info(
            "requesting to kube api - {}".format(uri)
        )

        return requests.get(
            self.get_url(uri, server=self.args.kube_api_url),
            headers={
                'Authorization': 'Bearer {}'.format(self.args.kube_token)
            },
            verify=False,
        )

    def get_cluster_info(self):
        running_servers = []
        r = self.do_kubeapi_request('api/v1/namespaces/{}/pods/'.format(
            self.args.kube_namespace
        ))
        servers = [
            x['metadata']['name']
            for x in r.json()['items'] if
            x['metadata']['labels']['app'] == self.args.kube_app_label
        ]

        for server in servers:
            server_item = {
                'name': server,
                'url': 'http://{}.{}:18083'.format(
                    server,
                    self.args.kube_router
                )
            }
            self.check_service(server_item, len(servers))
            running_servers.append(server_item)
        return running_servers

    def check_service(self, server, servers_count):
        status = self.statsd.OK
        url = self.get_url('api/nodes', server=server['url'])
        try:
            r = self.do_request(url)
            if r.status_code != requests.codes.ok or len(r.json()) < servers_count:
                status = self.statsd.CRITICAL
        except Exception as e:
            logger.exception(e)
            status = self.statsd.CRITICAL
        finally:
            self.statsd.service_check(
                "mqtt.broker",
                status,
                hostname=server['name'],
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
                logger.exception(e)
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
