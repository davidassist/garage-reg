"""
PDF Report Generation Service for Work Orders.

PDF riport generálási szolgáltatás munkarendelésekhez.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.models.tickets import WorkOrder, PartUsage, WorkOrderTimeLog
from app.models.auth import User
from app.models.organization import Gate


class PDFReportService:
    """
    Service for generating PDF reports from work orders.
    
    Szolgáltatás PDF riportok generálásához munkarendelésekből.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyBold',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10
        ))
    
    def generate_work_order_completion_report(
        self, 
        work_order: WorkOrder,
        gate: Optional[Gate] = None,
        technician: Optional[User] = None,
        parts_used: Optional[List[PartUsage]] = None,
        time_logs: Optional[List[WorkOrderTimeLog]] = None
    ) -> BytesIO:
        """
        Generate a comprehensive completion report for a work order.
        
        Teljes befejezési riport generálása munkarendeléshez.
        """
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content elements)
        story = []
        
        # Title
        story.append(Paragraph("Work Order Completion Report", self.styles['CustomTitle']))
        story.append(Paragraph("Munkarendelés Befejezési Riport", self.styles['SubTitle']))
        story.append(Spacer(1, 20))
        
        # Work order header information
        self._add_work_order_header(story, work_order, gate, technician)
        
        # Work details
        self._add_work_details(story, work_order)
        
        # Parts used section
        if parts_used:
            self._add_parts_section(story, parts_used)
        
        # Time logs section
        if time_logs:
            self._add_time_logs_section(story, time_logs)
        
        # Cost summary
        self._add_cost_summary(story, work_order, parts_used, time_logs)
        
        # Completion details
        self._add_completion_details(story, work_order)
        
        # Footer with generation details
        self._add_report_footer(story)
        
        # Build PDF
        doc.build(story)
        
        # Return buffer
        buffer.seek(0)
        return buffer
    
    def _add_work_order_header(
        self, 
        story: List, 
        work_order: WorkOrder, 
        gate: Optional[Gate], 
        technician: Optional[User]
    ):
        """Add work order header information."""
        
        header_data = [
            ["Work Order Number:", work_order.work_order_number],
            ["Title:", work_order.title],
            ["Status:", work_order.status.value.replace('_', ' ').title()],
            ["Priority:", work_order.priority.value.title()],
            ["Work Type:", work_order.work_type],
            ["Category:", work_order.work_category or "N/A"],
        ]
        
        if gate:
            header_data.append(["Gate:", f"{gate.gate_code} - {gate.name}"])
            if gate.site and gate.site.name:
                header_data.append(["Location:", gate.site.name])
        
        if technician:
            header_data.append(["Technician:", technician.display_name or technician.username])
        
        # Create header table
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
    
    def _add_work_details(self, story: List, work_order: WorkOrder):
        """Add work details section."""
        
        story.append(Paragraph("Work Details / Munka Részletek", self.styles['SubTitle']))
        
        if work_order.description:
            story.append(Paragraph("Description:", self.styles['BodyBold']))
            story.append(Paragraph(work_order.description, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        if work_order.instructions:
            story.append(Paragraph("Instructions:", self.styles['BodyBold']))
            story.append(Paragraph(work_order.instructions, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        if work_order.safety_requirements:
            story.append(Paragraph("Safety Requirements:", self.styles['BodyBold']))
            story.append(Paragraph(work_order.safety_requirements, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Time information
        time_data = []
        if work_order.scheduled_start:
            time_data.append(["Scheduled Start:", work_order.scheduled_start.strftime("%Y-%m-%d %H:%M")])
        if work_order.actual_start:
            time_data.append(["Actual Start:", work_order.actual_start.strftime("%Y-%m-%d %H:%M")])
        if work_order.actual_end:
            time_data.append(["Completion Time:", work_order.actual_end.strftime("%Y-%m-%d %H:%M")])
        if work_order.actual_duration_hours:
            time_data.append(["Duration:", f"{work_order.actual_duration_hours} hours"])
        
        if time_data:
            time_table = Table(time_data, colWidths=[2*inch, 2*inch])
            time_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(time_table)
        
        story.append(Spacer(1, 15))
    
    def _add_parts_section(self, story: List, parts_used: List[PartUsage]):
        """Add parts used section."""
        
        story.append(Paragraph("Parts Used / Felhasznált Alkatrészek", self.styles['SubTitle']))
        
        # Create parts table
        parts_data = [["Part Number", "Description", "Qty", "Unit Cost", "Total Cost"]]
        
        for part in parts_used:
            parts_data.append([
                part.part_number,
                part.part_name,
                str(part.quantity_used),
                f"${part.unit_cost or 0:.2f}",
                f"${part.total_cost or 0:.2f}"
            ])
        
        parts_table = Table(parts_data, colWidths=[1.2*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch])
        parts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(parts_table)
        story.append(Spacer(1, 15))
    
    def _add_time_logs_section(self, story: List, time_logs: List[WorkOrderTimeLog]):
        """Add time logs section."""
        
        story.append(Paragraph("Labor Time Logs / Munkaidő Naplók", self.styles['SubTitle']))
        
        # Create time logs table
        time_data = [["Date", "Activity", "Duration (hrs)", "Rate", "Cost"]]
        
        for log in time_logs:
            time_data.append([
                log.start_time.strftime("%Y-%m-%d") if log.start_time else "N/A",
                log.activity_type,
                f"{log.duration_hours or 0:.2f}",
                f"${log.hourly_rate or 0:.2f}" if log.hourly_rate else "N/A",
                f"${log.total_cost or 0:.2f}"
            ])
        
        time_table = Table(time_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
        time_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(time_table)
        story.append(Spacer(1, 15))
    
    def _add_cost_summary(
        self, 
        story: List, 
        work_order: WorkOrder,
        parts_used: Optional[List[PartUsage]],
        time_logs: Optional[List[WorkOrderTimeLog]]
    ):
        """Add cost summary section."""
        
        story.append(Paragraph("Cost Summary / Költség Összesítő", self.styles['SubTitle']))
        
        # Calculate totals
        parts_cost = sum(p.total_cost or 0 for p in (parts_used or []))
        labor_cost = sum(t.total_cost or 0 for t in (time_logs or []))
        total_cost = parts_cost + labor_cost
        
        cost_data = [
            ["Parts Cost:", f"${parts_cost:.2f}"],
            ["Labor Cost:", f"${labor_cost:.2f}"],
            ["Total Cost:", f"${total_cost:.2f}"]
        ]
        
        if work_order.cost_estimate:
            cost_data.append(["Original Estimate:", f"${work_order.cost_estimate:.2f}"])
            variance = total_cost - float(work_order.cost_estimate)
            cost_data.append(["Variance:", f"${variance:.2f}"])
        
        cost_table = Table(cost_data, colWidths=[2*inch, 1.5*inch])
        cost_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            # Highlight total row
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ]))
        
        story.append(cost_table)
        story.append(Spacer(1, 15))
    
    def _add_completion_details(self, story: List, work_order: WorkOrder):
        """Add completion details section."""
        
        story.append(Paragraph("Completion Details / Befejezési Részletek", self.styles['SubTitle']))
        
        if work_order.completion_notes:
            story.append(Paragraph("Completion Notes:", self.styles['BodyBold']))
            story.append(Paragraph(work_order.completion_notes, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Progress
        story.append(Paragraph(f"Progress: {work_order.progress_percentage}% Complete", self.styles['BodyBold']))
        story.append(Spacer(1, 10))
        
        # Status history could be added here if available
        
        story.append(Spacer(1, 15))
    
    def _add_report_footer(self, story: List):
        """Add report generation footer."""
        
        story.append(Spacer(1, 30))
        
        footer_text = f"""
        <br/><br/>
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        <br/>
        GarageReg Work Order Management System
        """
        
        story.append(Paragraph(footer_text, self.styles['Normal']))


class WorkOrderPDFController:
    """
    Controller for work order PDF operations.
    
    Kontroller munkarendelés PDF műveletekkhez.
    """
    
    def __init__(self, pdf_service: PDFReportService = None):
        self.pdf_service = pdf_service or PDFReportService()
    
    def generate_completion_report(
        self,
        work_order: WorkOrder,
        include_parts: bool = True,
        include_time_logs: bool = True
    ) -> BytesIO:
        """
        Generate completion report for a work order.
        
        Befejezési riport generálása munkarendeléshez.
        """
        
        # Get related data
        gate = work_order.gate if hasattr(work_order, 'gate') else None
        technician = work_order.assigned_technician if hasattr(work_order, 'assigned_technician') else None
        
        parts_used = None
        if include_parts and hasattr(work_order, 'part_usages'):
            parts_used = work_order.part_usages
        
        time_logs = None  
        if include_time_logs and hasattr(work_order, 'time_logs'):
            time_logs = work_order.time_logs
        
        return self.pdf_service.generate_work_order_completion_report(
            work_order=work_order,
            gate=gate,
            technician=technician,
            parts_used=parts_used,
            time_logs=time_logs
        )