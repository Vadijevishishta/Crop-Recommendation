import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("Crop recommendation dataset.csv")

X = df[["N","P","K","TEMP","RELATIVE_HUMIDITY","SOIL_PH"]]
y = df["CROPS"]

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

joblib.dump(
    {"model": model, "features": X.columns.tolist()},
    "crop_model.pkl"
)

print("✅ Model trained successfully")
print("🌾 Crops:", len(model.classes_))
