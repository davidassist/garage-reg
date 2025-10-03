"""S3 service for photo documentation in field forms."""

import boto3
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException
import os

from app.core.config import get_settings
from app.models.inspections import InspectionPhoto
from app.schemas.field_forms import PhotoUploadRequest, PhotoUploadResponse


class S3PhotoService:
    """Service for managing inspection photos in S3 storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self._setup_s3_client()
    
    def _setup_s3_client(self):
        """Setup S3 client with configuration."""
        try:
            # Use environment variables or AWS credentials file
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.settings.AWS_REGION or 'us-east-1'
            )
            
            # Default bucket configuration
            self.bucket_name = self.settings.S3_PHOTOS_BUCKET or 'garagereg-inspection-photos'
            
            # Test connection
            self._test_s3_connection()
            
        except NoCredentialsError:
            # Fallback to local file storage for development
            self.s3_client = None
            self.bucket_name = None
            print("⚠️  AWS credentials not found, using local file storage for photos")
    
    def _test_s3_connection(self):
        """Test S3 connection and create bucket if needed."""
        if not self.s3_client:
            return
        
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket doesn't exist, create it (for development)
                if self.settings.ENVIRONMENT == 'development':
                    try:
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                        print(f"✅ Created S3 bucket: {self.bucket_name}")
                    except ClientError as create_error:
                        print(f"❌ Failed to create S3 bucket: {create_error}")
            else:
                print(f"❌ S3 connection error: {e}")
    
    def generate_upload_url(
        self, 
        photo_request: PhotoUploadRequest,
        expires_in: int = 3600
    ) -> PhotoUploadResponse:
        """
        Generate pre-signed upload URL for photo.
        
        Args:
            photo_request: Photo upload request data
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Upload response with pre-signed URL
            
        Raises:
            HTTPException: If S3 operation fails
        """
        if not self.s3_client:
            # Fallback to local storage
            return self._generate_local_upload_response(photo_request)
        
        try:
            # Generate unique S3 key
            s3_key = self._generate_s3_key(photo_request)
            
            # Generate pre-signed URL for PUT operation
            upload_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key,
                    'ContentType': photo_request.metadata.mime_type or 'image/jpeg'
                },
                ExpiresIn=expires_in
            )
            
            return PhotoUploadResponse(
                photo_id=0,  # Will be set by caller after DB creation
                upload_url=upload_url,
                s3_key=s3_key,
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"S3 upload URL generation failed: {e}"
            )
    
    def generate_download_url(
        self, 
        s3_key: str, 
        expires_in: int = 3600
    ) -> str:
        """
        Generate pre-signed download URL for photo.
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Pre-signed download URL
        """
        if not self.s3_client:
            # Return local file URL
            return f"/api/v1/photos/local/{s3_key}"
        
        try:
            download_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return download_url
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"S3 download URL generation failed: {e}"
            )
    
    def validate_upload_completion(self, s3_key: str) -> Dict[str, Any]:
        """
        Validate that photo upload was completed successfully.
        
        Args:
            s3_key: S3 object key to validate
            
        Returns:
            Upload validation result with metadata
        """
        if not self.s3_client:
            # Mock validation for local storage
            return {
                "exists": True,
                "size": 1024000,  # Mock size
                "content_type": "image/jpeg",
                "last_modified": datetime.utcnow()
            }
        
        try:
            # Check object exists and get metadata
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                "exists": True,
                "size": response['ContentLength'],
                "content_type": response.get('ContentType'),
                "last_modified": response['LastModified'],
                "etag": response['ETag'].strip('\"')
            }
            
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return {"exists": False}
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"S3 validation failed: {e}"
                )
    
    def delete_photo(self, s3_key: str) -> bool:
        """
        Delete photo from S3 storage.
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if deleted successfully
        """
        if not self.s3_client:
            # Mock deletion for local storage
            return True
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            print(f"⚠️  Failed to delete S3 object {s3_key}: {e}")
            return False
    
    def _generate_s3_key(self, photo_request: PhotoUploadRequest) -> str:
        """
        Generate unique S3 key for photo.
        
        Format: inspections/{inspection_id}/photos/{timestamp}_{uuid}_{filename}
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Clean filename
        original_filename = photo_request.metadata.original_filename or "photo.jpg"
        safe_filename = "".join(c for c in original_filename if c.isalnum() or c in '.-_').rstrip()
        
        s3_key = (
            f"inspections/{photo_request.inspection_id}/"
            f"photos/{timestamp}_{unique_id}_{safe_filename}"
        )
        
        return s3_key
    
    def _generate_local_upload_response(
        self, 
        photo_request: PhotoUploadRequest
    ) -> PhotoUploadResponse:
        """Generate mock upload response for local development."""
        local_key = self._generate_s3_key(photo_request)
        
        # Create local upload endpoint
        upload_url = f"/api/v1/photos/upload/local/{local_key}"
        
        return PhotoUploadResponse(
            photo_id=0,
            upload_url=upload_url,
            s3_key=local_key,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
    
    def get_photo_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """Get photo metadata from S3."""
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                "size": response['ContentLength'],
                "content_type": response.get('ContentType'),
                "last_modified": response['LastModified'],
                "metadata": response.get('Metadata', {})
            }
            
        except ClientError:
            return None


