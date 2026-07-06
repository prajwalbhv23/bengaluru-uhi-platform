# Therma-Shield: AI-Powered Urban Heat Island Mitigation Platform

Therma-Shield is a production-ready, interactive geospatial decision support system and Climate Intelligence platform designed for municipalities, urban planners, and environmental agencies. The platform ingests satellite imagery and tabular sensor data, maps **Urban Heat Island (UHI)** hotspots, forecasts climate warming trends using Machine Learning (Scikit-Learn), and generates physical mitigation strategies through an AI Recommendation Engine.

---

## Overview
As cities grow, asphalt and concrete structures absorb heat, creating localized zones of extreme temperature known as Urban Heat Islands. Therma-Shield provides a complete visual digital twin of urban climates (pre-seeded with Bengaluru metropolitan datasets) to help planners analyze environmental vulnerabilities and test mitigation strategies.

### Core Workflow
1. **Data Ingestion**: Processes multi-spectral GeoTIFF bands, GeoJSON shapes, or tabular CSV coordinates.
2. **Feature Extraction**: Extracts Land Surface Temperature (LST), Normalized Difference Vegetation Index (NDVI), and Normalized Difference Built-up Index (NDBI).
3. **Statistical Analysis & Interpolation**: Maps raw hotspots and runs Inverse Distance Weighting (IDW) to interpolate continuous grid heat maps across municipal wards.
4. **Machine Learning Forecasting**: Trains a Random Forest regressor on spatial coordinates and remote sensing indicators to predict 5-year climate growth and future LST.
5. **Heuristic AI Action Recommendation**: Runs specialized rules matching land-cover, temperature, vegetation density, and built-up density to generate actionable climate response strategies.
6. **AI Assistant Dialogue**: Integrates a local context-aware assistant to query database stats and mitigation metrics.

---

## Features
* **Interactive GIS Heat Map**: High-performance dark-mode Leaflet canvas rendering visible hotspots, IDW grid overlays, and BBMP municipal ward boundaries. Responsive to map viewport bounds for optimized performance.
* **Analytical Dashboard**: Visualizes aggregated municipal summaries, risk levels, vegetation/built-up indexes, and historical distribution trends.
* **Point-and-Analyze Interactivity**: Clicking anywhere on the GIS map automatically locates the nearest hotspot or custom coordinates, extracts all environmental parameters for that location, and generates dynamic recommendations.
* **Climatology AI Assistant**: Context-aware NLP assistant that queries the SQLite database directly, allowing planners to ask natural language questions about local warming trends.
* **AI Climate Mitigation Strategy Engine**: Generates 5–10 customized mitigation strategies per hotspot (such as Cool Roofs, Miyawaki Forests, or Permeable Pavements) with technical explanations, priority levels, estimated temperature reductions, and costs.
* **Dynamic PDF Reports**: Generates executive ReportLab PDF documents summarizing climate diagnostics, data tables, and planning strategies.
* **Developer Control Center**: Accessible under the Settings tab, allowing developers to import new datasets, monitor ML model metrics, and trigger regressor retraining.

---

## Tech Stack

### Backend
* **FastAPI**: Asynchronous high-performance web framework.
* **Uvicorn**: ASGI server implementation.
* **SQLAlchemy**: ORM for database mapping.
* **ReportLab**: Dynamic PDF generation library.

### Frontend
* **React (Vite)**: Modern fast build environment.
* **Tailwind CSS**: Utility-first CSS styling.
* **Framer Motion**: Smooth animations.
* **React Leaflet / Leaflet.js**: Spatial map visualization.
* **Chart.js / React ChartJS 2**: Visual data widgets.
* **Axios**: HTTP client configuration.

### Database
* **SQLite**: Single-file relational database storage.

### AI / Machine Learning / GIS
* **Scikit-Learn**: Model training, evaluation, and regression.
* **Pandas & NumPy**: Data processing and statistical alignment.

---

## Folder Structure

