import os
from typing import List, Optional
from PIL import Image
import mimetypes
from utils.exceptions import ValidationError
from core.config import settings


def validate_image_file(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValidationError(f"Path is not a file: {file_path}")
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > settings.max_image_size_mb:
        raise ValidationError(
            f"File size {file_size_mb:.2f}MB exceeds maximum allowed size "
            f"{settings.max_image_size_mb}MB"
        )
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValidationError(f"File is not a valid image: {file_path}")
    
    file_ext = file_path.lower().split(".")[-1]
    if file_ext not in settings.supported_formats_list:
        raise ValidationError(
            f"Unsupported image format: {file_ext}. "
            f"Supported formats: {', '.join(settings.supported_formats_list)}"
        )
    
    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception as e:
        raise ValidationError(f"Invalid or corrupted image file: {e}")


def validate_batch_images(file_paths: List[str]) -> List[str]:
    validated_paths = []
    errors = []
    
    for file_path in file_paths:
        try:
            validate_image_file(file_path)
            validated_paths.append(file_path)
        except ValidationError as e:
            errors.append(f"{file_path}: {str(e)}")
    
    if errors:
        raise ValidationError(f"Validation errors: {'; '.join(errors)}")
    
    return validated_paths