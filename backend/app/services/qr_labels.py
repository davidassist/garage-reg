"""
QR címkék és gyári QR kezelése
"""
import io
import csv
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, grey, blue
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.organization import Gate, Building, Site, Client
from app.core.config import settings
from app.core.security import generate_secure_token


class QRLabelService:
    """QR címkék és gyári QR kezelő szolgáltatás"""
    
    def __init__(self):
        self.base_url = settings.BASE_URL or "https://garagereg.example.com"
        
    def generate_gate_qr_url(self, gate: Gate) -> str:
        """Kapu QR URL generálása"""
        # Factory QR token használata, ha van
        if gate.factory_qr_token:
            token = gate.factory_qr_token
        else:
            # Dinamikus token generálása
            token = f"{gate.id}-{gate.token_version}-{generate_secure_token()[:8]}"
            
        return urljoin(self.base_url, f"/gate/{token}")
    
    def create_qr_code(self, data: str, size: int = 200) -> Image.Image:
        """QR kód kép generálása"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Színes QR kód létrehozása
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 100, 200))
        )
        
        # Méretezés
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        return img
    
    def create_label_image(self, gate: Gate, qr_size: int = 150) -> Image.Image:
        """Egyetlen címke kép létrehozása"""
        # Címke mérete (70x30mm @ 300dpi)
        label_width = int(70 * 300 / 25.4)  # ~827px
        label_height = int(30 * 300 / 25.4)  # ~354px
        
        # Új kép létrehozása
        img = Image.new('RGB', (label_width, label_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Betűtípusok
            title_font = ImageFont.truetype("arial.ttf", 28)
            text_font = ImageFont.truetype("arial.ttf", 18)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            # Fallback alapértelmezett betűtípusokra
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # QR kód generálása és pozicionálása
        qr_url = self.generate_gate_qr_url(gate)
        qr_img = self.create_qr_code(qr_url, qr_size)
        
        # QR kód elhelyezése jobb oldalon
        qr_x = label_width - qr_size - 20
        qr_y = (label_height - qr_size) // 2
        img.paste(qr_img, (qr_x, qr_y))
        
        # Szöveges információk bal oldalon
        text_x = 20
        y_pos = 30
        
        # Cím
        gate_name = gate.display_name or gate.name
        if len(gate_name) > 20:
            gate_name = gate_name[:20] + "..."
        draw.text((text_x, y_pos), gate_name, fill='black', font=title_font)
        y_pos += 40
        
        # Kapu kód
        if gate.gate_code:
            draw.text((text_x, y_pos), f"Kód: {gate.gate_code}", fill='black', font=text_font)
            y_pos += 25
        
        # Típus
        draw.text((text_x, y_pos), f"Típus: {gate.gate_type}", fill='black', font=text_font)
        y_pos += 25
        
        # Gyártó és modell
        if gate.manufacturer or gate.model:
            mfg_model = f"{gate.manufacturer or ''} {gate.model or ''}".strip()
            if mfg_model:
                if len(mfg_model) > 25:
                    mfg_model = mfg_model[:25] + "..."
                draw.text((text_x, y_pos), mfg_model, fill='black', font=text_font)
                y_pos += 25
        
        # Telepítés helye
        building_info = ""
        if gate.building:
            building_info = gate.building.display_name or gate.building.name
            if gate.building.site:
                site_info = gate.building.site.display_name or gate.building.site.name
                building_info = f"{site_info} / {building_info}"
                
        if building_info:
            if len(building_info) > 30:
                building_info = building_info[:30] + "..."
            draw.text((text_x, y_pos), building_info, fill='grey', font=small_font)
            y_pos += 20
        
        # Factory QR jelölés, ha van
        if gate.factory_qr_token:
            draw.text((text_x, label_height - 40), f"Gyári QR: {gate.factory_qr_token[:8]}...", 
                     fill='blue', font=small_font)
        
        # Generálás dátuma
        gen_date = datetime.now().strftime('%Y.%m.%d')
        draw.text((text_x, label_height - 20), f"Generálva: {gen_date}", 
                 fill='grey', font=small_font)
        
        return img
    
    def create_bulk_labels_pdf(
        self, 
        gates: List[Gate], 
        labels_per_row: int = 3,
        labels_per_page: int = 9
    ) -> bytes:
        """Tömeges címke PDF generálása"""
        
        buffer = io.BytesIO()
        
        # PDF létrehozása
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=15*mm,
            leftMargin=10*mm,
            rightMargin=10*mm
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story = []
        
        # Címlap fejléc
        title = Paragraph(f"QR Címkék - {len(gates)} kapu", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Címkék táblázatban
        label_data = []
        current_row = []
        
        for i, gate in enumerate(gates):
            # Címke kép létrehozása
            label_img = self.create_label_image(gate)
            
            # Kép átkonvertálása PDF-hez
            img_buffer = io.BytesIO()
            label_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            rl_img = RLImage(img_buffer, width=70*mm, height=30*mm)
            current_row.append(rl_img)
            
            # Ha a sor megtelt vagy ez az utolsó elem
            if len(current_row) == labels_per_row or i == len(gates) - 1:
                # Sor kitöltése üres cellákkal ha szükséges
                while len(current_row) < labels_per_row:
                    current_row.append("")
                    
                label_data.append(current_row)
                current_row = []
        
        # Táblázat létrehozása
        if label_data:
            table = Table(label_data, colWidths=[70*mm] * labels_per_row)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
        
        # Információs táblázat a végén
        story.append(Spacer(1, 30))
        
        info_data = [['Kapu név', 'Kód', 'Típus', 'QR URL']]
        for gate in gates:
            qr_url = self.generate_gate_qr_url(gate)
            short_url = qr_url if len(qr_url) <= 40 else qr_url[:37] + "..."
            
            info_data.append([
                gate.display_name or gate.name,
                gate.gate_code or '-',
                gate.gate_type,
                short_url
            ])
        
        info_table = Table(info_data, colWidths=[50*mm, 30*mm, 30*mm, 70*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Címke információk", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(info_table)
        
        # PDF építése
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def import_factory_qr_csv(
        self, 
        db: Session, 
        csv_content: str, 
        batch_name: Optional[str] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Gyári QR CSV import
        
        Returns:
            Tuple[success_count, error_count, error_messages]
        """
        
        success_count = 0
        error_count = 0
        errors = []
        
        if not batch_name:
            batch_name = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # CSV olvasás
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Mezők kinyerése
                    gate_identifier = row.get('gate_id') or row.get('gate_code') or row.get('kapu_id')
                    factory_token = row.get('factory_qr') or row.get('qr_token') or row.get('token')
                    
                    if not gate_identifier:
                        errors.append(f"Sor {row_num}: Hiányzó kapu azonosító")
                        error_count += 1
                        continue
                        
                    if not factory_token:
                        errors.append(f"Sor {row_num}: Hiányzó gyári QR token")
                        error_count += 1
                        continue
                    
                    # Kapu keresése
                    gate = db.query(Gate).filter(
                        or_(
                            Gate.id == gate_identifier if gate_identifier.isdigit() else None,
                            Gate.gate_code == gate_identifier,
                            Gate.name == gate_identifier
                        )
                    ).first()
                    
                    if not gate:
                        errors.append(f"Sor {row_num}: Kapu nem található: {gate_identifier}")
                        error_count += 1
                        continue
                    
                    # Duplikáció ellenőrzés
                    existing_gate = db.query(Gate).filter(
                        Gate.factory_qr_token == factory_token
                    ).first()
                    
                    if existing_gate and existing_gate.id != gate.id:
                        errors.append(
                            f"Sor {row_num}: QR token már használatban: {factory_token} "
                            f"(kapu: {existing_gate.name})"
                        )
                        error_count += 1
                        continue
                    
                    # Gyári QR hozzárendelése
                    gate.factory_qr_token = factory_token
                    gate.factory_qr_assigned_at = datetime.now()
                    gate.factory_qr_batch = batch_name
                    
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Sor {row_num}: {str(e)}")
                    error_count += 1
            
            # Változások mentése
            if success_count > 0:
                db.commit()
            
        except Exception as e:
            db.rollback()
            errors.append(f"CSV feldolgozási hiba: {str(e)}")
            error_count += 1
        
        return success_count, error_count, errors
    
    def get_gates_for_labels(
        self, 
        db: Session, 
        gate_ids: Optional[List[int]] = None,
        building_ids: Optional[List[int]] = None,
        site_ids: Optional[List[int]] = None,
        client_ids: Optional[List[int]] = None,
        include_inactive: bool = False
    ) -> List[Gate]:
        """Címkézendő kapuk lekérdezése szűrőkkel"""
        
        query = db.query(Gate).join(Building).join(Site).join(Client)
        
        # Aktív szűrő
        if not include_inactive:
            query = query.filter(Gate.is_active == True)
        
        # ID szűrők
        if gate_ids:
            query = query.filter(Gate.id.in_(gate_ids))
        elif building_ids:
            query = query.filter(Gate.building_id.in_(building_ids))
        elif site_ids:
            query = query.filter(Building.site_id.in_(site_ids))
        elif client_ids:
            query = query.filter(Site.client_id.in_(client_ids))
        
        return query.order_by(
            Client.name,
            Site.name, 
            Building.name,
            Gate.name
        ).all()
    
    def create_sample_labels(self, db: Session, count: int = 6) -> bytes:
        """Minta címkék generálása teszteléshez"""
        
        # Első néhány kapu lekérdezése
        gates = db.query(Gate).join(Building).join(Site).join(Client).limit(count).all()
        
        if not gates:
            # Ha nincs kapu, dummy adatok létrehozása
            from app.models.organization import Gate, Building, Site, Client
            
            dummy_client = Client(name="Minta Ügyfél", display_name="Minta Ügyfél Kft.")
            dummy_site = Site(name="Teszt Telephely", display_name="Teszt Telephely", client=dummy_client)
            dummy_building = Building(name="A Épület", display_name="A Épület", site=dummy_site)
            
            gates = []
            for i in range(count):
                gate = Gate(
                    name=f"Kapu-{i+1}",
                    display_name=f"Teszt Kapu {i+1}",
                    gate_code=f"GATE-{str(i+1).zfill(3)}",
                    gate_type="swing",
                    manufacturer="ACME Gates",
                    model="Model-X",
                    building=dummy_building
                )
                gates.append(gate)
        
        return self.create_bulk_labels_pdf(gates)
    
    def generate_factory_qr_mapping(
        self, 
        gate_count: int, 
        batch_name: Optional[str] = None
    ) -> str:
        """Gyári QR mapping CSV generálás"""
        
        if not batch_name:
            batch_name = f"factory_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # CSV fejléc
        writer.writerow(['gate_code', 'factory_qr', 'batch', 'generated_at'])
        
        # Sorok generálása
        for i in range(gate_count):
            gate_code = f"GATE-{str(i+1).zfill(4)}"
            factory_qr = f"FQR-{batch_name}-{generate_secure_token()[:12]}"
            generated_at = datetime.now().isoformat()
            
            writer.writerow([gate_code, factory_qr, batch_name, generated_at])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content