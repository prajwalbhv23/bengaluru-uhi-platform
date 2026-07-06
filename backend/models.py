import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base

class UploadDataset(Base):
    __tablename__ = "upload_datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_type = Column(String)  # GeoTIFF, CSV, GeoJSON, etc.
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Pending")  # Pending, Processing, Processed, Failed
    records_count = Column(Integer, default=0)
    file_path = Column(String)
    
    # Aggregated metrics for GIS decision-support summary
    mitigation_summary = Column(Text, nullable=True)
    avg_temp = Column(Float, default=0.0)
    min_temp = Column(Float, default=0.0)
    max_temp = Column(Float, default=0.0)
    heat_island_intensity = Column(Float, default=0.0)
    water_body_coverage = Column(Float, default=0.0) # percentage of points as water

    hotspots = relationship("HotspotPrediction", back_populates="dataset", cascade="all, delete-orphan")

class HotspotPrediction(Base):
    __tablename__ = "hotspot_predictions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("upload_datasets.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    lst = Column(Float)  # Land Surface Temperature in °C
    ndvi = Column(Float)  # NDVI [-1, 1]
    ndbi = Column(Float)  # NDBI [-1, 1]
    built_up_density = Column(Float)  # Percentage [0, 100]
    vegetation_density = Column(Float)  # Percentage [0, 100]
    risk_score = Column(Float)  # Severity Score [0, 100]
    risk_level = Column(String)  # Low, Medium, High, Critical
    growth_prediction = Column(Float)  # Estimated LST growth in 5 years
    land_cover = Column(String)  # Residential, Commercial, Industrial, Park, Water, etc.
    ward = Column(String, nullable=True)
    tree_canopy = Column(Float, default=0.0)
    population_density = Column(Float, default=0.0)
    humidity = Column(Float, default=0.0)
    heat_index = Column(Float, default=0.0)

    dataset = relationship("UploadDataset", back_populates="hotspots")
    recommendations = relationship("MitigationRecommendation", back_populates="hotspot", cascade="all, delete-orphan")

class MitigationRecommendation(Base):
    __tablename__ = "mitigation_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspot_predictions.id", ondelete="CASCADE"))
    strategy_name = Column(String)
    category = Column(String)  # Green Infrastructure, Cool Materials, Policy / Urban Planning
    description = Column(Text)
    confidence_score = Column(Float)  # percentage [0, 100]
    temp_reduction = Column(Float)  # estimated reduction in °C
    cost_est = Column(Float)  # cost estimate in USD per sq meter or total
    env_impact = Column(String)  # Low, Medium, High
    carbon_reduction = Column(Float)  # estimated carbon reduction in tons CO2/year
    priority_level = Column(String)  # Immediate, Short-Term, Long-Term (formerly Low/Medium/High/Critical)
    
    # Advanced metadata fields for re-designed engine
    reason = Column(Text, nullable=True) # why was this recommended
    severity = Column(String, nullable=True) # Low, Moderate, High, Critical
    estimated_impact = Column(Text, nullable=True)
    environmental_benefits = Column(Text, nullable=True)
    sdg_alignment = Column(String, nullable=True) # e.g. "SDG 11: Sustainable Cities"
    cost_level = Column(String, nullable=True) # Low / Medium / High
    implementation_time = Column(String, nullable=True)
    technical_explanation = Column(Text, nullable=True)
    sustainability_benefits = Column(Text, nullable=True)
    recommended_implementation = Column(Text, nullable=True)
    trigger_condition = Column(Text, nullable=True)

    hotspot = relationship("HotspotPrediction", back_populates="recommendations")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # user, assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, index=True)
    setting_value = Column(String)
