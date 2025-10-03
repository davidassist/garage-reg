"""Tests for QR/NFC labeling functionality."""

import pytest
import base64
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.orm import Session

from app.services.label_service import LabelService
from app.schemas.labels import QRCodeResponse, NFCDataResponse, TokenRotationResponse
from app.models.organization import Gate


class TestLabelService:
    """Test the LabelService directly."""
    
    @pytest.mark.asyncio
    async def test_generate_field_token(self, db_session: Session, test_org_id: int):
        """Test field token generation."""
        service = LabelService(db_session)
        
        # Create test gate
        gate = Gate(
            org_id=test_org_id,
            building_id=1,  # Assuming test building exists
            name="Test Gate",
            gate_type="swing",
            status="operational"
        )
        db_session.add(gate)
        db_session.commit()
        
        # Generate token
        token = service.generate_field_token(gate.id, test_org_id, expires_hours=24)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long
    
    @pytest.mark.asyncio
    async def test_verify_field_token(self, db_session: Session, test_org_id: int):
        """Test field token verification."""
        service = LabelService(db_session)
        
        # Create test gate
        gate = Gate(
            org_id=test_org_id,
            building_id=1,
            name="Test Gate for Token",
            gate_type="sliding",
            status="operational"
        )
        db_session.add(gate)
        db_session.commit()
        
        # Generate and verify token
        token = service.generate_field_token(gate.id, test_org_id, expires_hours=24)
        payload = service.verify_field_token(token)
        
        assert payload["gate_id"] == gate.id
        assert payload["org_id"] == test_org_id
        assert payload["type"] == "field_access"
        assert "exp" in payload
        assert "jti" in payload
    
    @pytest.mark.asyncio
    async def test_generate_qr_code(self, db_session: Session, test_org_id: int):
        """Test QR code generation."""
        service = LabelService(db_session)
        
        # Create test gate
        gate = Gate(
            org_id=test_org_id,
            building_id=1,
            name="QR Test Gate",
            gate_type="barrier",
            status="operational"
        )
        db_session.add(gate)
        db_session.commit()
        
        # Generate QR code
        qr_data = service.generate_qr_code(gate.id, test_org_id, size=200)
        
        assert qr_data is not None
        assert isinstance(qr_data, bytes)
        assert len(qr_data) > 100  # PNG data should be substantial
        
        # Check PNG signature
        assert qr_data[:8] == b'\x89PNG\r\n\x1a\n'
    
    @pytest.mark.asyncio
    async def test_generate_nfc_data(self, db_session: Session, test_org_id: int):
        """Test NFC data generation."""
        service = LabelService(db_session)
        
        # Create test gate
        gate = Gate(
            org_id=test_org_id,
            building_id=1,
            name="NFC Test Gate",
            gate_type="turnstile", 
            status="operational"
        )
        db_session.add(gate)
        db_session.commit()
        
        # Generate NFC data
        nfc_data = service.generate_nfc_data(gate.id, test_org_id, expires_hours=720)
        
        assert nfc_data is not None
        assert "url" in nfc_data
        assert "token" in nfc_data
        assert "gate_name" in nfc_data
        assert "expires_at" in nfc_data
        assert nfc_data["gate_name"] == "NFC Test Gate"
        assert nfc_data["type"] == "garagereg_gate_access"
    
    @pytest.mark.asyncio
    async def test_token_rotation(self, db_session: Session, test_org_id: int):
        """Test token rotation functionality."""
        service = LabelService(db_session)
        
        # Create test gate
        gate = Gate(
            org_id=test_org_id,
            building_id=1,
            name="Rotation Test Gate",
            gate_type="swing",
            status="operational",
            token_version=1
        )
        db_session.add(gate)
        db_session.commit()
        
        original_version = gate.token_version
        
        # Rotate tokens
        result = service.rotate_gate_tokens(gate.id, test_org_id)
        
        # Refresh gate from DB
        db_session.refresh(gate)
        
        assert result["gate_id"] == gate.id
        assert result["token_version"] == original_version + 1
        assert result["qr_token"] != result["nfc_token"]
        assert gate.token_version == original_version + 1
        assert gate.last_token_rotation is not None
    
    @pytest.mark.asyncio
    async def test_generate_label_image(self, db_session: Session, test_org_id: int):
        """Test label image generation."""
        service = LabelService(db_session)
        
        # Create test gate with detailed info
        gate = Gate(
            org_id=test_org_id,
            building_id=1,
            name="Label Test Gate",
            gate_code="LTG001",
            gate_type="sliding",
            manufacturer="Test Manufacturer",
            model="Test Model",
            serial_number="SN123456",
            status="operational"
        )
        db_session.add(gate)
        db_session.commit()
        
        # Generate label
        label_data = service.generate_label_image(
            gate.id, 
            test_org_id, 
            label_type="standard",
            width=400,
            height=300
        )
        
        assert label_data is not None
        assert isinstance(label_data, bytes)
        assert len(label_data) > 1000  # Label should be substantial
        
        # Check PNG signature
        assert label_data[:8] == b'\x89PNG\r\n\x1a\n'