```
urban-heat-island-platform/
├── backend/
│   ├── main.py                     # FastAPI backend server entry point
│   ├── database.py                 # SQLite SQLAlchemy initialization
│   ├── models.py                   # SQLAlchemy schema mapping (Hotspots, Recs, Chat)
│   ├── seed_db.py                  # Automatic database seeder
│   ├── requirements.txt            # Python dependencies
│   ├── routes/
│   │   ├── chat.py                 # Conversational assistant endpoints
│   │   ├── dashboard.py            # Summary statistics endpoints
│   │   ├── history.py              # Ingested dataset logs
│   │   ├── map.py                  # Hotspots, grids, and GeoJSON polygons
│   │   ├── predict.py              # ML model evaluation & training
│   │   ├── recommend.py            # Recommendations analysis
│   │   ├── report.py               # ReportLab PDF compiler
│   │   └── upload.py               # File uploads & validation pipeline
│   ├── ml/
│   │   └── pipeline.py             # Random Forest regressor pipeline
│   ├── recommendation_engine/
│   │   └── engine.py               # AI planning & mitigation heuristics
│   └── utils/
│       ├── assistant.py            # NLP Database assistant logic
│       ├── generate_bangalore_dataset.py # Bangalore production dataset generator
│       ├── generate_samples.py     # Legacy sample generator
│       └── geo_processor.py        # Remote sensing parameter parser
├── frontend/
│   ├── package.json                # npm package configuration
│   ├── vite.config.js              # Vite bundler rules
│   ├── tailwind.config.js          # Custom theme configuration
│   ├── .env                        # Active API endpoints configuration
│   ├── .env.example                # Template configuration file
│   └── src/
│       ├── main.jsx                # Application root mount
│       ├── App.jsx                 # App routing shell and state hub
│       ├── index.css               # Global styles & custom styling
│       ├── components/
│       │   ├── Sidebar.jsx         # Left navigation bar
│       │   ├── Dashboard.jsx       # Chart panels and analytics
│       │   ├── HeatMap.jsx         # React-Leaflet map & details panel
│       │   ├── Recommendations.jsx # Mitigation recommendations grid
│       │   ├── AIAssistant.jsx     # Conversational assistant panel
│       │   ├── Reports.jsx         # PDF compiler & history listing
│       │   └── Settings.jsx        # Developer controls & dataset importer
│       └── utils/
│           └── api.js              # Axios connection module
├── render.yaml                     # Backend Render deployment template
└── README.md                       # Documentation file
```

---

## Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Node.js 18+**

### 1. Backend Configuration
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize and seed the database:
   ```bash
   python seed_db.py
   ```
   *Note: This automatically creates `platform.db` and populates the database with the Bangalore metropolitan dataset (`Bangalore_UHI_Production.csv`), pre-calculating all local hotspot recommendations.*
4. Start the FastAPI uvicorn server on port **8080**:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
   ```
   *Note: Port 8080 is explicitly used to bypass zombie socket conflicts that commonly lock port 8000 on Windows localhost. The API documentation is available at `http://127.0.0.1:8080/docs`.*

### 2. Frontend Configuration
1. Open a new terminal tab and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Ensure your local environment variables in `frontend/.env` point to port **8080**:
   ```env
   VITE_API_URL=http://localhost:8080
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The interactive UI dashboard will be accessible at `http://localhost:5173`.*

---

## Environment Variables

### Frontend (`frontend/.env`)
* `VITE_API_URL`: Points to the active backend API. Set to `http://localhost:8080` for local development.

### Backend Deployment (`render.yaml`)
* `PORT`: Configures the server listening port (defaults to `8080` locally, or dynamically assigned in production).
* `ALLOWED_ORIGINS`: Configures CORS matching origins.

---

## API Documentation

### Dashboard
* **Method**: `GET`
* **Endpoint**: `/api/dashboard/summary`
* **Purpose**: Retrieves aggregated statistics, overall risk levels, average NDVI/NDBI indices, and historical climate trends.

### GIS Map
* **Method**: `GET`
* **Endpoint**: `/api/map/hotspots`
* **Purpose**: Retrieves coordinates, names, and temperatures of identified hotspots.
* **Method**: `GET`
* **Endpoint**: `/api/map/grid`
* **Purpose**: Retrieves coordinates for the 625-point Inverse Distance Weighting (IDW) interpolation grid.
* **Method**: `GET`
* **Endpoint**: `/api/map/districts`
* **Purpose**: Retrieves GeoJSON features representing Bangalore's BBMP municipal ward boundaries.

