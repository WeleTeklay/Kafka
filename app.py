import os
import numpy as np
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Baseline historical rainfall data per region (for realistic relative comparisons)
REGIONAL_BASelines = {
    "Tigray Region": [45.2, 48.0, 42.5, 46.1, 44.0],
    "Amhara Region": [65.0, 70.2, 68.4, 62.1, 66.5],
    "Oromia Region": [80.5, 85.0, 78.2, 82.1, 79.0],
    "Somali Region": [20.1, 18.5, 22.0, 19.4, 21.0],
    "SNNPR": [95.0, 98.2, 92.5, 96.0, 94.1],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Drought Prediction System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 420px; text-align: center; }
        select, input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #0070f3; color: white; border: none; padding: 10px; width: 100%; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0051cc; }
        #result { margin-top: 15px; font-weight: bold; color: #333; text-align: left; font-size: 14px; line-height: 1.5; }
        .chart-container { position: relative; margin-top: 20px; height: 180px; width: 100%; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Drought Predictor</h2>
        <p>Select Region & Enter Recent Rainfall</p>
        
        <select id="region">
            <option value="Tigray Region">Tigray Region</option>
            <option value="Amhara Region">Amhara Region</option>
            <option value="Oromia Region">Oromia Region</option>
            <option value="Somali Region">Somali Region</option>
            <option value="SNNPR">SNNPR</option>
        </select>

        <input type="number" id="rainfall" step="0.1" placeholder="Recent Rainfall in mm">
        <button onclick="predictDrought()">Analyze Region Risk</button>
        
        <div id="result"></div>
        
        <div class="chart-container">
            <canvas id="riskChart"></canvas>
        </div>
    </div>

    <script>
        let myChart = null;

        function updateChart(deficitPct, riskLevel) {
            let ctx = document.getElementById('riskChart').getContext('2d');
            let highVal = (riskLevel === 'High') ? deficitPct : Math.min(deficitPct, 50);
            let lowVal = Math.max(0, 100 - deficitPct);

            if (myChart) { myChart.destroy(); }

            myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Deficit %', 'Normal Baseline %'],
                    datasets: [{
                        data: [deficitPct, lowVal],
                        backgroundColor: [riskLevel === 'High' ? '#d9534f' : '#f0ad4e', '#28a745'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true, max: 100 } },
                    plugins: { legend: { display: false } }
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
            resultDiv.innerText = "Processing analysis...";
            
            try {
                let response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ region: region, rainfall_mm: parseFloat(val) })
                });
                let data = await response.json();
                if(response.ok) {
                    let color = data.risk_level === 'High' ? '#d9534f' : (data.risk_level === 'Medium' ? '#f0ad4e' : '#28a745');
                    
                    resultDiv.innerHTML = `
                        <u><b>${data.region} Analysis</b></u><br>
                        • Historical Avg: ${data.historical_avg_rainfall_mm} mm<br>
                        • Recent Rainfall: ${data.input_rainfall_mm} mm<br>
                        • Deficit: <b>${data.deficit_pct}%</b><br>
                        • Risk Level: <span style="color: ${color}; font-size: 16px;"><b>${data.risk_level} Risk</b></span>
                    `;
                    
                    updateChart(data.deficit_pct, data.risk_level);
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
    region = data.get("region", "Tigray Region")
    recent_rainfall = float(data.get("rainfall_mm", 0.0))

    # Fetch historical baseline for the chosen region
    historical_series = REGIONAL_BASelines.get(region, [50.0, 50.0, 50.0])
    historical_avg = float(np.mean(historical_series))

    # Calculate deficit percentage relative to historical regional average
    if historical_avg > 0:
      deficit_pct = round(
          ((historical_avg - recent_rainfall) / historical_avg) * 100, 1
      )
    else:
      deficit_pct = 0.0

    # Ensure deficit doesn't drop below 0 for excess rainfall
    deficit_pct = max(0.0, deficit_pct)

    # Classify risk based on regional deficit percentage[cite: 1]
    if deficit_pct > 50:
      risk_level = "High"
    elif deficit_pct > 25:
      risk_level = "Medium"
    else:
      risk_level = "Low"

    return jsonify({
        "region": region,
        "historical_avg_rainfall_mm": round(historical_avg, 1),
        "input_rainfall_mm": recent_rainfall,
        "deficit_pct": deficit_pct,
        "risk_level": risk_level,
    })
  except Exception as e:
    return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
  app.run(debug=True, port=5002)
