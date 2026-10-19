# Real-Time Rainfall Data Pipeline for Drought Early Warning

A small end-to-end data engineering project. It pulls daily rainfall data from a public API, streams it through **Apache Kafka**, stores it in **HDFS**, runs a batch analysis to estimate drought risk per region, and shows the result on a web dashboard.

**Live demo:** https://kafka-eight.vercel.app

## What it does

1. **Ingest:** downloads daily rainfall for four Ethiopian regions (Tigray, Amhara, Oromia, SNNPR) from the [Open-Meteo](https://open-meteo.com/) archive API and sums it into 5-day totals.
2. **Stream:** a Kafka producer sends each record as a JSON event to a topic.
3. **Store:** a Kafka consumer collects events into small batches and writes them to HDFS as JSON Lines files.
4. **Analyse:** a batch job reads the raw files from HDFS and calculates a drought risk level for each region.
5. **Serve:** a Flask app and a Chart.js dashboard show the result.

## Architecture

```
Open-Meteo API
      |
fetch_rainfall.py  -->  rainfall.csv
                              |
                    rainfall_producer.py
                              |
                  Kafka topic: rainfall-data
                              |
                  rainfall_batch_consumer.py
                              |
          HDFS: /drought-data/raw/rainfall/*.json
                              |
                    drought_analysis.py
                              |
                         output.json
                              |
                  app.py (Flask) + dashboard
```

## Files

| File | Purpose |
|---|---|
| `fetch_rainfall.py` | Calls the Open-Meteo API for each region (1 June to 31 July 2026), groups days into 5-day totals, and writes `rainfall.csv` (52 rows). |
| `rainfall.csv` | The collected data: `region`, `date`, `rainfall_mm`. |
| `rainfall_producer.py` | Reads the CSV and sends each row to the `rainfall-data` topic. Messages are keyed by region and sent with `acks='all'`. |
| `rainfall_batch_consumer.py` | Reads from the topic in the consumer group `rainfall-batch-writer`. Writes a batch to HDFS when it holds 5 messages or 15 seconds have passed. Stops after about 20 seconds with no new data. |
| `drought_analysis.py` | Reads all batch files from HDFS and writes `output.json` (see below). |
| `output.json` | The analysis result for each region. |
| `app.py` | Flask app. Serves the dashboard and a `/predict` endpoint that reads `output.json`. |
| `vercel.json` | Deployment settings for Vercel. |
| `train_model.py`, `drought_model.pkl` | An experimental Random Forest classifier. It is not used by the pipeline or the dashboard. |

## How the drought risk is calculated

For each region, `drought_analysis.py` does the following:

- **Historical average:** the mean rainfall across all 5-day totals in the data.
- **Recent average:** the mean of the last 3 totals.
- **Deficit %:** `(historical - recent) / historical * 100`.
- **Next-period estimate:** a straight-line trend fitted to the 5-day totals.
- **Risk level:** `High` if the deficit is above 50%, `Medium` if above 25%, otherwise `Low`.

The baseline comes from the two months of data collected here, not from a long-term climate record. Treat the risk level as a demonstration, not a forecast.

Example entry in `output.json`:

```json
{
  "region": "Tigray",
  "recent_avg_rainfall_mm": 9.8,
  "historical_avg_rainfall_mm": 8.6,
  "deficit_pct": -13.7,
  "predicted_next_period_mm": 24.5,
  "risk_level": "Low"
}
```

## Requirements

- Python 3.8 or newer
- Apache Kafka running at `localhost:9092`
- HDFS with WebHDFS enabled at `localhost:9870`

```bash
pip install -r requirements.txt
```

## Run the pipeline

Run each step from the project folder.

**1. Create the Kafka topic and the HDFS folder (once).**

```bash
kafka-topics.sh --create --topic rainfall-data \
  --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

hdfs dfs -mkdir -p /drought-data/raw/rainfall
```

**2. Collect the data.**

```bash
python fetch_rainfall.py
```

**3. Start the consumer first, then the producer (in a second terminal).**

```bash
python rainfall_batch_consumer.py
python rainfall_producer.py
```

**4. Analyse the data stored in HDFS.**

```bash
python drought_analysis.py
```

**5. Start the dashboard.**

```bash
python app.py
```

Open http://localhost:5002, choose a region, and click **Fetch Pipeline Analysis**. You can also type a rainfall value to see how the risk level changes.

## Configuration

Before running, check these values:

- `HDFS_USER` in `rainfall_batch_consumer.py` and `drought_analysis.py` (set to `hp`). Change it to your own HDFS username.
- The Kafka address (`localhost:9092`) and the HDFS address (`http://localhost:9870`) are written directly in the scripts.
- `REGIONS`, `START_DATE`, and `END_DATE` in `fetch_rainfall.py` control which data is collected.

## About the Vercel deployment

The live demo only runs `app.py`. It reads the `output.json` file stored in this repository. Kafka and HDFS are not running there. To see new results online, run the pipeline locally and commit the updated `output.json`.

## Tech stack

Python, Apache Kafka (`kafka-python`), HDFS (`hdfs` client), Pandas, NumPy, Scikit-learn, Flask, Chart.js, Open-Meteo API, Vercel.

