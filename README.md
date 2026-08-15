# MQTT Message Receiver

A simple Python program to receive (subscribe to) general MQTT messages from a broker running on `localhost:1883` for the topic `/mqtt`.

## Features

- Connects to MQTT broker at localhost port 1883
- Subscribes to topic `/mqtt` (configurable)
- Prints timestamp, topic, QoS, retain flag, and payload for every received message
- Handles both text (UTF-8) and binary payloads
- Auto-reconnects on connection loss
- Supports MQTT v5 via paho-mqtt 2.x (CallbackAPIVersion.VERSION2)
- Configurable host, port, topic, QoS, client ID via CLI args

## Requirements

- Python 3.7+
- paho-mqtt >= 2.1.0

## Installation

```powershell
# From this directory
pip install -r requirements.txt
```

Or manually:
```powershell
pip install paho-mqtt
```

## Usage

### Basic (default topic `/mqtt`)

```powershell
python mqtt_subscriber.py
```

### Subscribe to a topic and all its subtopics

```powershell
python mqtt_subscriber.py --topic "/mqtt/#"
python mqtt_subscriber.py --topic "/gw/#"
```

### Custom broker / port / QoS

```powershell
python mqtt_subscriber.py --host localhost --port 1883 --topic "/mqtt" --qos 1
```

### Other options

```powershell
python mqtt_subscriber.py --help
```

Available options:
- `--host` : Broker hostname/IP (default: localhost)
- `--port` : Broker port (default: 1883)
- `--topic` : Topic filter to subscribe (default: /mqtt). Supports wildcards like `#` or `+`
- `--qos` : 0, 1 or 2 (default 0)
- `--client-id` : Custom MQTT client ID
- `-v, --verbose` : Verbose mode (currently reserved for future use)

## Example Output

```
[2026-04-10 12:34:56.789] MQTT Subscriber starting...
[2026-04-10 12:34:56.789] Broker: localhost:1883
[2026-04-10 12:34:56.789] Topic: /mqtt (QoS 0)
[2026-04-10 12:34:56.789] Press Ctrl+C to exit.
==================================================
[2026-04-10 12:34:56.812] Connected to MQTT broker at localhost:1883
[2026-04-10 12:34:56.815] Subscribed to topic: '/mqtt' (QoS 0)
[2026-04-10 12:35:01.234] [/mqtt] QoS:0 
    Payload: Hello from device
--------------------------------------------------
[2026-04-10 12:35:03.111] [/mqtt/sensor] QoS:0 
    Payload: {"temp": 23.5, "hum": 45}
--------------------------------------------------
```

## Testing

You can use any MQTT client or the included test publisher (see below) to send messages.

With mosquitto_pub (if installed):

```powershell
mosquitto_pub -h localhost -p 1883 -t "/mqtt" -m "test message"
mosquitto_pub -h localhost -p 1883 -t "/mqtt/data" -m '{"key":"value"}'
```

## Running in Background (Windows)

```powershell
# Simple
Start-Process python -ArgumentList "mqtt_subscriber.py" -WindowStyle Hidden

# Or use a job
$job = Start-Job { python D:\Work\Minew\mqtt\mqtt_subscriber.py }
```

To stop: `Get-Job | Stop-Job`

## Notes

- The program uses `loop_forever()` which handles reconnection automatically.
- Topic `/mqtt` is exact match by default. To receive messages from `/mqtt` and any sub-topics (e.g. `/mqtt/foo`, `/mqtt/foo/bar`), subscribe with `--topic "/mqtt/#"`
- No authentication is configured (assumes open broker or credentials not required).
- For production, consider adding TLS, username/password, certificate validation, structured logging, etc.

## License

MIT (or public domain, use freely)
