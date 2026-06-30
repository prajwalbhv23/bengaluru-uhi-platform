import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import UploadDataset, HotspotPrediction, MitigationRecommendation

# Try to import reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

router = APIRouter(prefix="/api")

@router.get("/report/download")
async def download_report(
    dataset_id: int = Query(None, description="Dataset ID to generate report for"),
    db: Session = Depends(get_db)
):
    """
    Generates a production-ready, beautifully styled PDF executive report of the UHI analysis
    and returns it as a streaming download.
    """
    # 1. Fetch data
    if dataset_id:
        dataset = db.query(UploadDataset).filter(UploadDataset.id == dataset_id).first()
    else:
        dataset = db.query(UploadDataset).filter(UploadDataset.status == "Processed").order_by(UploadDataset.upload_time.desc()).first()
        
    if not dataset:
        raise HTTPException(status_code=404, detail="No active processed dataset found.")
        
    hotspots = db.query(HotspotPrediction).filter(HotspotPrediction.dataset_id == dataset.id).all()
    if not hotspots:
        raise HTTPException(status_code=400, detail="The dataset has no hotspots processed yet.")
        
    # Gather statistics
    max_temp = max(h.lst for h in hotspots)
    avg_temp = sum(h.lst for h in hotspots) / len(hotspots)
    avg_ndvi = sum(h.ndvi for h in hotspots) / len(hotspots)
    critical_zones = [h for h in hotspots if h.risk_level == "Critical"]
    high_zones = [h for h in hotspots if h.risk_level == "High"]
    
    # 2. Compile Recommendations
    recommendations_list = []
    for h in hotspots:
        for r in h.recommendations:
            recommendations_list.append((h, r))
            
    # Calculate carbon reduction and total estimated cost
    total_carbon_offset = sum(r.carbon_reduction for h, r in recommendations_list)
    avg_cost = sum(r.cost_est for h, r in recommendations_list) / max(1, len(recommendations_list))
    
    if not HAS_REPORTLAB:
        # Fallback text/markdown stream if ReportLab is missing
        output = io.BytesIO()
        report_text = f"""
BENGALURU URBAN HEAT ISLAND INTELLIGENCE PLATFORM
==================================================
BENGALURU CLIMATE INTELLIGENCE ASSESSMENT REPORT
--------------------------------------------------
Dataset File: {dataset.filename}
Generated On: {dataset.upload_time.strftime('%Y-%m-%d %H:%M')}
Status: Processed

KEY METRICS
- Total Hotspots Detected: {len(hotspots)} locations
- Maximum Surface Temperature: {max_temp:.2f}°C
- Average Surface Temperature: {avg_temp:.2f}°C
- Average Vegetation density (NDVI): {avg_ndvi:.3f}
- Critical Risk Zones: {len(critical_zones)} areas
- High Risk Zones: {len(high_zones)} areas
- Estimated Carbon Savings: {total_carbon_offset:.1f} tons CO2/year
- Average Mitigation Cost: ${avg_cost:.2f} / m²

RECOMMENDED STRATEGIES
"""
        for i, (h, r) in enumerate(recommendations_list[:20]):
            report_text += f"\n{i+1}. {r.strategy_name} ({r.category}) at {h.name}\n"
            report_text += f"   Priority: {r.priority_level} | Est Cooling: -{r.temp_reduction}°C | Cost: ${r.cost_est}/m²\n"
            report_text += f"   Description: {r.description}\n"
            
        output.write(report_text.encode('utf-8'))
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=Bengaluru_UHI_Report_{dataset.id}.txt"}
        )
        
    # Generate actual ReportLab PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom high-quality ParagraphStyles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0F172A'), # Deep slate
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#059669'), # Emerald Green
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        leading=14,
        spaceAfter=10
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBody_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Title & Subtitle Banner
    story.append(Paragraph("BENGALURU URBAN HEAT ISLAND INTELLIGENCE PLATFORM", title_style))
    story.append(Paragraph(f"Bengaluru Climate Intelligence Assessment Report &mdash; Dataset: {dataset.filename} &mdash; Generated On: {dataset.upload_time.strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    exec_summary_text = (
        f"This report presents the spatial analysis of Urban Heat Island (UHI) hotspots detected from satellite and sensor data in "
        f"the dataset <b>{dataset.filename}</b>. Our Machine Learning pipeline extracted environmental indices (NDVI, NDBI) and "
        f"modeled surface temperatures across <b>{len(hotspots)} locations</b>. A total of <b>{len(critical_zones)} Critical</b> and "
        f"<b>{len(high_zones)} High-Risk</b> zones were isolated. The AI Recommendation Engine generated customized physical "
        f"mitigation layouts targeting an average temperature reduction of up to 4.5°C in critical cores, with a projected net "
        f"carbon offset of <b>{total_carbon_offset:.1f} tons CO₂/year</b>."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    
    # KPI Grid Table
    kpi_data = [
        [
            Paragraph("<b>Total Zones Analyzed</b>", bold_body_style), 
            Paragraph(str(len(hotspots)), body_style),
            Paragraph("<b>Peak Surface Temp (LST)</b>", bold_body_style),
            Paragraph(f"{max_temp:.1f}°C", body_style)
        ],
        [
            Paragraph("<b>Average Hotspot Temp</b>", bold_body_style),
            Paragraph(f"{avg_temp:.1f}°C", body_style),
            Paragraph("<b>Average NDVI</b>", bold_body_style),
            Paragraph(f"{avg_ndvi:.3f}", body_style)
        ],
        [
            Paragraph("<b>Critical Zones (>42°C)</b>", bold_body_style),
            Paragraph(str(len(critical_zones)), body_style),
            Paragraph("<b>Carbon Reduction Estimate</b>", bold_body_style),
            Paragraph(f"{total_carbon_offset:.1f} Tons/yr", body_style)
        ],
    ]
    
    kpi_table = Table(kpi_data, colWidths=[150, 100, 170, 100])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 15))
    
    # Section 2: Hotspot Vulnerability Analysis
    story.append(Paragraph("2. Hotspot Vulnerability & Risk Classification", h1_style))
    story.append(Paragraph(
        "Hotspots are classified based on Land Surface Temperature (LST) and the corresponding Normalized Difference "
        "Vegetation Index (NDVI). Areas combining high temperature and low vegetation are cataloged as high or critical priority.",
        body_style
    ))
    
    # Table of Top Hotspots (limit to 8 for PDF page layout)
    hotspot_headers = ["Location/District", "LST (°C)", "NDVI", "NDBI", "Land Cover", "Risk Level"]
    hotspot_rows = [[Paragraph(f"<b>{h}</b>", bold_body_style) for h in hotspot_headers]]
    
    sorted_hotspots = sorted(hotspots, key=lambda x: x.lst, reverse=True)[:8]
    for h in sorted_hotspots:
        hotspot_rows.append([
            Paragraph(h.name, body_style),
            Paragraph(f"{h.lst:.1f}", body_style),
            Paragraph(f"{h.ndvi:.2f}", body_style),
            Paragraph(f"{h.ndbi:.2f}", body_style),
            Paragraph(h.land_cover, body_style),
            Paragraph(f"<font color='{ '#EF4444' if h.risk_level=='Critical' else '#F97316' if h.risk_level=='High' else '#EAB308' }'><b>{h.risk_level}</b></font>", body_style)
        ])
        
    hotspot_table = Table(hotspot_rows, colWidths=[140, 70, 60, 60, 100, 90])
    hotspot_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'), # Left align names
    ]))
    
    story.append(hotspot_table)
    story.append(Spacer(1, 15))
    
    # Section 3: AI Mitigation Recommendations
    story.append(Paragraph("3. Recommended AI Mitigation Interventions", h1_style))
    story.append(Paragraph(
        "Below is a list of the most cost-effective and highest impact cooling strategies suggested by our AI Engine, "
        "tailored to the specific land cover dynamics and temperatures of the worst-performing districts.",
        body_style
    ))
    
    # Table of Recommendations
    rec_headers = ["Target Zone", "Mitigation Strategy", "Category", "Est Cooling", "Carbon Offset", "Cost Est"]
    rec_rows = [[Paragraph(f"<b>{h}</b>", bold_body_style) for h in rec_headers]]
    
    sorted_recs = sorted(recommendations_list, key=lambda x: (x[1].priority_level == "Critical", x[1].temp_reduction), reverse=True)[:8]
    for h, r in sorted_recs:
        rec_rows.append([
            Paragraph(h.name, body_style),
            Paragraph(r.strategy_name, body_style),
            Paragraph(r.category, body_style),
            Paragraph(f"-{r.temp_reduction:.1f}°C", body_style),
            Paragraph(f"{r.carbon_reduction:.1f} t/yr", body_style),
            Paragraph(f"${r.cost_est:.1f}/m²", body_style)
        ])
        
    rec_table = Table(rec_rows, colWidths=[110, 150, 90, 70, 70, 70])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (1,-1), 'LEFT'), # Left align strategy names
    ]))
    
    story.append(rec_table)
    story.append(Spacer(1, 15))
    
    # Section 4: Future Planning
    story.append(Paragraph("4. Future Urban Planning & Action Items", h1_style))
    story.append(Paragraph(
        "1. <b>Prioritize Critical Cores</b>: Focus municipal capital budgets on districts marked as Critical Risk. Applying light roof coatings is the fastest low-cost action item.<br/>"
        "2. <b>Expand Street Canopies</b>: Incorporate tree planting guidelines in districts showing average NDVI values below 0.15. Target a tree canopy expansion of 25% over the next 5 years.<br/>"
        "3. <b>Revamp Local Building Codes</b>: Require green facades or photovoltaic parking structures in new commercial permits.<br/>"
        "4. <b>Establish Hydrological Cool Zones</b>: Connect storm drain retention bioswales near industrial parks to encourage cooling by natural evaporation.",
        body_style
    ))
    
    # Build Document
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Bengaluru_UHI_Report_{dataset.id}.pdf"}
    )
