#!/usr/bin/env python3
"""
Simple MQTT Publisher for testing the subscriber.

Publishes messages to localhost:1883 on a given topic.

Usage:
    python mqtt_publisher.py --message "hello"
    python mqtt_publisher.py -t "/mqtt" -m "test payload" --count 5 --interval 1
"""

import argparse
import datetime
import json
import sys
import time

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"[{get_timestamp()}] Publish client failed to connect: {reason_code}")
        sys.exit(1)
    else:
        print(f"[{get_timestamp()}] Publisher connected to {userdata['host']}:{userdata['port']}")


def on_publish(client, userdata, mid, reason_code, properties):
    if userdata.get("verbose"):
        print(f"[{get_timestamp()}] Message published (mid={mid})")


def main():
    parser = argparse.ArgumentParser(description="Simple MQTT publisher for testing.")
    parser.add_argument(
        "--host", default="localhost", help="MQTT broker host"
    )
    parser.add_argument(
        "--port", type=int, default=1883, help="MQTT broker port"
    )
    parser.add_argument(
        "-t", "--topic", default="/mqtt", help="Topic to publish to"
    )
    parser.add_argument(
        "-m", "--message", default=None, help="Message payload to send (string)"
    )
    parser.add_argument(
        "-f", "--file", default=None, help="Read payload from file instead of --message"
    )
    parser.add_argument(
        "--json", action="store_true", help="Send a sample JSON payload (ignores --message)"
    )
    parser.add_argument(
        "--count", type=int, default=1, help="Number of messages to send (default: 1)"
    )
    parser.add_argument(
        "--interval", type=float, default=0.5, help="Seconds between messages (default: 0.5)"
    )
    parser.add_argument(
        "--qos", type=int, default=0, choices=[0, 1, 2], help="QoS (default 0)"
    )
    parser.add_argument(
        "--retain", action="store_true", help="Set retain flag"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "rb") as f:
                payload = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    elif args.json:
        sample = {
            "timestamp": datetime.datetime.now().isoformat(),
            "device": "test-device",
            "data": {"temperature": 23.7, "humidity": 48, "status": "ok"},
            "seq": 0,
        }
        payload = json.dumps(sample, indent=2).encode("utf-8")
    elif args.message is not None:
        payload = args.message.encode("utf-8")
    else:
        payload = f"test message at {datetime.datetime.now().isoformat()}".encode("utf-8")

    userdata = {"host": args.host, "port": args.port, "verbose": args.verbose}

    client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id=f"mqtt_test_pub_{int(time.time())}",
        userdata=userdata,
    )
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"[{get_timestamp()}] Connecting to {args.host}:{args.port} ...")
    try:
        client.connect(args.host, args.port, keepalive=30)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    client.loop_start()

    # Wait for connection (simple)
    timeout = 5
    while not client.is_connected() and timeout > 0:
        time.sleep(0.1)
        timeout -= 0.1

    if not client.is_connected():
        print("Failed to connect within timeout.")
        client.loop_stop()
        sys.exit(1)

    print(f"[{get_timestamp()}] Publishing {args.count} message(s) to '{args.topic}' (QoS {args.qos}, retain={args.retain})")
    print(f"    Payload preview: {payload[:120]}{b'...' if len(payload) > 120 else b''}")

    try:
        for i in range(args.count):
            current_payload = payload
            if args.json:
                # regenerate with seq for json
                sample = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "device": "test-device",
                    "data": {"temperature": 23.7 + i * 0.1, "humidity": 48, "status": "ok"},
                    "seq": i + 1,
                }
                current_payload = json.dumps(sample, indent=2).encode("utf-8")

            result = client.publish(
                args.topic,
                payload=current_payload,
                qos=args.qos,
                retain=args.retain,
            )
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Publish error: {result.rc}")
            else:
                if args.verbose or args.count > 1:
                    print(f"[{get_timestamp()}] Sent #{i+1}: {current_payload[:80]}...")

            if i < args.count - 1:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        time.sleep(0.2)  # allow last publish to go out
        client.loop_stop()
        client.disconnect()
        print(f"[{get_timestamp()}] Publisher done.")


if __name__ == "__main__":
    main()
