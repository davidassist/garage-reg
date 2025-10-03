"""
Analytics and reporting service for inspections, SLA monitoring and error statistics
Elemző és jelentéskészítő szolgáltatás ellenőrzésekhez, SLA monitoring-hoz és hibastatisztikához
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, case, extract, text
from dataclasses import dataclass
import pandas as pd
import io

from app.models.inspections import Inspection, ChecklistItem, InspectionItem
from app.models.organization import Gate
from app.models.tickets import WorkOrder, Ticket
from app.models.maintenance import MaintenanceJob
from app.database import get_db

logger = logging.getLogger(__name__)


@dataclass
class KPIMetric:
    """KPI metric data structure"""
    name: str
    value: Union[int, float, Decimal]
    unit: str
    trend: Optional[float] = None  # Percentage change
    target: Optional[Union[int, float]] = None
    status: str = "normal"  # normal, warning, critical


@dataclass
class ChartDataPoint:
    """Chart data point structure"""
    label: str
    value: Union[int, float, Decimal]
    date: Optional[datetime] = None
    category: Optional[str] = None


@dataclass
class ExportData:
    """Export data structure"""
    data: List[Dict[str, Any]]
    headers: List[str]
    title: str


class AnalyticsService:
    """
    Main analytics service for generating KPIs, charts and reports
    Fő elemző szolgáltatás KPI-k, grafikonok és jelentések generálásához
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # =============================================================================
    # INSPECTION ANALYTICS - ELLENŐRZÉSI ELEMZÉSEK
    # =============================================================================
    
    def get_due_inspections_analytics(
        self,
        days_ahead: int = 30,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Lejáró ellenőrzések elemzése - Due inspections analytics
        
        Args:
            days_ahead: Hány napra előre nézzünk
            organization_id: Szűrés szervezetre
        """
        
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        # Base query
        query = self.db.query(Inspection).join(Gate)
        
        if organization_id:
            query = query.filter(Gate.organization_id == organization_id)
        
        # Overdue inspections (lejárt ellenőrzések)
        overdue_count = query.filter(
            Inspection.scheduled_date < datetime.now(),
            Inspection.status.in_(['scheduled', 'in_progress'])
        ).count()
        
        # Due this week (ez a héten esedékes)
        week_end = datetime.now() + timedelta(days=7)
        due_this_week = query.filter(
            Inspection.scheduled_date >= datetime.now(),
            Inspection.scheduled_date <= week_end,
            Inspection.status.in_(['scheduled', 'in_progress'])
        ).count()
        
        # Due next 30 days (következő 30 napban esedékes)
        due_30_days = query.filter(
            Inspection.scheduled_date >= datetime.now(),
            Inspection.scheduled_date <= cutoff_date,
            Inspection.status.in_(['scheduled', 'in_progress'])
        ).count()
        
        # Completion rate calculation (befejezési arány számítása)
        last_30_days = datetime.now() - timedelta(days=30)
        
        total_inspections = query.filter(
            Inspection.scheduled_date >= last_30_days
        ).count()
        
        completed_inspections = query.filter(
            Inspection.scheduled_date >= last_30_days,
            Inspection.status == 'completed'
        ).count()
        
        completion_rate = (completed_inspections / total_inspections * 100) if total_inspections > 0 else 0
        
        # Daily due inspections for chart (napi lejáró ellenőrzések grafikonhoz)
        daily_due = []
        for i in range(30):
            day = datetime.now() + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            daily_count = query.filter(
                Inspection.scheduled_date >= day_start,
                Inspection.scheduled_date <= day_end,
                Inspection.status.in_(['scheduled', 'in_progress'])
            ).count()
            
            daily_due.append(ChartDataPoint(
                label=day.strftime("%m-%d"),
                value=daily_count,
                date=day_start
            ))
        
        # By gate type analysis (kaputípus szerinti elemzés)
        gate_type_stats = self.db.query(
            Gate.gate_type,
            func.count(Inspection.id).label('total_inspections'),
            func.count(case((Inspection.status == 'completed', 1))).label('completed'),
            func.count(case((Inspection.scheduled_date < datetime.now(), 1))).label('overdue')
        ).join(Gate).group_by(Gate.gate_type).all()
        
        gate_analysis = []
        for gate_type, total, completed, overdue in gate_type_stats:
            completion_pct = (completed / total * 100) if total > 0 else 0
            gate_analysis.append({
                'gate_type': gate_type,
                'total_inspections': total,
                'completed': completed,
                'overdue': overdue,
                'completion_rate': round(completion_pct, 1)
            })
        
        return {
            'summary': {
                'overdue_inspections': overdue_count,
                'due_this_week': due_this_week,
                'due_30_days': due_30_days,
                'completion_rate': round(completion_rate, 1)
            },
            'daily_due_chart': [
                {'label': dp.label, 'value': dp.value, 'date': dp.date.isoformat() if dp.date else None}
                for dp in daily_due
            ],
            'gate_type_analysis': gate_analysis,
            'kpis': [
                KPIMetric(
                    name="Lejárt Ellenőrzések",
                    value=overdue_count,
                    unit="db",
                    status="critical" if overdue_count > 10 else "warning" if overdue_count > 0 else "normal"
                ),
                KPIMetric(
                    name="Befejezési Arány",
                    value=completion_rate,
                    unit="%",
                    target=85.0,
                    status="critical" if completion_rate < 70 else "warning" if completion_rate < 85 else "normal"
                ),
                KPIMetric(
                    name="Heti Esedékesség",
                    value=due_this_week,
                    unit="db",
                    status="warning" if due_this_week > 20 else "normal"
                )
            ]
        }
    
    # =============================================================================
    # SLA ANALYTICS - SLA ELEMZÉSEK
    # =============================================================================
    
    def get_sla_analytics(
        self,
        days_back: int = 30,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        SLA teljesítmény elemzése - SLA performance analytics
        
        Args:
            days_back: Hány napra visszamenőleg
            organization_id: Szűrés szervezetre
        """
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Work Orders SLA Analysis
        wo_query = self.db.query(WorkOrder).join(Gate)
        
        if organization_id:
            wo_query = wo_query.filter(Gate.organization_id == organization_id)
        
        wo_query = wo_query.filter(WorkOrder.created_at >= start_date)
        
        # Calculate SLA metrics
        total_work_orders = wo_query.count()
        
        # SLA breached (SLA túllépés)
        sla_breached = wo_query.filter(
            WorkOrder.sla_due_date.isnot(None),
            WorkOrder.completed_at.isnot(None),
            WorkOrder.completed_at > WorkOrder.sla_due_date
        ).count()
        
        # SLA at risk (SLA veszélyben - 80% of time used)
        sla_at_risk = wo_query.filter(
            WorkOrder.sla_due_date.isnot(None),
            WorkOrder.status.in_(['open', 'in_progress']),
            WorkOrder.sla_due_date < datetime.now() + timedelta(hours=24)
        ).count()
        
        # Average resolution time
        completed_orders = wo_query.filter(
            WorkOrder.completed_at.isnot(None)
        ).all()
        
        if completed_orders:
            total_resolution_hours = sum([
                (wo.completed_at - wo.created_at).total_seconds() / 3600
                for wo in completed_orders
            ])
            avg_resolution_time = total_resolution_hours / len(completed_orders)
        else:
            avg_resolution_time = 0
        
        sla_compliance_rate = ((total_work_orders - sla_breached) / total_work_orders * 100) if total_work_orders > 0 else 0
        
        # Daily SLA performance for chart
        daily_sla_performance = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            day_total = wo_query.filter(
                WorkOrder.created_at >= day_start,
                WorkOrder.created_at <= day_end
            ).count()
            
            day_breached = wo_query.filter(
                WorkOrder.created_at >= day_start,
                WorkOrder.created_at <= day_end,
                WorkOrder.sla_due_date.isnot(None),
                WorkOrder.completed_at.isnot(None),
                WorkOrder.completed_at > WorkOrder.sla_due_date
            ).count()
            
            day_compliance = ((day_total - day_breached) / day_total * 100) if day_total > 0 else 100
            
            daily_sla_performance.append(ChartDataPoint(
                label=day.strftime("%m-%d"),
                value=round(day_compliance, 1),
                date=day_start
            ))
        
        # Priority breakdown
        priority_stats = self.db.query(
            WorkOrder.priority,
            func.count(WorkOrder.id).label('total'),
            func.count(case((
                and_(WorkOrder.sla_due_date.isnot(None),
                     WorkOrder.completed_at.isnot(None),
                     WorkOrder.completed_at > WorkOrder.sla_due_date), 1
            ))).label('breached')
        ).filter(WorkOrder.created_at >= start_date)\
         .group_by(WorkOrder.priority).all()
        
        priority_analysis = []
        for priority, total, breached in priority_stats:
            compliance = ((total - breached) / total * 100) if total > 0 else 0
            priority_analysis.append({
                'priority': priority,
                'total_orders': total,
                'sla_breached': breached,
                'compliance_rate': round(compliance, 1)
            })
        
        return {
            'summary': {
                'total_work_orders': total_work_orders,
                'sla_breached': sla_breached,
                'sla_at_risk': sla_at_risk,
                'sla_compliance_rate': round(sla_compliance_rate, 1),
                'avg_resolution_hours': round(avg_resolution_time, 1)
            },
            'daily_sla_chart': [
                {'label': dp.label, 'value': dp.value, 'date': dp.date.isoformat() if dp.date else None}
                for dp in daily_sla_performance
            ],
            'priority_analysis': priority_analysis,
            'kpis': [
                KPIMetric(
                    name="SLA Megfelelés",
                    value=sla_compliance_rate,
                    unit="%",
                    target=95.0,
                    status="critical" if sla_compliance_rate < 80 else "warning" if sla_compliance_rate < 95 else "normal"
                ),
                KPIMetric(
                    name="Átlagos Megoldási Idő",
                    value=avg_resolution_time,
                    unit="óra",
                    target=24.0,
                    status="warning" if avg_resolution_time > 48 else "normal"
                ),
                KPIMetric(
                    name="Veszélyben Lévő Esetek",
                    value=sla_at_risk,
                    unit="db",
                    status="warning" if sla_at_risk > 5 else "normal"
                )
            ]
        }
    
    # =============================================================================
    # ERROR STATISTICS - HIBASTATISZTIKÁK
    # =============================================================================
    
    def get_error_statistics(
        self,
        days_back: int = 30,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Hibastatisztika elemzése - Error statistics analysis
        
        Args:
            days_back: Hány napra visszamenőleg
            organization_id: Szűrés szervezetre
        """
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Base query for inspections with issues
        inspection_query = self.db.query(InspectionItem)\
            .join(Inspection)\
            .join(Gate)
        
        if organization_id:
            inspection_query = inspection_query.filter(Gate.organization_id == organization_id)
        
        inspection_query = inspection_query.filter(Inspection.completed_at >= start_date)
        
        # Failed inspection items (sikertelen ellenőrzési tételek)
        failed_items = inspection_query.filter(InspectionItem.status == 'failed').count()
        
        # Total inspection items
        total_items = inspection_query.count()
        
        # Failure rate
        failure_rate = (failed_items / total_items * 100) if total_items > 0 else 0
        
        # Most common failure reasons
        failure_reasons = self.db.query(
            InspectionItem.notes,
            func.count(InspectionItem.id).label('count')
        ).filter(
            InspectionItem.status == 'failed',
            InspectionItem.notes.isnot(None)
        ).join(Inspection)\
         .filter(Inspection.completed_at >= start_date)\
         .group_by(InspectionItem.notes)\
         .order_by(desc('count'))\
         .limit(10).all()
        
        # Gate type failure analysis
        gate_failure_stats = self.db.query(
            Gate.gate_type,
            func.count(InspectionItem.id).label('total_items'),
            func.count(case((InspectionItem.status == 'failed', 1))).label('failed_items')
        ).join(Inspection)\
         .join(Gate)\
         .filter(Inspection.completed_at >= start_date)\
         .group_by(Gate.gate_type).all()
        
        gate_failure_analysis = []
        for gate_type, total, failed in gate_failure_stats:
            failure_pct = (failed / total * 100) if total > 0 else 0
            gate_failure_analysis.append({
                'gate_type': gate_type,
                'total_items': total,
                'failed_items': failed,
                'failure_rate': round(failure_pct, 1)
            })
        
        # Daily error trend
        daily_errors = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            day_failed = inspection_query.filter(
                Inspection.completed_at >= day_start,
                Inspection.completed_at <= day_end,
                InspectionItem.status == 'failed'
            ).count()
            
            day_total = inspection_query.filter(
                Inspection.completed_at >= day_start,
                Inspection.completed_at <= day_end
            ).count()
            
            day_failure_rate = (day_failed / day_total * 100) if day_total > 0 else 0
            
            daily_errors.append(ChartDataPoint(
                label=day.strftime("%m-%d"),
                value=round(day_failure_rate, 1),
                date=day_start
            ))
        
        # Work order correlation (munkalapcorrelation)
        # Find gates with high failure rates and work orders
        problematic_gates = self.db.query(
            Gate.id,
            Gate.name,
            Gate.gate_type,
            func.count(InspectionItem.id).label('total_items'),
            func.count(case((InspectionItem.status == 'failed', 1))).label('failed_items'),
            func.count(WorkOrder.id).label('work_orders')
        ).join(Inspection)\
         .join(InspectionItem)\
         .outerjoin(WorkOrder, Gate.id == WorkOrder.gate_id)\
         .filter(Inspection.completed_at >= start_date)\
         .group_by(Gate.id, Gate.name, Gate.gate_type)\
         .having(func.count(case((InspectionItem.status == 'failed', 1))) > 0)\
         .order_by(desc('failed_items'))\
         .limit(10).all()
        
        gate_correlation = []
        for gate_id, gate_name, gate_type, total, failed, work_orders in problematic_gates:
            failure_rate = (failed / total * 100) if total > 0 else 0
            gate_correlation.append({
                'gate_id': gate_id,
                'gate_name': gate_name,
                'gate_type': gate_type,
                'failure_rate': round(failure_rate, 1),
                'failed_items': failed,
                'work_orders': work_orders,
                'correlation_score': round(failure_rate * work_orders / 100, 2)
            })
        
        return {
            'summary': {
                'total_inspection_items': total_items,
                'failed_items': failed_items,
                'overall_failure_rate': round(failure_rate, 1),
                'top_failure_reasons': [
                    {'reason': reason, 'count': count} for reason, count in failure_reasons
                ]
            },
            'daily_error_chart': [
                {'label': dp.label, 'value': dp.value, 'date': dp.date.isoformat() if dp.date else None}
                for dp in daily_errors
            ],
            'gate_type_failures': gate_failure_analysis,
            'problematic_gates': gate_correlation,
            'kpis': [
                KPIMetric(
                    name="Összesített Hibaarány",
                    value=failure_rate,
                    unit="%",
                    target=5.0,
                    status="critical" if failure_rate > 15 else "warning" if failure_rate > 5 else "normal"
                ),
                KPIMetric(
                    name="Sikertelen Tételek",
                    value=failed_items,
                    unit="db",
                    status="warning" if failed_items > 50 else "normal"
                ),
                KPIMetric(
                    name="Problémás Kapuk",
                    value=len(gate_correlation),
                    unit="db",
                    status="warning" if len(gate_correlation) > 5 else "normal"
                )
            ]
        }
    
    # =============================================================================
    # EXPORT FUNCTIONS - EXPORT FUNKCIÓK
    # =============================================================================
    
    def export_due_inspections_csv(
        self,
        days_ahead: int = 30,
        organization_id: Optional[int] = None
    ) -> bytes:
        """Export due inspections to CSV"""
        
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        query = self.db.query(
            Inspection.id,
            Inspection.inspection_type,
            Inspection.scheduled_date,
            Inspection.status,
            Gate.name.label('gate_name'),
            Gate.gate_type,
            Gate.location
        ).join(Gate)
        
        if organization_id:
            query = query.filter(Gate.organization_id == organization_id)
        
        inspections = query.filter(
            Inspection.scheduled_date <= cutoff_date,
            Inspection.status.in_(['scheduled', 'in_progress'])
        ).order_by(Inspection.scheduled_date).all()
        
        # Convert to DataFrame
        data = []
        for insp in inspections:
            days_until = (insp.scheduled_date - datetime.now()).days
            status_hu = {
                'scheduled': 'Ütemezett',
                'in_progress': 'Folyamatban',
                'completed': 'Befejezett'
            }.get(insp.status, insp.status)
            
            data.append({
                'Ellenőrzés ID': insp.id,
                'Típus': insp.inspection_type,
                'Kapu': insp.gate_name,
                'Kapu típus': insp.gate_type,
                'Helyszín': insp.location,
                'Tervezett dátum': insp.scheduled_date.strftime('%Y-%m-%d %H:%M'),
                'Napok hátra': days_until,
                'Állapot': status_hu,
                'Sürgősség': 'LEJÁRT' if days_until < 0 else 'SÜRGŐS' if days_until <= 3 else 'NORMÁL'
            })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        return output.getvalue().encode('utf-8-sig')
    
    def export_sla_report_excel(
        self,
        days_back: int = 30,
        organization_id: Optional[int] = None
    ) -> bytes:
        """Export SLA report to Excel with multiple sheets"""
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Get SLA analytics data
        sla_data = self.get_sla_analytics(days_back, organization_id)
        
        # Create Excel writer
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Summary sheet
            summary_df = pd.DataFrame([{
                'Metrika': 'Összes munkalap',
                'Érték': sla_data['summary']['total_work_orders'],
                'Egység': 'db'
            }, {
                'Metrika': 'SLA túllépések',
                'Érték': sla_data['summary']['sla_breached'],
                'Egység': 'db'
            }, {
                'Metrika': 'SLA megfelelési arány',
                'Érték': sla_data['summary']['sla_compliance_rate'],
                'Egység': '%'
            }, {
                'Metrika': 'Átlagos megoldási idő',
                'Érték': sla_data['summary']['avg_resolution_hours'],
                'Egység': 'óra'
            }])
            summary_df.to_excel(writer, sheet_name='Összefoglaló', index=False)
            
            # Daily performance
            daily_df = pd.DataFrame(sla_data['daily_sla_chart'])
            daily_df['date'] = pd.to_datetime(daily_df['date']).dt.strftime('%Y-%m-%d')
            daily_df.columns = ['Dátum', 'SLA megfelelés (%)', 'Dátum (ISO)']
            daily_df = daily_df[['Dátum', 'SLA megfelelés (%)']]
            daily_df.to_excel(writer, sheet_name='Napi teljesítmény', index=False)
            
            # Priority analysis
            priority_df = pd.DataFrame(sla_data['priority_analysis'])
            priority_df.columns = ['Prioritás', 'Összes munkalap', 'SLA túllépés', 'Megfelelési arány (%)']
            priority_df.to_excel(writer, sheet_name='Prioritás elemzés', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def export_error_statistics_csv(
        self,
        days_back: int = 30,
        organization_id: Optional[int] = None
    ) -> bytes:
        """Export error statistics to CSV"""
        
        error_data = self.get_error_statistics(days_back, organization_id)
        
        # Prepare data for export
        export_data = []
        
        # Add summary
        export_data.append({
            'Kategória': 'Összefoglaló',
            'Metrika': 'Összes ellenőrzési tétel',
            'Érték': error_data['summary']['total_inspection_items'],
            'Egység': 'db'
        })
        export_data.append({
            'Kategória': 'Összefoglaló',
            'Metrika': 'Sikertelen tételek',
            'Érték': error_data['summary']['failed_items'],
            'Egység': 'db'
        })
        export_data.append({
            'Kategória': 'Összefoglaló',
            'Metrika': 'Hibaarány',
            'Érték': error_data['summary']['overall_failure_rate'],
            'Egység': '%'
        })
        
        # Add gate type failures
        for gate_data in error_data['gate_type_failures']:
            export_data.append({
                'Kategória': 'Kaputípus hibák',
                'Metrika': f"{gate_data['gate_type']} - hibaarány",
                'Érték': gate_data['failure_rate'],
                'Egység': '%'
            })
        
        # Add problematic gates
        for gate_data in error_data['problematic_gates']:
            export_data.append({
                'Kategória': 'Problémás kapuk',
                'Metrika': f"{gate_data['gate_name']} - hibaarány",
                'Érték': gate_data['failure_rate'],
                'Egység': '%'
            })
        
        df = pd.DataFrame(export_data)
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        return output.getvalue().encode('utf-8-sig')
    
    # =============================================================================
    # COMBINED DASHBOARD DATA - KOMBINÁLT DASHBOARD ADATOK
    # =============================================================================
    
    def get_dashboard_analytics(
        self,
        organization_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get combined analytics data for dashboard
        Kombinált elemzési adatok dashboard-hoz
        """
        
        # Get all analytics
        due_inspections = self.get_due_inspections_analytics(30, organization_id)
        sla_analytics = self.get_sla_analytics(days_back, organization_id)
        error_stats = self.get_error_statistics(days_back, organization_id)
        
        # Combine KPIs
        all_kpis = (
            due_inspections['kpis'] +
            sla_analytics['kpis'] +
            error_stats['kpis']
        )
        
        return {
            'kpis': [
                {
                    'name': kpi.name,
                    'value': kpi.value,
                    'unit': kpi.unit,
                    'trend': kpi.trend,
                    'target': kpi.target,
                    'status': kpi.status
                } for kpi in all_kpis
            ],
            'charts': {
                'due_inspections': due_inspections['daily_due_chart'],
                'sla_performance': sla_analytics['daily_sla_chart'],
                'error_trends': error_stats['daily_error_chart']
            },
            'summaries': {
                'inspections': due_inspections['summary'],
                'sla': sla_analytics['summary'],
                'errors': error_stats['summary']
            },
            'analysis': {
                'gate_types': due_inspections['gate_type_analysis'],
                'priority_breakdown': sla_analytics['priority_analysis'],
                'problematic_gates': error_stats['problematic_gates']
            }
        }