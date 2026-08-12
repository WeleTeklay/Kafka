cat > ~/drought_prediction/fetch_rainfall.py << 'EOF'
import requests
import csv

REGIONS = {
    "Tigray": (13.4967, 39.4753),   # Mekelle
    "Amhara": (11.5936, 37.3908),   # Bahir Dar
    "Oromia": (8.5400, 39.2700),    # Adama
    "SNNPR": (7.0504, 38.4955),     # Hawassa
}

START_DATE = "2026-06-01"
END_DATE = "2026-07-31"

def fetch_region(lat, lon):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return list(zip(data["daily"]["time"], data["daily"]["precipitation_sum"]))

def pentad_aggregate(daily_rows):
    buckets = []
    for i in range(0, len(daily_rows), 5):
        chunk = daily_rows[i:i + 5]
        if not chunk:
            continue
        end_date = chunk[-1][0]
        total_mm = sum(v if v is not None else 0.0 for _, v in chunk)
        buckets.append((end_date, round(total_mm, 2)))
    return buckets

def main():
    rows = []
    for region, (lat, lon) in REGIONS.items():
        print(f"Fetching {region}...")
        daily = fetch_region(lat, lon)
        for pentad_date, rainfall_mm in pentad_aggregate(daily):
            rows.append({"region": region, "date": pentad_date, "rainfall_mm": rainfall_mm})

    with open("rainfall.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["region", "date", "rainfall_mm"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to rainfall.csv")

if __name__ == "__main__":
    main()
EOF