class PhotoValidationService:
    """Service for validating photo requirements and enforcing mandatory photos."""
    
    @staticmethod
    def validate_photo_requirements(
        inspection_id: int,
        uploaded_photos: list,
        required_photos: list
    ) -> Dict[str, Any]:
        """
        Validate if all required photos are uploaded.
        
        Args:
            inspection_id: Inspection ID
            uploaded_photos: List of uploaded photos
            required_photos: List of required photo definitions
            
        Returns:
            Validation result with missing photos and status
        """
        uploaded_categories = {
            photo.category: photo 
            for photo in uploaded_photos 
            if photo.upload_status == 'completed'
        }
        
        missing_photos = []
        for req_photo in required_photos:
            category = req_photo.get('category', 'mandatory')
            if category not in uploaded_categories:
                missing_photos.append(req_photo)
        
        return {
            "is_valid": len(missing_photos) == 0,
            "missing_photos": missing_photos,
            "uploaded_count": len(uploaded_categories),
            "required_count": len(required_photos)
        }
    
    @staticmethod
    def enforce_mandatory_photos(
        inspection_item,
        checklist_item
    ) -> List[str]:
        """
        Enforce mandatory photo requirements based on checklist item.
        
        Args:
            inspection_item: Current inspection item
            checklist_item: Template checklist item
            
        Returns:
            List of required photo categories
        """
        required_categories = []
        
        # Always require photo if checklist item specifies it
        if checklist_item.requires_photo:
            required_categories.append('mandatory')
        
        # Require evidence photos for failed items
        if inspection_item.result == 'fail':
            required_categories.extend(['evidence', 'damage'])
        
        # Require before/after photos for repairs
        if (checklist_item.category == 'repair' or 
            'repair' in (checklist_item.instructions or '').lower()):
            required_categories.extend(['before', 'after'])
        
        # Safety-critical items always need photo documentation
        if checklist_item.safety_critical:
            required_categories.append('safety_evidence')
        
        return list(set(required_categories))  # Remove duplicates
    
    @staticmethod
    def validate_measurement_photo(
        measurement_value: float,
        tolerance: float,
        require_photo_threshold: float = 0.1
    ) -> bool:
        """
        Determine if measurement requires photo documentation.
        
        Args:
            measurement_value: Measured value
            tolerance: Acceptable tolerance
            require_photo_threshold: Threshold for requiring photo (default 10%)
            
        Returns:
            True if photo is required for this measurement
        """
        if tolerance == 0:
            return False
        
        deviation_ratio = abs(measurement_value - tolerance) / tolerance
        return deviation_ratio > require_photo_threshold