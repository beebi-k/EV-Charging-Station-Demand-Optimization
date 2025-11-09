import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from geopy.geocoders import Nominatim

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))
MODEL_DIR = os.path.join(BASE_DIR, "model")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

model_path = os.path.join(MODEL_DIR, "ev_demand_model.pkl")
scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")

model = joblib.load(model_path) if os.path.exists(model_path) else None
scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

geolocator = Nominatim(user_agent="premium_ev_app")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if data["username"] == "admin@example.com" and data["password"] == "password123":
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"success": True})

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    place = data["place_name"]
    type_encoded = data.get("type_encoded", 0)

    try:
        loc = geolocator.geocode(place, timeout=10)
        if not loc:
            raise Exception("Not found → Using fallback")
        lat, lon = loc.latitude, loc.longitude
        resolved = loc.address
    except:
        # Offline fallback location: India
        lat, lon = 20.5937, 78.9629
        resolved = f"Fallback: {place}"

    if model and scaler:
        X = [[lat, lon, int(type_encoded)]]
        score = round(float(model.predict(scaler.transform(X))[0]), 2)
        note = "✅ Real ML model used"
    else:
        score = round(((abs(lat) + abs(lon)) % 100) + int(type_encoded) * 3, 2)
        note = "⚠ Offline fallback (train model.py for real predictions)"

    return jsonify({
        "location_name": resolved,
        "latitude": lat,
        "longitude": lon,
        "predicted_demand_score": score,
        "note": note
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    msg = request.json["message"].lower()
    if "battery" in msg:
        reply = "🔋 Keep battery between 20%-80%. Avoid daily DC fast charging."
    elif "charger" in msg:
        reply = "⚡ Try DC Fast chargers in high-demand urban zones!"
    elif "hello" in msg:
        reply = "👋 Hi! Ask me about EV battery tips!"
    else:
        reply = "😊 Try: 'battery tips' or 'best charger type'"
    return jsonify({"reply": reply})

if __name__ == "__main__":
    print("✅ Server Running: http://127.0.0.1:5000/")
    print("Serving frontend from:", FRONTEND_DIR)
    app.run(host="0.0.0.0", port=5000, debug=True)
