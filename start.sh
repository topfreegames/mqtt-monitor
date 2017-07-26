#! /bin/bash

echo -e ${CA_CONN_CRT} > /etc/ca_conn.crt
mqtt-monitor --mqtt-host $MQTT_HOST --mqtt-port $MQTT_PORT --mqtt-username $MQTT_USERNAME --mqtt-password $MQTT_PASSWORD --statsd-host $STATSD_HOST  --statsd-port $STATSD_PORT $OTHER_OPTIONS --ca-file /etc/ca_conn.crt
