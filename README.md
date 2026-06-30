# Therma-Shield: AI-Powered Urban Heat Island Mitigation Platform

Therma-Shield is a state-of-the-art decision support dashboard and Climate Intelligence platform designed for municipalities, urban planners, and environmental agencies. The system ingests satellite imagery and sensor networks, isolates **Urban Heat Island (UHI)** hotspots, forecasts climate warming trends using Machine Learning (Scikit-Learn), and generates physical mitigation strategies through an AI Recommendation Engine.

---

## Key Features

1. **Environmental Feature Extraction**: Auto-calculates Land Surface Temperature (LST), Normalized Difference Vegetation Index (NDVI), and Normalized Difference Built-up Index (NDBI) from multi-spectral bands (Landsat 8/9, Sentinel-2).
2. **Machine Learning Predictor**: Automatically trains and evaluates RandomForest vs. GradientBoosting Regressors on spatial profiles to predict temperature risks and 5-year warming progression.
3. **AI Recommendation Engine**: Applies multi-layered environmental planning rules to suggest tailored interventions (green infrastructure, cool roof coatings, pocket parks, Miyawaki forests) complete with cost, cooling offset, carbon reduction, and priority levels.
4. **Natural Language AI Assistant**: Context-aware local chat assistant pre-loaded with climatology data and integrated directly with the active dataset database to answer queries in real-time.
5. **Interactive GIS Mapping**: Dark-mode customized Leaflet map supporting spatial layer toggles, district GeoJSON polygons, and popup analytics cards.
6. **Executive PDF Reports**: Dynamic, beautifully styled PDF compiler (ReportLab) to download full climate diagnostics, matrices, and planning suggestions.
7. **Admin Dashboard**: Run database deletes, retrain model weights, and adjust temperature trigger boundaries dynamically.

---

## Technology Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, React-Leaflet, Chart.js, Axios
- **Backend**: FastAPI, SQLite (SQLAlchemy ORM), Uvicorn
- **Machine Learning & GIS**: Scikit-Learn, NumPy, Pandas, Rasterio, GeoPandas, Pillow, ReportLab

---

## Project Structure

```
urban-heat-island-platform/
├── backend/
│   ├── main.py                     # FastAPI server entry point
│   ├── requirements.txt             # Python dependencies
│   ├── database.py                 # SQLite SQLAlchemy config
│   ├── models.py                   # DB Schemas (Hotspots, Suggestions, Chat)
│   ├── routes/
│   │   ├── upload.py               # File uploads & background pipeline
│   │   ├── predict.py              # ML training and evaluation
│   │   ├── recommend.py            # AI recommendations
│   │   ├── report.py               # PDF report generator
│   │   ├── dashboard.py            # Aggregated statistics
│   │   ├── map.py                  # Leaflet layers & GeoJSON
│   │   ├── history.py              # History manager
│   │   └── chat.py                 # Chat assistant endpoints
│   ├── ml/
│   │   └── pipeline.py             # Feature engineering & ML training
│   ├── recommendation_engine/
│   │   └── engine.py               # AI mitigation logic
│   └── utils/
│       ├── geo_processor.py        # Geospatial image/vector parser
│       ├── assistant.py            # NLP Chat assistant logic
│       └── generate_samples.py     # Sample dataset generator
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── index.css               # Themes, glassmorphic styling
│       ├── App.jsx                 # App shell and state transitions
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── Dashboard.jsx       # Chart widgets
│       │   ├── UploadPanel.jsx     # Drag & drop uploader
│       │   ├── HeatMap.jsx         # GIS React-Leaflet map
│       │   ├── Recommendations.jsx # Suggestions grid
│       │   ├── AIAssistant.jsx     # Chat bubbles and suggestions
│       │   ├── Reports.jsx         # PDF compiler
│       │   └── Settings.jsx        # Model calibration parameters
│       └── utils/
│           └── api.js              # Axios connection
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate sample datasets:
   ```bash
   python utils/generate_samples.py
   ```
4. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *API will be active at `http://localhost:8000` (Docs available at `/docs`).*

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
   *Dashboard will be active at `http://localhost:5173`.*

---

## Future Scope

1. **Earth Engine Integration**: Live fetch APIs to extract landsat bands dynamically using coordinates.
2. **Convolutional Neural Networks (CNNs)**: Implement segmentation models (U-Net) to automatically segment green canopies and concrete roads from raw visual bands.
3. **Advanced Microclimate Modeling**: Incorporate wind dynamics and elevation profiles to calculate urban canyon ventilation layouts.

---

## License
MIT License. Created as part of the Geospatial AI Platform portfolio.