class TestLabelAPI:
    """Test label API endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_qr_code_endpoint(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test QR code generation endpoint."""
        response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}.png?size=200&expires_hours=24",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        assert "gate_" in response.headers["content-disposition"]
        assert len(response.content) > 100
    
    @pytest.mark.asyncio
    async def test_get_qr_code_info(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test QR code info endpoint."""
        response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}?expires_hours=168",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["gate_id"] == test_gate_id
        assert "gate_name" in data
        assert "token" in data
        assert "url" in data
        assert data["expires_hours"] == 168
        assert "qr_image_url" in data
    
    @pytest.mark.asyncio
    async def test_generate_nfc_data_endpoint(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test NFC data generation endpoint."""
        response = await client.get(
            f"/api/v1/labels/nfc/{test_gate_id}?expires_hours=720",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["gate_id"] == test_gate_id
        assert "nfc_data" in data
        assert data["expires_hours"] == 720
        
        nfc_data = data["nfc_data"]
        assert "url" in nfc_data
        assert "token" in nfc_data
        assert "gate_name" in nfc_data
    
    @pytest.mark.asyncio
    async def test_rotate_gate_tokens_endpoint(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test token rotation endpoint."""
        response = await client.post(
            f"/api/v1/labels/rotate/{test_gate_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["gate_id"] == test_gate_id
        assert "token_version" in data
        assert "qr_token" in data
        assert "nfc_token" in data
        assert "rotated_at" in data
        assert data["qr_expires_hours"] == 168  # 1 week
        assert data["nfc_expires_hours"] == 720  # 30 days
    
    @pytest.mark.asyncio
    async def test_field_access_by_token(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test field access using token."""
        # First generate a token
        qr_response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert qr_response.status_code == status.HTTP_200_OK
        qr_data = qr_response.json()
        token = qr_data["token"]
        
        # Now use the token to access gate info (no auth required)
        field_response = await client.get(f"/api/v1/labels/field/{token}")
        
        assert field_response.status_code == status.HTTP_200_OK
        field_data = field_response.json()
        
        assert field_data["gate_id"] == test_gate_id
        assert "gate_name" in field_data
        assert "gate_type" in field_data
        assert "status" in field_data
        assert "token_expires_at" in field_data
        assert "access_granted_at" in field_data
    
    @pytest.mark.asyncio
    async def test_legacy_gate_access_endpoint(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test legacy GET /gates/{token} endpoint."""
        # Generate token
        qr_response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        token = qr_response.json()["token"]
        
        # Test legacy endpoint
        legacy_response = await client.get(f"/api/v1/labels/gates/{token}")
        
        assert legacy_response.status_code == status.HTTP_200_OK
        data = legacy_response.json()
        assert data["gate_id"] == test_gate_id
    
    @pytest.mark.asyncio
    async def test_generate_label_image_endpoint(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test label generation endpoint."""
        request_data = {
            "gate_id": test_gate_id,
            "label_type": "standard",
            "width": 400,
            "height": 300,
            "include_printer_templates": True
        }
        
        response = await client.post(
            "/api/v1/labels/generate",
            json=request_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["gate_id"] == test_gate_id
        assert data["label_type"] == "standard"
        assert data["width"] == 400
        assert data["height"] == 300
        assert "download_url" in data
        assert "printer_templates" in data
    
    @pytest.mark.asyncio
    async def test_download_label_image(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_gate_id: int
    ):
        """Test label image download."""
        response = await client.get(
            f"/api/v1/labels/download/{test_gate_id}?label_type=standard&width=400&height=300",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 1000
    
    @pytest.mark.asyncio
    async def test_invalid_token_access(self, client: AsyncClient):
        """Test field access with invalid token."""
        response = await client.get("/api/v1/labels/field/invalid_token")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_expired_token_access(self, client: AsyncClient, admin_token: str, test_gate_id: int):
        """Test field access with expired token."""
        # Generate very short-lived token (1 second)
        qr_response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}?expires_hours=0.0003",  # Very short
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        token = qr_response.json()["token"]
        
        # Wait a bit and try to use expired token
        import time
        time.sleep(2)
        
        response = await client.get(f"/api/v1/labels/field/{token}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_unauthorized_label_access(self, client: AsyncClient, client_token: str, test_gate_id: int):
        """Test that non-admin users can't generate labels."""
        response = await client.get(
            f"/api/v1/labels/qr/{test_gate_id}.png",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN