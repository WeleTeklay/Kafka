
from kafka import KafkaConsumer
from hdfs import InsecureClient
import json
import time
import uuid

BATCH_SIZE = 5
FLUSH_INTERVAL = 15
IDLE_TIMEOUT = 20
HDFS_DIR = '/drought-data/raw/rainfall'
HDFS_USER = 'hp'  # change to your actual username

consumer = KafkaConsumer(
    'rainfall-data',
    bootstrap_servers='localhost:9092',
    group_id='rainfall-batch-writer',
    auto_offset_reset='earliest',
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

hdfs_client = InsecureClient('http://localhost:9870', user=HDFS_USER)

buffer = []
last_flush = time.time()
last_message_time = time.time()

def flush_to_hdfs(buffer):
    if not buffer:
        return
    filename = f"{HDFS_DIR}/batch_{int(time.time())}_{uuid.uuid4().hex[:6]}.json"
    with hdfs_client.write(filename, encoding='utf-8') as writer:
        for msg in buffer:
            writer.write(json.dumps(msg) + '\n')
    print(f"Flushed {len(buffer)} messages to {filename}")

print("Listening for rainfall messages (auto-stops after ~20s of no new data)...")

while True:
    records = consumer.poll(timeout_ms=5000)
    if records:
        for tp, messages in records.items():
            for message in messages:
                buffer.append(message.value)
        last_message_time = time.time()

    size_triggered = len(buffer) >= BATCH_SIZE
    time_triggered = (time.time() - last_flush) >= FLUSH_INTERVAL
    if buffer and (size_triggered or time_triggered):
        flush_to_hdfs(buffer)
        buffer = []
        last_flush = time.time()

    if time.time() - last_message_time > IDLE_TIMEOUT:
        flush_to_hdfs(buffer)
        buffer = []
        print("No new messages for a while — stopping.")
        break

consumer.close()
print("Consumer stopped cleanly.")

