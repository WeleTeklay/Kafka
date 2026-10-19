# Real-Time Drought Analysis & Rainfall Pipeline with Kafka

An end-to-end data pipeline and machine learning application built using **Apache Kafka**, Python, and machine learning models to fetch rainfall data, stream it via producers and consumers, analyze drought conditions, and serve insights through an application interface.

---

## 📁 Project Structure

Kafka/  <br>
├── app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Ah, I see! Markdown treats single line breaks inside paragraphs as spaces, so the tree structure collapsed into a messy single paragraph. 

To fix that so it copies as regular text (not a black code block) but keeps its vertical line-by-line tree layout, you need to use **double spaces at the end of each line** or use **HTML line breaks (`<br>`)**. 

Here is the clean version ready for you to copy:

```markdown
# Real-Time Drought Analysis & Rainfall Pipeline with Kafka

An end-to-end data pipeline and machine learning application built using **Apache Kafka**, Python, and machine learning models to fetch rainfall data, stream it via producers and consumers, analyze drought conditions, and serve insights through an application interface.

---

## 📁 Project Structure

Kafka/<br>
├── app.py                     # Main application / UI entry point<br>
├── drought_analysis.py        # Core logic for drought analysis and data processing<br>
├── drought_model.pkl          # Trained machine learning model for drought prediction<br>
├── fetch_rainfall.py          # Script to fetch live or historical rainfall data<br>
├── output.json                # Sample or generated JSON output data<br>
├── rainfall.csv               # Dataset containing rainfall records<br>
├── rainfall_batch_consumer.py # Kafka consumer for batch processing rainfall streams<br>
├── rainfall_producer.py       # Kafka producer to stream rainfall data<br>
├── requirements.txt           # Python dependencies<br>
├── train_model.py             # Script used to train the machine learning model<br>
└── vercel.json                # Deployment configuration for Vercel

---

## 🚀 Features

* **Data Ingestion (`fetch_rainfall.py`):** Automatically retrieves rainfall metrics from external sources or APIs.
* **Streaming Architecture (`rainfall_producer.py` & `rainfall_batch_consumer.py`):** Utilizes Apache Kafka to publish and consume streaming rainfall telemetry for real-time processing.
* **Machine Learning (`drought_model.pkl` & `train_model.py`):** Predicts and classifies drought severity using historical rainfall features.
* **Analytics Engine (`drought_analysis.py`):** Processes consumer outputs to calculate key environmental metrics and drought indicators.
* **Application Interface (`app.py`):** Serves the analysis results and model predictions via an interactive application framework.

---

## 🛠️ Installation & Prerequisites

Make sure you have **Python 3.8+** and a running instance of **Apache Kafka** (along with ZooKeeper or KRaft) installed on your local machine or server.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name/Kafka
