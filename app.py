import os
import joblib
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Load your trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
try:
  model = joblib.load(MODEL_PATH)
except Exception as e:
  model = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Drought Prediction System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 400px; text-align: center; }
        select, input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #0070f3; color: white; border: none; padding: 10px; width: 100%; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0051cc; }
        #result { margin-top: 15px; font-weight: bold; color: #333; }
        .chart-container { position: relative; margin-top: 20px; height: 200px; width: 100%; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Drought Predictor</h2>
        <p>Select Region & Enter Rainfall</p>
        
        <select id="region">
            <option value="Tigray Region">Tigray Region</option>
            <option value="Amhara Region">Amhara Region</option>
            <option value="Oromia Region">Oromia Region</option>
            <option value="Somali Region">Somali Region</option>
            <option value="SNNPR">SNNPR</option>
        </select>

        <input type="number" id="rainfall" step="0.1" placeholder="Rainfall in mm (e.g. 4.5)">
        <button onclick="predictDrought()">Predict Risk & View Chart</button>
        
        <div id="result"></div>
        
        <div class="chart-container">
            <canvas id="riskChart"></canvas>
        </div>
    </div>

    <script>
        let myChart = null;

        function updateChart(confidence, isHighRisk) {
            let ctx = document.getElementById('riskChart').getContext('2d');
            let highRiskVal = isHighRisk ? confidence * 100 : (1 - confidence) * 100;
            let lowRiskVal = 100 - highRiskVal;

            if (myChart) {
                myChart.destroy();
            }

            myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['High/Medium Risk', 'Low Risk / Normal'],
                    datasets: [{
                        label: 'Probability (%)',
                        data: [highRiskVal, lowRiskVal],
                        backgroundColor: ['#d9534f', '#28a745'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        async function predictDrought() {
            let region = document.getElementById('region').value;
            let val = document.getElementById('rainfall').value;
            let resultDiv = document.getElementById('result');
            
            if(!val) {
                resultDiv.innerText = "Please enter a rainfall value!";
                return;
            }
            resultDiv.innerText = "Processing...";
            
            try {
                let response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rainfall_mm: parseFloat(val) })
                });
                let data = await response.json();
                if(response.ok) {
                    let color = (data.drought_prediction === 1) ? "#d9534f" : "#28a745";
                    let confPercent = (data.confidence * 100).toFixed(1);
                    
                    resultDiv.innerHTML = `<u>${region}</u><br>Risk: <span style="color: ${color};">${data.risk_status}</span><br>Confidence: ${confPercent}%`;
                    
                    updateChart(data.confidence, data.drought_prediction === 1);
                } else {
                    resultDiv.innerText = "Prediction failed.";
                }
            } catch (err) {
                resultDiv.innerText = "Error connecting to server.";
            }
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML_TEMPLATE)


@app.route("/predict", methods=["POST"])
def predict():
  try:
    data = request.get_json()
    rainfall = float(data.get("rainfall_mm", 0.0))

    if model is not None:
      prediction = model.predict([[rainfall]])[0]
      if hasattr(model, "predict_proba"):
        confidence = float(max(model.predict_proba([[rainfall]])[0]))
      else:
        confidence = 1.0
    else:
      prediction = 1 if rainfall < 5.0 else 0
      confidence = 0.95 if rainfall < 5.0 else 0.88

    risk_status = (
        "High/Medium Risk" if int(prediction) == 1 else "Low Risk / Normal"
    )

    return jsonify({
        "input_rainfall_mm": rainfall,
        "drought_prediction": int(prediction),
        "risk_status": risk_status,
        "confidence": confidence,
    })
  except Exception as e:
    return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
  app.run(debug=True, port=5002)
