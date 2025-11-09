# backend/train_model.py
import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import joblib

# <- EDIT only if your CSV path is different
CSV_PATH = r"C:\Users\kalag\OneDrive\Desktop\Electric V\backend\ev-charging-stations-india-cleaned.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

TARGET_COL = "demand_score"  # change if your csv has a different column name

print("Loading CSV from:", CSV_PATH)
df = pd.read_csv(CSV_PATH)

# normalize possible misspelling
if "lattitude" in df.columns and "latitude" not in df.columns:
    df.rename(columns={"lattitude": "latitude"}, inplace=True)

# ensure numeric lat/lon
df["latitude"] = pd.to_numeric(df.get("latitude"), errors="coerce")
df["longitude"] = pd.to_numeric(df.get("longitude"), errors="coerce")
df = df.dropna(subset=["latitude", "longitude"])

if "type" not in df.columns:
    df["type"] = 0

if TARGET_COL not in df.columns:
    print(f"Warning: {TARGET_COL} not found. Creating synthetic target.")
    df[TARGET_COL] = ((df["latitude"].abs() + df["longitude"].abs()) % 100) + df["type"] * 3

X = df[["latitude", "longitude", "type"]].values
y = df[TARGET_COL].values

print("Training on rows:", len(X))
scaler = MinMaxScaler()
Xs = scaler.fit_transform(X)

model = LinearRegression()
model.fit(Xs, y)

joblib.dump(model, os.path.join(MODEL_DIR, "ev_demand_model.pkl"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

print("Saved model & scaler to:", MODEL_DIR)
