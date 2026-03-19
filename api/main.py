from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import json
import os

# ── Cargar modelo ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'model.pkl')
META_PATH  = os.path.join(BASE_DIR, '..', 'model', 'metadata.json')

model = joblib.load(MODEL_PATH)
with open(META_PATH, encoding='utf-8') as f:
    metadata = json.load(f)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="API de Predicción de Alquiler – Ecuador",
    description="Predice el precio de alquiler de un inmueble en Ecuador usando XGBoost.",
    version="1.0.0",
)

# ── Esquemas ───────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    provincia: str = Field(..., example="Pichincha")
    lugar: str = Field(..., example="Quito")
    num_dormitorios: float = Field(..., ge=0, example=3)
    num_banos: float = Field(..., ge=0, example=2)
    area: float = Field(..., gt=0, example=120)
    num_garages: float = Field(..., ge=0, example=1)

class PredictResponse(BaseModel):
    prediction: float

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/", summary="Health check")
def root():
    return {"status": "ok", "message": "API de predicción de alquiler en Ecuador"}

@app.get("/metadata", summary="Valores válidos para provincia y lugar")
def get_metadata():
    return metadata

@app.post("/predict", response_model=PredictResponse, summary="Predice el precio de alquiler")
def predict(data: PredictRequest):
    # Si el lugar no está en el modelo, usar 'Otro'
    lugar_norm = data.lugar if data.lugar in metadata['lugares'] else 'Otro'

    X = pd.DataFrame([{
        'Provincia': data.provincia,
        'Lugar': lugar_norm,
        'Num. dormitorios': data.num_dormitorios,
        'Num. banos': data.num_banos,
        'Area': data.area,
        'Num. garages': data.num_garages,
    }])

    try:
        pred = float(model.predict(X)[0])
        pred = max(0.0, round(pred, 2))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

    return PredictResponse(prediction=pred)
