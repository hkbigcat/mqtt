#!/usr/bin/env python3
"""
MQTT Subscriber - Receives general MQTT messages from localhost:1883 on topic "/mqtt"

Usage:
    python mqtt_subscriber.py
    python mqtt_subscriber.py --topic "/mqtt/#"
    python mqtt_subscriber.py --host localhost --port 1883 --topic "/mqtt"
"""

import argparse
import datetime
import sys

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"[{get_timestamp()}] Failed to connect: {reason_code}. Retrying...")
    else:
        print(f"[{get_timestamp()}] Connected to MQTT broker at {userdata['host']}:{userdata['port']}")
        topic = userdata.get("topic", "/mqtt")
        qos = userdata.get("qos", 0)
        result, mid = client.subscribe(topic, qos=qos)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{get_timestamp()}] Subscribed to topic: '{topic}' (QoS {qos})")
        else:
            print(f"[{get_timestamp()}] Subscribe failed for topic: '{topic}' (code: {result})")


def on_message(client, userdata, msg):
    timestamp = get_timestamp()
    topic = msg.topic
    qos = msg.qos
    retain = "RETAIN" if msg.retain else ""
    try:
        payload_str = msg.payload.decode("utf-8")
        payload_display = payload_str
    except UnicodeDecodeError:
        payload_display = f"<binary: {msg.payload.hex()}>"

    print(f"[{timestamp}] [{topic}] QoS:{qos} {retain}")
    print(f"    Payload: {payload_display}")
    print("-" * 50)


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"[{get_timestamp()}] Unexpected disconnection. Reason: {reason_code}")
    else:
        print(f"[{get_timestamp()}] Disconnected cleanly.")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    for sub_result in reason_code_list:
        if sub_result.is_failure:
            print(f"[{get_timestamp()}] Subscription failed: {sub_result}")
        else:
            print(f"[{get_timestamp()}] Subscription successful (mid={mid})")


def main():
    parser = argparse.ArgumentParser(
        description="MQTT message receiver for general messages."
    )
    parser.add_argument(
        "--host", default="localhost", help="MQTT broker host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=1883, help="MQTT broker port (default: 1883)"
    )
    parser.add_argument(
        "--topic",
        default="/mqtt",
        help='Topic to subscribe to (default: /mqtt). Use "/mqtt/#" for all subtopics.',
    )
    parser.add_argument(
        "--qos", type=int, default=0, choices=[0, 1, 2], help="QoS level (default: 0)"
    )
    parser.add_argument(
        "--client-id",
        default=None,
        help="Client ID (default: auto-generated)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    userdata = {
        "host": args.host,
        "port": args.port,
        "topic": args.topic,
        "qos": args.qos,
        "verbose": args.verbose,
    }

    client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id=args.client_id,
        userdata=userdata,
    )

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    # Optional: set will message for last will
    # client.will_set("/mqtt/status", payload="offline", qos=0, retain=True)

    print(f"[{get_timestamp()}] MQTT Subscriber starting...")
    print(f"[{get_timestamp()}] Broker: {args.host}:{args.port}")
    print(f"[{get_timestamp()}] Topic: {args.topic} (QoS {args.qos})")
    print(f"[{get_timestamp()}] Press Ctrl+C to exit.")
    print("=" * 50)

    try:
        client.connect(args.host, args.port, keepalive=60)
    except Exception as e:
        print(f"[{get_timestamp()}] Connection error: {e}")
        sys.exit(1)

    try:
        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        print(f"\n[{get_timestamp()}] Shutting down...")
        client.disconnect()
        print(f"[{get_timestamp()}] Goodbye.")
    except Exception as e:
        print(f"[{get_timestamp()}] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
