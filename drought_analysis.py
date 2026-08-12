
from hdfs import InsecureClient
import json
import numpy as np
from collections import defaultdict
import datetime

HDFS_DIR = '/drought-data/raw/rainfall'
HDFS_USER = 'hp'  # change to your actual username

client = InsecureClient('http://localhost:9870', user=HDFS_USER)

by_region = defaultdict(list)

filenames = client.list(HDFS_DIR)
for fname in filenames:
    with client.read(f"{HDFS_DIR}/{fname}", encoding='utf-8') as reader:
        for line in reader:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            by_region[record["region"]].append((record["date"], record["rainfall_mm"]))

def classify_risk(deficit_pct):
    if deficit_pct > 50:
        return "High"
    elif deficit_pct > 25:
        return "Medium"
    else:
        return "Low"

output_regions = []
for region, series in by_region.items():
    series.sort(key=lambda x: x[0])
    values = [v for _, v in series]

    historical_avg = float(np.mean(values))
    recent_values = values[-3:] if len(values) >= 3 else values
    recent_avg = float(np.mean(recent_values))

    x = np.arange(len(values))
    if len(values) >= 2:
        slope, intercept = np.polyfit(x, values, 1)
        predicted_next = float(slope * len(values) + intercept)
    else:
        predicted_next = recent_avg

    deficit_pct = round(((historical_avg - recent_avg) / historical_avg) * 100, 1) if historical_avg > 0 else 0.0
    risk_level = classify_risk(deficit_pct)

    output_regions.append({
        "region": region,
        "recent_avg_rainfall_mm": round(recent_avg, 1),
        "historical_avg_rainfall_mm": round(historical_avg, 1),
        "deficit_pct": deficit_pct,
        "predicted_next_period_mm": round(predicted_next, 1),
        "risk_level": risk_level,
    })

output = {
    "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    "regions": output_regions,
}

with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))

