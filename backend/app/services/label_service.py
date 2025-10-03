"""QR Code and NFC labeling system for gates."""

import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from fastapi import HTTPException
import secrets
import jwt
import structlog

from app.core.config import get_settings
from app.models.organization import Gate
from app.core.security import create_field_token, verify_field_token

logger = structlog.get_logger(__name__)
settings = get_settings()


class LabelService:
    """Service for generating QR codes and NFC labels for gates."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_field_token(self, gate_id: int, org_id: int, expires_hours: int = 24) -> str:
        """
        Generate a signed field token for mobile access.
        
        Args:
            gate_id: Gate ID
            org_id: Organization ID
            expires_hours: Token expiration in hours
            
        Returns:
            Signed JWT token for field access
        """
        try:
            payload = {
                "gate_id": gate_id,
                "org_id": org_id,
                "type": "field_access",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=expires_hours),
                "jti": secrets.token_urlsafe(16)  # Unique token ID for revocation
            }
            
            token = jwt.encode(
                payload, 
                settings.SECRET_KEY, 
                algorithm="HS256"
            )
            
            logger.info(
                "Generated field token",
                gate_id=gate_id,
                org_id=org_id,
                expires_hours=expires_hours,
                jti=payload["jti"]
            )
            
            return token
            
        except Exception as e:
            logger.error("Failed to generate field token", error=str(e))
            raise HTTPException(status_code=500, detail="Token generation failed")
    
    def verify_field_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a field token.
        
        Args:
            token: JWT field token
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            
            # Verify token type
            if payload.get("type") != "field_access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            # Check if gate exists and is accessible
            gate_id = payload.get("gate_id")
            org_id = payload.get("org_id")
            
            if not gate_id or not org_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            
            gate = self.db.query(Gate).filter(
                Gate.id == gate_id,
                Gate.org_id == org_id,
                Gate.is_active == True
            ).first()
            
            if not gate:
                raise HTTPException(status_code=404, detail="Gate not found or inactive")
            
            logger.info(
                "Field token verified",
                gate_id=gate_id,
                org_id=org_id,
                jti=payload.get("jti")
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid field token", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            raise HTTPException(status_code=500, detail="Token verification failed")
    
    def generate_qr_code(
        self, 
        gate_id: int, 
        org_id: int,
        size: int = 200,
        expires_hours: int = 24 * 7  # 1 week default
    ) -> bytes:
        """
        Generate QR code for gate access.
        
        Args:
            gate_id: Gate ID
            org_id: Organization ID  
            size: QR code size in pixels
            expires_hours: Token expiration in hours
            
        Returns:
            PNG image data as bytes
        """
        try:
            # Verify gate exists
            gate = self.db.query(Gate).filter(
                Gate.id == gate_id,
                Gate.org_id == org_id
            ).first()
            
            if not gate:
                raise HTTPException(status_code=404, detail="Gate not found")
            
            # Generate field token
            token = self.generate_field_token(gate_id, org_id, expires_hours)
            
            # Create QR code URL
            base_url = settings.FRONTEND_URL or "https://garagereg.example.com"
            qr_url = f"{base_url}/field/{token}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size // 25,  # Adjust box size based on target size
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # Create image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize to exact size
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            logger.info(
                "Generated QR code",
                gate_id=gate_id,
                org_id=org_id,
                size=size,
                url_length=len(qr_url)
            )
            
            return img_data
            
        except Exception as e:
            logger.error("QR code generation failed", error=str(e))
            raise HTTPException(status_code=500, detail="QR code generation failed")
    
    def generate_label_image(
        self,
        gate_id: int,
        org_id: int,
        label_type: str = "standard",
        width: int = 400,
        height: int = 300
    ) -> bytes:
        """
        Generate a complete label with QR code and gate information.
        
        Args:
            gate_id: Gate ID
            org_id: Organization ID
            label_type: Label type (standard, compact, zebra, brother)
            width: Label width in pixels
            height: Label height in pixels
            
        Returns:
            PNG image data as bytes
        """
        try:
            # Get gate information
            gate = self.db.query(Gate).filter(
                Gate.id == gate_id,
                Gate.org_id == org_id
            ).first()
            
            if not gate:
                raise HTTPException(status_code=404, detail="Gate not found")
            
            # Create label image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to load font, fallback to default if not available
            try:
                title_font = ImageFont.truetype("arial.ttf", 20)
                text_font = ImageFont.truetype("arial.ttf", 14)
                small_font = ImageFont.truetype("arial.ttf", 10)
            except OSError:
                # Fallback to default font
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Generate QR code (smaller for label)
            qr_size = min(width // 3, height - 40)
            qr_data = self.generate_qr_code(gate_id, org_id, size=qr_size)
            qr_img = Image.open(io.BytesIO(qr_data))
            
            # Position QR code
            qr_x = 10
            qr_y = (height - qr_size) // 2
            img.paste(qr_img, (qr_x, qr_y))
            
            # Add text information
            text_x = qr_x + qr_size + 20
            text_y = 20
            
            # Gate name
            draw.text((text_x, text_y), gate.name, fill='black', font=title_font)
            text_y += 30
            
            # Gate code if available
            if gate.gate_code:
                draw.text((text_x, text_y), f"Code: {gate.gate_code}", fill='black', font=text_font)
                text_y += 25
            
            # Gate type
            draw.text((text_x, text_y), f"Type: {gate.gate_type.title()}", fill='black', font=text_font)
            text_y += 25
            
            # Manufacturer and model
            if gate.manufacturer:
                manufacturer_text = gate.manufacturer
                if gate.model:
                    manufacturer_text += f" {gate.model}"
                draw.text((text_x, text_y), manufacturer_text, fill='black', font=text_font)
                text_y += 25
            
            # Serial number
            if gate.serial_number:
                draw.text((text_x, text_y), f"S/N: {gate.serial_number}", fill='black', font=small_font)
                text_y += 20
            
            # Installation date
            if gate.installation_date:
                install_date = gate.installation_date.strftime("%Y-%m-%d")
                draw.text((text_x, text_y), f"Installed: {install_date}", fill='black', font=small_font)
                text_y += 20
            
            # Footer with organization info
            footer_y = height - 30
            draw.text((10, footer_y), "GarageReg - Gate Management System", fill='gray', font=small_font)
            
            # Generated timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            draw.text((width - 120, footer_y), f"Generated: {timestamp}", fill='gray', font=small_font)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            logger.info(
                "Generated label image",
                gate_id=gate_id,
                org_id=org_id,
                label_type=label_type,
                width=width,
                height=height
            )
            
            return img_data
            
        except Exception as e:
            logger.error("Label generation failed", error=str(e))
            raise HTTPException(status_code=500, detail="Label generation failed")
    
    def generate_nfc_data(self, gate_id: int, org_id: int, expires_hours: int = 24 * 30) -> Dict[str, str]:
        """
        Generate NFC tag data for gate access.
        
        Args:
            gate_id: Gate ID
            org_id: Organization ID
            expires_hours: Token expiration in hours (default 30 days)
            
        Returns:
            Dictionary with NFC data
        """
        try:
            # Verify gate exists
            gate = self.db.query(Gate).filter(
                Gate.id == gate_id,
                Gate.org_id == org_id
            ).first()
            
            if not gate:
                raise HTTPException(status_code=404, detail="Gate not found")
            
            # Generate long-lived token for NFC
            token = self.generate_field_token(gate_id, org_id, expires_hours)
            
            # Create NFC URL
            base_url = settings.FRONTEND_URL or "https://garagereg.example.com"
            nfc_url = f"{base_url}/field/{token}"
            
            nfc_data = {
                "url": nfc_url,
                "token": token,
                "gate_name": gate.name,
                "gate_id": str(gate_id),
                "expires_at": (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat(),
                "type": "garagereg_gate_access"
            }
            
            logger.info(
                "Generated NFC data",
                gate_id=gate_id,
                org_id=org_id,
                expires_hours=expires_hours
            )
            
            return nfc_data
            
        except Exception as e:
            logger.error("NFC data generation failed", error=str(e))
            raise HTTPException(status_code=500, detail="NFC data generation failed")
    
    def rotate_gate_tokens(self, gate_id: int, org_id: int) -> Dict[str, Any]:
        """
        Rotate all tokens for a gate (invalidates old tokens).
        
        Args:
            gate_id: Gate ID
            org_id: Organization ID
            
        Returns:
            New token information
        """
        try:
            # Verify gate exists
            gate = self.db.query(Gate).filter(
                Gate.id == gate_id,
                Gate.org_id == org_id
            ).first()
            
            if not gate:
                raise HTTPException(status_code=404, detail="Gate not found")
            
            # Update gate's token_version to invalidate old tokens
            if not hasattr(gate, 'token_version'):
                gate.token_version = 1
            else:
                gate.token_version = (gate.token_version or 0) + 1
            
            # Update last_token_rotation timestamp
            gate.last_token_rotation = datetime.utcnow()
            
            self.db.commit()
            
            # Generate new tokens
            qr_token = self.generate_field_token(gate_id, org_id, expires_hours=24 * 7)  # 1 week
            nfc_token = self.generate_field_token(gate_id, org_id, expires_hours=24 * 30)  # 30 days
            
            result = {
                "gate_id": gate_id,
                "token_version": gate.token_version,
                "qr_token": qr_token,
                "nfc_token": nfc_token,
                "qr_expires_hours": 24 * 7,
                "nfc_expires_hours": 24 * 30,
                "rotated_at": gate.last_token_rotation.isoformat()
            }
            
            logger.info(
                "Rotated gate tokens",
                gate_id=gate_id,
                org_id=org_id,
                token_version=gate.token_version
            )
            
            return result
            
        except Exception as e:
            logger.error("Token rotation failed", error=str(e))
            raise HTTPException(status_code=500, detail="Token rotation failed")


def create_zebra_zpl_template(gate_name: str, gate_code: str, qr_data: str) -> str:
    """
    Create Zebra ZPL template for label printing.
    
    Args:
        gate_name: Gate name
        gate_code: Gate code
        qr_data: QR code data (base64 encoded)
        
    Returns:
        ZPL template string
    """
    zpl_template = f"""^XA
^LH0,0
^FO50,50^GFA,1024,1024,16,{qr_data}^FS
^FO200,50^A0N,28,28^FD{gate_name}^FS
^FO200,90^A0N,20,20^FDCode: {gate_code}^FS
^FO200,120^A0N,16,16^FDGarageReg System^FS
^FO50,200^A0N,12,12^FDGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}^FS
^XZ"""
    
    return zpl_template


def create_brother_ptouch_template(gate_name: str, gate_code: str) -> str:
    """
    Create Brother P-Touch template for label printing.
    
    Args:
        gate_name: Gate name
        gate_code: Gate code
        
    Returns:
        Brother template string (simplified)
    """
    template = f"""[LABEL]
SIZE=36mm,12mm
ORIENTATION=LANDSCAPE

[TEXT]
FONT=Arial,12
POSITION=5,2
TEXT={gate_name}

[TEXT]
FONT=Arial,8
POSITION=5,6
TEXT=Code: {gate_code}

[TEXT]  
FONT=Arial,6
POSITION=5,10
TEXT=GarageReg System
"""
    
    return template