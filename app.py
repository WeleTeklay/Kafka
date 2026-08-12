from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model when the app starts
model = joblib.load("drought_model.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Expecting JSON payload: {"rainfall_mm": 5.2}
    rainfall = float(data.get('rainfall_mm', 0.0))
    features = np.array([[rainfall]])
    
    prediction = model.predict(features)
    probability = model.predict_proba(features)
    
    risk_status = "High/Medium Risk" if prediction[0] == 1 else "Low Risk"
    
    return jsonify({
        "input_rainfall_mm": rainfall,
        "drought_prediction": int(prediction[0]),
        "risk_status": risk_status,
        "confidence": float(np.max(probability))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
