# Real-Time Drought Analysis & Rainfall Pipeline with Kafka

An end-to-end data pipeline and machine learning application built using **Apache Kafka**, Python, and machine learning models to fetch rainfall data, stream it via producers and consumers, analyze drought conditions, and serve insights through an application interface.

---

## 📁 Project Structure

```text
Kafka/
├── app.py                     # Main application / UI entry point
├── drought_analysis.py        # Core logic for drought analysis and data processing
├── drought_model.pkl          # Trained machine learning model for drought prediction
├── fetch_rainfall.py          # Script to fetch live or historical rainfall data
├── output.json                # Sample or generated JSON output data
├── rainfall.csv               # Dataset containing rainfall records
├── rainfall_batch_consumer.py # Kafka consumer for batch processing rainfall streams
├── rainfall_producer.py       # Kafka producer to stream rainfall data
├── requirements.txt           # Python dependencies
├── train_model.py             # Script used to train the machine learning model
└── vercel.json                # Deployment configuration for Vercel
🚀 Features
Data Ingestion (fetch_rainfall.py): Automatically retrieves rainfall metrics from external sources or APIs.

Streaming Architecture (rainfall_producer.py & rainfall_batch_consumer.py): Utilizes Apache Kafka to publish and consume streaming rainfall telemetry for real-time processing.

Machine Learning (drought_model.pkl & train_model.py): Predicts and classifies drought severity using historical rainfall features.

Analytics Engine (drought_analysis.py): Processes consumer outputs to calculate key environmental metrics and drought indicators.

Application Interface (app.py): Serves the analysis results and model predictions via an interactive application framework.

🛠️ Installation & Prerequisites
Make sure you have Python 3.8+ and a running instance of Apache Kafka (along with ZooKeeper or KRaft) installed on your local machine or server.

Clone the repository:

Bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name/Kafka
Install dependencies:

Bash
pip install -r requirements.txt
⚙️ Usage & Running the Pipeline
To run the pipeline locally, execute the components in the following order:

Start your Kafka broker/server.

Run the Rainfall Producer:
Streams rainfall records to your Kafka topic.

Bash
python rainfall_producer.py
Run the Batch Consumer:
Consumes the streamed messages and logs/saves them for downstream analysis.

Bash
python rainfall_batch_consumer.py
Execute Drought Analysis:
Processes the aggregated data to evaluate drought conditions.

Bash
python drought_analysis.py
Launch the Application:

Bash
python app.py
🤖 Model Training
If you need to retrain the machine learning model using updated datasets (rainfall.csv):

Bash
python train_model.py
This will generate and overwrite the serialized drought_model.pkl file.

📦 Deployment
This repository includes a vercel.json configuration file, making it easy to deploy the frontend or serverless components to Vercel.

📄 License
This project is licensed under the MIT License.
