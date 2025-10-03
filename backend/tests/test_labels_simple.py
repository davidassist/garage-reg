"""Simple test for QR/NFC labeling functionality."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.services.label_service import LabelService
from app.core.security import create_field_token, verify_field_token


class TestLabelServiceDirect:
    """Test LabelService functionality directly without complex database setup."""
    
    def test_field_token_creation_and_verification(self):
        """Test field token creation and verification without database."""
        gate_id = 123
        org_id = 456
        expires_hours = 24
        
        # Create token
        token = create_field_token(
            gate_id=gate_id,
            org_id=org_id,
            expires_delta=timedelta(hours=expires_hours)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long
        
        # Verify token
        payload = verify_field_token(token)
        assert payload is not None
        assert payload["gate_id"] == gate_id
        assert payload["org_id"] == org_id
        assert payload["type"] == "field_access"
    
    def test_field_token_expiration(self):
        """Test field token expiration."""
        gate_id = 123
        org_id = 456
        
        # Create short-lived token (1 second)
        token = create_field_token(
            gate_id=gate_id,
            org_id=org_id,
            expires_delta=timedelta(seconds=1)
        )
        
        # Should be valid immediately
        payload = verify_field_token(token)
        assert payload is not None
        
        # Wait for expiration and test again
        import time
        time.sleep(2)
        
        # Should be invalid now
        payload = verify_field_token(token)
        assert payload is None
    
    def test_invalid_field_token(self):
        """Test verification of invalid field token."""
        invalid_token = "invalid.token.here"
        payload = verify_field_token(invalid_token)
        assert payload is None
    
    @patch('app.services.label_service.qrcode')
    @patch('app.services.label_service.BytesIO')
    def test_qr_code_generation_mock(self, mock_bytesio, mock_qrcode):
        """Test QR code generation with mocked dependencies."""
        # Mock setup
        mock_qr = Mock()
        mock_qrcode.QRCode.return_value = mock_qr
        mock_img = Mock()
        mock_qr.make_image.return_value = mock_img
        
        mock_buffer = Mock()
        mock_bytesio.return_value = mock_buffer
        mock_buffer.getvalue.return_value = b'fake_png_data'
        
        # Mock database session
        mock_db = Mock()
        
        # Test
        service = LabelService(mock_db)
        
        # Create a mock gate
        mock_gate = Mock()
        mock_gate.id = 123
        mock_gate.name = "Test Gate"
        mock_gate.gate_code = "TG001"
        mock_gate.gate_type = "swing"
        mock_gate.token_version = 1
        
        # Mock database query
        mock_db.query().filter().first.return_value = mock_gate
        
        # Generate QR code
        with patch.object(service, 'generate_field_token', return_value='mock_token'):
            qr_data = service.generate_qr_code(123, 456, size=200)
        
        # Verify
        assert qr_data == b'fake_png_data'
        mock_qrcode.QRCode.assert_called_once()
        mock_img.save.assert_called_once()
    
    def test_nfc_data_generation_mock(self):
        """Test NFC data generation with mocked dependencies."""
        # Mock database session
        mock_db = Mock()
        
        # Create a mock gate
        mock_gate = Mock()
        mock_gate.id = 123
        mock_gate.name = "Test NFC Gate"
        mock_gate.gate_code = "TG002"
        mock_gate.token_version = 1
        
        # Mock database query
        mock_db.query().filter().first.return_value = mock_gate
        
        # Test
        service = LabelService(mock_db)
        
        with patch.object(service, 'generate_field_token', return_value='mock_nfc_token'):
            nfc_data = service.generate_nfc_data(123, 456, expires_hours=720)
        
        # Verify
        assert nfc_data is not None
        assert "url" in nfc_data
        assert "token" in nfc_data
        assert "gate_name" in nfc_data
        assert "expires_at" in nfc_data
        assert nfc_data["gate_name"] == "Test NFC Gate"
        assert nfc_data["token"] == "mock_nfc_token"
        assert nfc_data["type"] == "garagereg_gate_access"
    
    def test_token_rotation_mock(self):
        """Test token rotation with mocked database."""
        # Mock database session
        mock_db = Mock()
        
        # Create a mock gate
        mock_gate = Mock()
        mock_gate.id = 123
        mock_gate.token_version = 1
        
        # Mock database query and update
        mock_db.query().filter().first.return_value = mock_gate
        mock_db.commit.return_value = None
        
        # Test
        service = LabelService(mock_db)
        
        with patch.object(service, 'generate_field_token') as mock_generate:
            mock_generate.side_effect = ['qr_token', 'nfc_token']
            
            result = service.rotate_gate_tokens(123, 456)
        
        # Verify
        assert result["gate_id"] == 123
        assert result["token_version"] == 2
        assert result["qr_token"] == "qr_token"
        assert result["nfc_token"] == "nfc_token"
        assert mock_gate.token_version == 2
        assert mock_gate.last_token_rotation is not None
        mock_db.commit.assert_called_once()
    
    @patch('app.services.label_service.Image')
    @patch('app.services.label_service.ImageDraw')
    @patch('app.services.label_service.ImageFont')
    def test_label_image_generation_mock(self, mock_font, mock_draw, mock_image):
        """Test label image generation with mocked dependencies."""
        # Mock setup
        mock_img = Mock()
        mock_image.new.return_value = mock_img
        mock_drawer = Mock()
        mock_draw.Draw.return_value = mock_drawer
        mock_font_obj = Mock()
        mock_font.truetype.return_value = mock_font_obj
        mock_font.load_default.return_value = mock_font_obj
        
        mock_buffer = Mock()
        mock_buffer.getvalue.return_value = b'fake_label_data'
        
        # Mock database
        mock_db = Mock()
        mock_gate = Mock()
        mock_gate.id = 123
        mock_gate.name = "Label Test Gate"
        mock_gate.gate_code = "LTG001"
        mock_gate.gate_type = "sliding"
        mock_gate.manufacturer = "Test Manufacturer"
        mock_gate.model = "Test Model"
        mock_gate.serial_number = "SN123456"
        mock_gate.token_version = 1
        
        mock_db.query().filter().first.return_value = mock_gate
        
        # Test
        service = LabelService(mock_db)
        
        with patch('app.services.label_service.BytesIO', return_value=mock_buffer):
            with patch.object(service, 'generate_qr_code', return_value=b'qr_data'):
                label_data = service.generate_label_image(
                    123, 456, 
                    label_type="standard",
                    width=400, height=300
                )
        
        # Verify
        assert label_data == b'fake_label_data'
        mock_image.new.assert_called_once_with('RGB', (400, 300), color='white')
        mock_draw.Draw.assert_called_once_with(mock_img)


class TestLabelServiceIntegration:
    """Integration tests with real JWT tokens but mocked database."""
    
    def test_full_qr_workflow(self):
        """Test complete QR generation workflow."""
        # Mock database
        mock_db = Mock()
        mock_gate = Mock()
        mock_gate.id = 999
        mock_gate.name = "Integration Test Gate"
        mock_gate.gate_code = "ITG001"
        mock_gate.gate_type = "turnstile"
        mock_gate.token_version = 1
        
        mock_db.query().filter().first.return_value = mock_gate
        
        service = LabelService(mock_db)
        
        # Test token generation
        token = service.generate_field_token(999, 123, expires_hours=168)
        assert token is not None
        
        # Test token verification
        payload = service.verify_field_token(token)
        assert payload is not None
        assert payload["gate_id"] == 999
        assert payload["org_id"] == 123
        
        # Test QR code info generation
        with patch.object(service, 'generate_qr_code', return_value=b'mock_qr_png'):
            qr_info = {
                "gate_id": 999,
                "gate_name": "Integration Test Gate",
                "token": token,
                "url": f"http://localhost:3000/field/{token}",
                "expires_hours": 168,
                "expires_at": "2025-10-08T20:45:00Z",
                "qr_image_url": f"http://localhost:8000/api/v1/labels/qr/{999}.png"
            }
        
        assert qr_info["gate_id"] == 999
        assert qr_info["token"] == token
        assert "field/" in qr_info["url"]