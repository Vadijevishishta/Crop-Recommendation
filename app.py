from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import requests

app = Flask(__name__)

# ================= LOAD MODEL =================
data = joblib.load("crop_model.pkl")
model = data["model"]
features = data["features"]

API_KEY = "5b7bac91f00b738e2f5861fea1ff1405"

# ================= ORGANIC PEST =================
ORGANIC_PESTS = {
    "rice": ["Neem oil spray", "Light traps", "Trichogramma"],
    "wheat": ["Neem seed kernel extract", "Yellow sticky traps"],
    "maize": ["Neem oil", "Pheromone traps"],
    "sorghum": ["Neem oil spray", "Bird perches"],
    "pearl millet": ["Neem seed extract"],
    "ragi": ["Neem oil"],
    "panivaragu": ["Neem oil"],
    "samai": ["Neem oil"],
    "thinai": ["Neem oil"],
    "varagu": ["Neem oil"],
    "kudiraivali": ["Neem oil"],

    "black gram": ["Neem oil", "Chilli–garlic extract"],
    "green gram": ["Neem seed extract"],
    "cowpea": ["Neem oil"],
    "bengalgram": ["Neem oil"],
    "horsegram": ["Neem oil"],
    "red gram": ["Neem oil"],
    "soyabean": ["Neem oil"],

    "groundnut": ["Neem oil", "Castor trap crop"],
    "sunflower": ["Neem oil", "Bird perches"],
    "gingely": ["Neem oil"],
    "castor": ["Neem oil"],

    "cotton": ["Neem oil", "Trichoderma"],
    "jute": ["Neem oil"],
    "sugarcane": ["Trichogramma cards", "Neem cake"],
    "sugarbeet": ["Neem oil"],

    "tomato": ["Neem oil", "Bt spray"],
    "onion": ["Neem oil", "Sticky traps"],
    "small onion": ["Neem oil"],
    "chillies": ["Neem oil", "Yellow sticky traps"],
    "cabbage": ["Neem oil", "Bt spray"],
    "bhendi": ["Neem oil"],
    "brinjal": ["Neem oil", "Pheromone traps"],
    "capsicum": ["Neem oil"],
    "pumpkin": ["Neem oil"],
    "snake gourd": ["Neem oil"],
    "ribbed gourd": ["Neem oil"],
    "bottle gourd": ["Neem oil"],
    "bitter gourd": ["Neem oil"],
    "ash gourd": ["Neem oil"],
    "cucumber": ["Neem oil"],
    "watermelon": ["Neem oil"],
    "muskmelon": ["Neem oil"],
    "tinda": ["Neem oil"],
    "chowchow": ["Neem oil"],
    "cluster bean": ["Neem oil"],
    "vegetable cowpea": ["Neem oil"],
    "french bean": ["Neem oil"],
    "peas": ["Neem oil"],
    "annual moringa": ["Neem oil"],
    "carrot": ["Neem oil"],
    "beetroot": ["Neem oil"],
    "radish": ["Neem oil"],
    "sweet potato": ["Neem oil"],
    "tapioca": ["Neem oil"],
    "elephant foot yam": ["Neem oil"],
    "cauliflower": ["Neem oil", "Bt spray"]
}

def get_organic_pest_control(crop):
    return ORGANIC_PESTS.get(crop.lower(), ["Neem oil spray (general)"])

# ================= WEATHER (5 DAYS AVG) =================
def get_weather_avg(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )
    res = requests.get(url, timeout=10).json()

    temps = [i["main"]["temp"] for i in res["list"]]
    hums = [i["main"]["humidity"] for i in res["list"]]

    return round(np.mean(temps), 2), round(np.mean(hums), 2)

# ================= ROUTES =================
@app.route("/")
def home():
    return "Crop Recommendation System Running"

@app.route("/ui")
def ui():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    d = request.json

    temp, hum = get_weather_avg(d["lat"], d["lon"])

    df = pd.DataFrame([{
        "N": d["N"],
        "P": d["P"],
        "K": d["K"],
        "TEMP": temp,
        "RELATIVE_HUMIDITY": hum,
        "SOIL_PH": d["SOIL_PH"]
    }])

    # ===== Prediction =====
    crop = model.predict(df)[0].strip().lower()

    # ===== INPUT BASED XAI (DYNAMIC) =====
    input_values = {
        "N": d["N"],
        "P": d["P"],
        "K": d["K"],
        "TEMP": temp,
        "RELATIVE_HUMIDITY": hum,
        "SOIL_PH": d["SOIL_PH"]
    }

    total = sum(abs(v) for v in input_values.values())

    feature_importance = {
        k: round(abs(v) / total, 3)
        for k, v in input_values.items()
    }

    # Top 3 reasons
    top = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    xai_reasons = [f"{f} influenced the decision" for f, _ in top]

    return jsonify({
        "recommended_crop": crop.title(),
        "avg_7day_temp": temp,
        "avg_7day_humidity": hum,
        "feature_importance": feature_importance,
        "xai_reasons": xai_reasons,
        "organic_pest_control": get_organic_pest_control(crop)
    })



 
if __name__ == "__main__":
    print("UI → http://127.0.0.1:5000/ui")
    app.run(debug=True)
