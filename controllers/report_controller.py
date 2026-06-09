from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from services.report_service import (
    get_critical_regions_report,
    get_historical_report,
    export_csv,
    export_critical_csv,
)
from services.heatscore_service import get_ranking
from database.connection import get_connection
import io

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/critical")
def critical_regions():
    data = get_critical_regions_report()
    return {"total": len(data), "regions": data}


@router.get("/history/{region_id}")
def historical(region_id: int):
    data = get_historical_report(region_id)
    if not data:
        raise HTTPException(status_code=404, detail="No history found for this region")
    return data


@router.get("/export/csv")
def export_all_csv():
    content, filename = export_csv()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/csv/{region_id}")
def export_region_csv(region_id: int):
    content, filename = export_csv(region_id)
    if not content:
        raise HTTPException(status_code=404, detail="No data found for this region")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/critical/csv")
def export_critical_regions_csv():
    content, filename = export_critical_csv()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/pdf/{region_id}")
def export_pdf(region_id: int):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    from datetime import datetime

    data = get_historical_report(region_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this region")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM regions WHERE id = ?", (region_id,))
    row = cur.fetchone()
    conn.close()
    region_name = row[0] if row else str(region_id)

    heatscore = get_ranking()
    hs_region = next((r for r in heatscore if r["region_id"] == region_id), None)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(f"UrbanHeat — Relatório da Região: {region_name}", styles["Title"])
    )
    elements.append(
        Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]
        )
    )
    elements.append(Spacer(1, 12))

    if hs_region:
        elements.append(Paragraph("HeatScore", styles["Heading2"]))
        hs_data = [
            ["Score", "Classificação", "Temp. Média", "Freq. Calor", "Duração Crítica"],
            [
                str(hs_region["score"]),
                hs_region["classification"],
                f"{hs_region['average_temperature']}°C",
                f"{round(hs_region['high_temperature_frequency'] * 100, 1)}%",
                f"{round(hs_region['critical_duration'] * 100, 1)}%",
            ],
        ]
        hs_table = Table(hs_data, hAlign="LEFT")
        hs_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.whitesmoke, colors.white],
                    ),
                ]
            )
        )
        elements.append(hs_table)
        elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("Histórico de Medições (últimos 30 dias)", styles["Heading2"])
    )
    table_data = [["Região", "Temperatura (°C)", "Umidade (%)", "Data/Hora"]]
    for m in data:
        table_data.append(
            [
                m["region_name"],
                str(m["temperature"]),
                str(m["humidity"]),
                m["created_at"],
            ]
        )

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    filename = (
        f"urbanheat_{region_name.lower()}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