### Recommendations
* **Method**: `GET`
* **Endpoint**: `/api/recommendations`
* **Purpose**: Retrieves pre-calculated mitigation strategies for all hotspots.
* **Method**: `GET`
* **Endpoint**: `/api/recommendations/distribution`
* **Purpose**: Retrieves strategy type counts for chart components.
* **Method**: `POST`
* **Endpoint**: `/api/recommendations/analyze`
* **Purpose**: Submits custom coordinate parameters to generate on-the-fly UHI mitigation recommendations.

### Reports
* **Method**: `GET`
* **Endpoint**: `/api/report/download`
* **Purpose**: Compiles and downloads a comprehensive PDF climate report for active datasets.

### AI Assistant
* **Method**: `POST`
* **Endpoint**: `/api/chat`
* **Purpose**: Submits a natural language query along with current coordinate context to receive context-aware responses.
* **Method**: `GET`
* **Endpoint**: `/api/chat/history`
* **Purpose**: Retrieves the active session's persistent message log.
* **Method**: `DELETE`
* **Endpoint**: `/api/chat/history`
* **Purpose**: Clears all conversational history logs.

---

## Screenshots

* **Dashboard Overview**: `[Dashboard Screenshot Placeholder]`
* **Interactive GIS Map**: `[GIS Heat Map Screenshot Placeholder]`
* **AI Recommendations Grid**: `[AI Recommendations Screenshot Placeholder]`
* **PDF Report Preview**: `[Reports PDF Screenshot Placeholder]`
* **Climatology AI Assistant**: `[AI Assistant Screenshot Placeholder]`
* **Developer Controls & Settings**: `[Settings Panel Screenshot Placeholder]`

---

## Running the Project: Development Workflow
1. Start the backend service on port `8080`.
2. Start the Vite frontend development environment.
3. Open `http://localhost:5173` in your browser. The platform automatically mounts the preloaded Bangalore digital twin dataset.
4. Go to the **GIS Heat Map** and toggle layer switches (Hotspots, IDW Grid, Municipal Wards).
5. Click on any hotspot marker or municipal boundary to load it as the active context.
6. Navigate to **AI Recommendations** to view customized strategies generated dynamically for that neighborhood.
7. Open the **AI Assistant** to chat about local warming causes.
8. Click **Download PDF Report** in the Reports tab to generate an executive report.

---

## Deployment

### Backend (Render)
This project is configured to run on Render via the [render.yaml](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/urban-heat-island-platform/render.yaml) file:
1. Link your GitHub repository to Render.
2. Render will automatically parse `render.yaml` to spin up a Python web service under the `backend` directory.
3. Configure the `ALLOWED_ORIGINS` environment variable to match your frontend production URL.

### Frontend (Vercel)
Deploy your compiled Vite bundle to Vercel:
1. Import your repository into Vercel.
2. Set the build folder to `frontend`.
3. Set the Environment Variable `VITE_API_URL` to point to your live Render backend URL.

---

## Troubleshooting

### 1. Backend port Binding Collisions (`Errno 10048`)
* **Problem**: Uvicorn fails to start with: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`.
* **Fix**: Port 8000 is occupied by a lingering process. Start uvicorn on port **8080**:
  ```bash
  python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
  ```
  Ensure your `frontend/.env` has `VITE_API_URL=http://localhost:8080` and rebuild.

### 2. GIS Heat Map turns Black
* **Problem**: The map page fails to render, leaving a blank black screen.
* **Fix**: Check the browser console. If there are GeoJSON coordinate or tooltip reference crashes, verify that the active database is seeded. Run:
  ```bash
  python seed_db.py
  ```
  to recreate and populate `platform.db` with correct coordinate schemas.

### 3. Missing AI recommendations for clicked point
* **Problem**: Clicking a custom point on the map fails to display recommendations in the panel.
* **Fix**: Ensure your backend has the latest import for `AIRecommendationEngine` inside `backend/routes/recommend.py`. Verify that the FastAPI console is not showing a `NameError`.

---

## Future Improvements
1. **Google Earth Engine (GEE) Integration**: Dynamically pull real-time NDVI and thermal band parameters using local coordinates instead of pre-computed rasters.
2. **High-Resolution Canopy Segmentation**: Implement deep learning segmentation models (e.g. U-Net) to extract precise canopy coverage boundaries from high-resolution visual bands.
3. **Advanced Microclimate Ventilation Modeling**: Incorporate elevation contours and wind speed measurements to calculate convective cooling pathways along urban corridors.

---

## License
MIT License. Created as part of the Geospatial AI Platform portfolio.
