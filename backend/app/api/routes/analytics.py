"""
Analytics and reporting API endpoints
Elemző és jelentéskészítő API végpontok
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io

from app.database import get_db
from app.core.deps import get_current_active_user
from app.core.rbac import require_permission, PermissionActions, Resources
from app.models.auth import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_dashboard_analytics(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    days_back: int = Query(30, ge=1, le=365, description="Days back for analysis"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kombinált dashboard elemzések - Combined dashboard analytics
    Returns KPIs, charts and summary data for the main dashboard
    """
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_dashboard_analytics(
            organization_id=organization_id,
            days_back=days_back
        )
        
        return {
            "status": "success",
            "data": dashboard_data,
            "generated_at": datetime.now().isoformat(),
            "organization_id": organization_id,
            "period_days": days_back
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@router.get("/inspections/due")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_due_inspections_analytics(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to analyze"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Lejáró ellenőrzések elemzése - Due inspections analytics
    Provides comprehensive analysis of upcoming and overdue inspections
    """
    try:
        analytics_service = AnalyticsService(db)
        due_analytics = analytics_service.get_due_inspections_analytics(
            days_ahead=days_ahead,
            organization_id=organization_id
        )
        
        return {
            "status": "success",
            "data": due_analytics,
            "generated_at": datetime.now().isoformat(),
            "parameters": {
                "days_ahead": days_ahead,
                "organization_id": organization_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Due inspections analytics error: {str(e)}")


@router.get("/sla")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_sla_analytics(
    days_back: int = Query(30, ge=1, le=365, description="Days back for SLA analysis"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    SLA teljesítmény elemzése - SLA performance analytics
    Provides detailed SLA compliance metrics and trends
    """
    try:
        analytics_service = AnalyticsService(db)
        sla_analytics = analytics_service.get_sla_analytics(
            days_back=days_back,
            organization_id=organization_id
        )
        
        return {
            "status": "success",
            "data": sla_analytics,
            "generated_at": datetime.now().isoformat(),
            "parameters": {
                "days_back": days_back,
                "organization_id": organization_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SLA analytics error: {str(e)}")


@router.get("/errors")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_error_statistics(
    days_back: int = Query(30, ge=1, le=365, description="Days back for error analysis"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Hibastatisztika elemzése - Error statistics analysis
    Provides comprehensive error analysis and failure patterns
    """
    try:
        analytics_service = AnalyticsService(db)
        error_stats = analytics_service.get_error_statistics(
            days_back=days_back,
            organization_id=organization_id
        )
        
        return {
            "status": "success",
            "data": error_stats,
            "generated_at": datetime.now().isoformat(),
            "parameters": {
                "days_back": days_back,
                "organization_id": organization_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error statistics error: {str(e)}")


# =============================================================================
# EXPORT ENDPOINTS - EXPORT VÉGPONTOK
# =============================================================================

@router.get("/export/inspections/csv")
@require_permission(Resources.GATE, PermissionActions.READ)
async def export_due_inspections_csv(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to export"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lejáró ellenőrzések CSV export - Export due inspections to CSV
    """
    try:
        analytics_service = AnalyticsService(db)
        csv_data = analytics_service.export_due_inspections_csv(
            days_ahead=days_ahead,
            organization_id=organization_id
        )
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lejaro_ellenorzesek_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/export/sla/excel")
@require_permission(Resources.GATE, PermissionActions.READ)
async def export_sla_report_excel(
    days_back: int = Query(30, ge=1, le=365, description="Days back for SLA export"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    SLA jelentés Excel export - Export SLA report to Excel
    """
    try:
        analytics_service = AnalyticsService(db)
        excel_data = analytics_service.export_sla_report_excel(
            days_back=days_back,
            organization_id=organization_id
        )
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sla_jelentes_{timestamp}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/export/errors/csv")
@require_permission(Resources.GATE, PermissionActions.READ)
async def export_error_statistics_csv(
    days_back: int = Query(30, ge=1, le=365, description="Days back for error export"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Hibastatisztika CSV export - Export error statistics to CSV
    """
    try:
        analytics_service = AnalyticsService(db)
        csv_data = analytics_service.export_error_statistics_csv(
            days_back=days_back,
            organization_id=organization_id
        )
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hibastatisztika_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/export/dashboard/excel")
@require_permission(Resources.GATE, PermissionActions.READ)
async def export_dashboard_excel(
    days_back: int = Query(30, ge=1, le=365, description="Days back for dashboard export"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Teljes dashboard Excel export - Export complete dashboard to Excel
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get all analytics data
        dashboard_data = analytics_service.get_dashboard_analytics(
            organization_id=organization_id,
            days_back=days_back
        )
        
        # Create comprehensive Excel report
        output = io.BytesIO()
        
        import pandas as pd
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # KPIs sheet
            kpis_data = []
            for kpi in dashboard_data['kpis']:
                kpis_data.append({
                    'KPI Név': kpi['name'],
                    'Érték': kpi['value'],
                    'Egység': kpi['unit'],
                    'Cél': kpi.get('target', ''),
                    'Állapot': kpi['status'],
                    'Trend': kpi.get('trend', '')
                })
            
            kpis_df = pd.DataFrame(kpis_data)
            kpis_df.to_excel(writer, sheet_name='KPI-k', index=False)
            
            # Due inspections chart data
            due_inspections_df = pd.DataFrame(dashboard_data['charts']['due_inspections'])
            due_inspections_df.columns = ['Dátum', 'Esedékes ellenőrzések', 'ISO Dátum']
            due_inspections_df = due_inspections_df[['Dátum', 'Esedékes ellenőrzések']]
            due_inspections_df.to_excel(writer, sheet_name='Lejáró ellenőrzések', index=False)
            
            # SLA performance chart data
            sla_performance_df = pd.DataFrame(dashboard_data['charts']['sla_performance'])
            sla_performance_df.columns = ['Dátum', 'SLA megfelelés (%)', 'ISO Dátum']
            sla_performance_df = sla_performance_df[['Dátum', 'SLA megfelelés (%)']]
            sla_performance_df.to_excel(writer, sheet_name='SLA teljesítmény', index=False)
            
            # Error trends chart data
            error_trends_df = pd.DataFrame(dashboard_data['charts']['error_trends'])
            error_trends_df.columns = ['Dátum', 'Hibaarány (%)', 'ISO Dátum']
            error_trends_df = error_trends_df[['Dátum', 'Hibaarány (%)']]
            error_trends_df.to_excel(writer, sheet_name='Hibastatisztika', index=False)
            
            # Summary sheet
            summary_data = []
            for category, data in dashboard_data['summaries'].items():
                for key, value in data.items():
                    summary_data.append({
                        'Kategória': category.title(),
                        'Metrika': key,
                        'Érték': value
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Összefoglalók', index=False)
        
        output.seek(0)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_jelentes_{timestamp}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard export error: {str(e)}")


# =============================================================================
# UTILITY ENDPOINTS - SEGÉDVÉGPONTOK
# =============================================================================

@router.get("/kpis")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_key_kpis(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    days_back: int = Query(30, ge=1, le=90, description="Days back for KPI calculation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kulcs KPI-k lekérdezése - Get key KPIs only
    Returns the 3 main KPIs for quick dashboard display
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get analytics for KPIs
        due_inspections = analytics_service.get_due_inspections_analytics(30, organization_id)
        sla_analytics = analytics_service.get_sla_analytics(days_back, organization_id)
        error_stats = analytics_service.get_error_statistics(days_back, organization_id)
        
        # Select the 3 most important KPIs
        key_kpis = [
            due_inspections['kpis'][0],  # Overdue inspections
            sla_analytics['kpis'][0],    # SLA compliance
            error_stats['kpis'][0]       # Error rate
        ]
        
        return {
            "status": "success",
            "kpis": [
                {
                    'name': kpi.name,
                    'value': kpi.value,
                    'unit': kpi.unit,
                    'status': kpi.status,
                    'target': kpi.target
                } for kpi in key_kpis
            ],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KPI error: {str(e)}")


@router.get("/charts/combined")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_combined_chart_data(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    days_back: int = Query(30, ge=7, le=90, description="Days back for chart data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kombinált grafikon adatok - Combined chart data
    Returns chart data for all three main metrics in one call
    """
    try:
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_dashboard_analytics(
            organization_id=organization_id,
            days_back=days_back
        )
        
        return {
            "status": "success",
            "charts": dashboard_data['charts'],
            "period_days": days_back,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart data error: {str(e)}")