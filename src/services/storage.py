import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from ..config.settings import get_settings

settings = get_settings()

class StorageService:
    def __init__(self):
        self.media_path = settings.MEDIA_PATH
        os.makedirs(self.media_path, exist_ok=True)

    async def save_image(self, file: UploadFile) -> str:
        """Save an uploaded image and return its URL."""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.media_path, file_name)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Return URL
            return f"{settings.MEDIA_URL}{file_name}"
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file: {str(e)}"
            )

    def delete_image(self, file_path: str) -> None:
        """Delete an image file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file: {str(e)}"
            )

    async def validate_image(self, file: UploadFile) -> None:
        """Validate uploaded image file."""
        # Check file size
        if file.size > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 5MB limit"
            )
        
        # Check file type
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPEG, PNG, and WebP are allowed"
            )

storage_service = StorageService()
