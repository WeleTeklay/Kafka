import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load your collected data
df = pd.read_csv("rainfall.csv")

# 2. Feature Engineering & Target Labeling
# Let's define a target: if rainfall is below 6.0 mm, label it as drought risk (1), else (0)
df['is_drought'] = (df['rainfall_mm'] < 6.0).astype(int)

# Features and Target
X = df[['rainfall_mm']]
y = df['is_drought']

# 3. Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

# 4. Save the trained model artifact
joblib.dump(model, "drought_model.pkl")
print("Model successfully trained and saved as drought_model.pkl")
