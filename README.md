# 🏠 Predicción de Precios de Alquiler en Ecuador

API REST y notebooks de ciencia de datos para predecir precios de alquiler de inmuebles en Ecuador.  
Desarrollado como prueba técnica para el Laboratorio de Ciencia de Datos ADA – EPN.

---

## 📁 Estructura del Repositorio

```
.
├── data/
│   ├── real_state_ecuador_dataset.csv   # Dataset original
│   └── real_state_clean.csv             # Dataset procesado (generado por el notebook EDA)
├── notebooks/
│   ├── 01_EDA.ipynb                     # Análisis exploratorio de datos
│   └── 02_ML.ipynb                      # Modelado de Machine Learning
├── model/
│   ├── model.pkl                        # Modelo serializado (XGBoost pipeline)
│   └── metadata.json                    # Lugares y provincias válidos
├── api/
│   ├── main.py                          # API FastAPI
│   └── requirements.txt                 # Dependencias Python
├── Dockerfile                           # Contenedor Docker
├── render.yaml                          # Configuración de despliegue en Render
└── README.md
```

---

## 🚀 URL Pública de la API

```
https://ecuador-rental-api.onrender.com
```

### Health check
```bash
curl https://ecuador-rental-api.onrender.com/
```

---

## 📡 Uso de la API

### Endpoint principal

**`POST /predict`**

Predice el precio mensual de alquiler (USD) de un inmueble.

#### Request

```bash
curl -X POST "https://ecuador-rental-api.onrender.com/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "provincia": "Pichincha",
       "lugar": "Quito",
       "num_dormitorios": 3,
       "num_banos": 2,
       "area": 120,
       "num_garages": 1
     }'
```

#### Response

```json
{
  "prediction": 588.73
}
```

### Otros endpoints

| Método | Endpoint      | Descripción                              |
|--------|---------------|------------------------------------------|
| GET    | `/`           | Health check                             |
| GET    | `/metadata`   | Lista de provincias y lugares válidos    |
| GET    | `/docs`       | Documentación interactiva (Swagger UI)   |

### Parámetros de entrada

| Campo            | Tipo   | Descripción                   | Ejemplo      |
|------------------|--------|-------------------------------|--------------|
| `provincia`      | string | Provincia del inmueble        | `"Pichincha"` |
| `lugar`          | string | Ciudad o sector               | `"Quito"`    |
| `num_dormitorios`| float  | Número de dormitorios         | `3`          |
| `num_banos`      | float  | Número de baños               | `2`          |
| `area`           | float  | Área en m²                    | `120`        |
| `num_garages`    | float  | Número de garajes             | `1`          |

> **Nota:** Si el `lugar` no está en el dataset de entrenamiento, el modelo lo trata como `"Otro"` internamente.

---

## 🛠️ Ejecución Local

### Con Python

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/adalab-rental-prediction.git
cd adalab-rental-prediction

# 2. Instalar dependencias
pip install -r api/requirements.txt

# 3. Iniciar la API
uvicorn api.main:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`.

### Con Docker

```bash
docker build -t ecuador-rental-api .
docker run -p 8000:8000 ecuador-rental-api
```

### Ejecutar notebooks

```bash
pip install jupyter xgboost scikit-learn pandas matplotlib seaborn
cd notebooks
jupyter notebook
```

Ejecutar en orden: `01_EDA.ipynb` → `02_ML.ipynb`

---

## 🧠 Descripción de la Solución

### 1. Procesamiento de Datos (`01_EDA.ipynb`)

- **Normalización de `Lugar`**: se extrajo la ciudad del formato `"Provincia, ..., Ciudad, Ecuador"` mediante parsing de strings y se corrigieron variantes ortográficas (`Sangolqui` → `Sangolquí`, códigos postales de Quito, etc.).
- **Valores faltantes**: imputados con la mediana por ciudad; si no hay datos en esa ciudad, con la mediana global.
- **Outliers**: se eliminó el 1% superior de precios (> p99) para reducir el impacto de valores extremos atípicos.
- **Tipo de Precio por Lugar**: clasificación en `Económico` / `Medio` / `Lujo` usando los cuartiles Q1 y Q3 **dentro de cada ciudad** (precio relativo al mercado local).

### 2. Modelado de Machine Learning (`02_ML.ipynb`)

Se compararon cuatro algoritmos de regresión:

| Modelo            | MAE (USD) | R²     |
|-------------------|-----------|--------|
| Ridge             | ~548      | negativo |
| RandomForest      | ~361      | 0.27   |
| GradientBoosting  | ~377      | 0.04   |
| **XGBoost**       | **~373**  | **0.18** |

**Modelo seleccionado: XGBoost** (`XGBRegressor`)

**Justificación:**
- Obtiene buen balance MAE/R² en datos tabulares pequeños.
- Maneja nativamente variables categóricas codificadas y valores atípicos residuales.
- No requiere normalización de features numéricas.
- Con validación cruzada 5-fold logra **MAE ≈ $297 ± $44** y **R² ≈ 0.58 ± 0.21**.

> La diferencia entre CV y test set se debe al tamaño reducido del dataset (496 registros) y a la alta concentración de muestras en Quito (~75% del total).

### 3. API REST (FastAPI)

- Framework: **FastAPI** con validación automática de esquemas via Pydantic.
- El modelo se carga en memoria al iniciar el servidor (`joblib`).
- Lugares desconocidos son mapeados a `"Otro"` para evitar errores de encoding.
- Documentación automática en `/docs` (Swagger UI).

---

## 📊 Análisis Destacados

- **75% de las propiedades** se encuentran en Pichincha (principalmente Quito).
- La **mediana global** de precio es $500 USD; el promedio es $776 (sesgado por propiedades de lujo).
- **Correlación Área–Precio**: baja correlación de Pearson (-0.03) debido a outliers; la relación es positiva para el rango intercuartílico.
- **Premium por habitación**: el salto de 2→3 dormitorios genera el mayor incremento de precio (+67% en promedio).

---

## 🧪 Ejemplo con curl

```bash
curl -X POST "https://ecuador-rental-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"provincia":"Guayas","lugar":"Guayaquil","num_dormitorios":2,"num_banos":1,"area":75,"num_garages":0}'
```

---

## 📦 Dependencias principales

- Python 3.11
- FastAPI 0.111
- scikit-learn 1.4
- XGBoost 2.0
- pandas 2.2
- joblib 1.4
