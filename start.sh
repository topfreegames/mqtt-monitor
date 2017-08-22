#! /bin/bash

mqtt-monitor --mqtt-api-username $MQTT_API_USERNAME --mqtt-api-password $MQTT_API_PASSWORD --statsd-host $STATSD_HOST  --statsd-port $STATSD_PORT --kube-router $EMQTT_ROUTE
