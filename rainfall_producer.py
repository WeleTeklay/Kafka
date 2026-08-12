
from kafka import KafkaProducer
import csv
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all'
)

with open('rainfall.csv') as f:
    rows = list(csv.DictReader(f))

for row in rows:
    event = {
        "region": row["region"],
        "date": row["date"],
        "rainfall_mm": float(row["rainfall_mm"]),
    }
    producer.send('rainfall-data', key=row["region"], value=event)
    print(f"Sent: {event}")
    time.sleep(0.3)

producer.flush()
print("Done sending rainfall events.")

