import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_image_quality_score(image_path: str) -> float:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0.0
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        brightness = np.mean(gray)
        
        contrast = gray.std()
        
        noise_score = calculate_noise_score(gray)
        
        quality_score = (
            min(laplacian_var / 1000.0, 1.0) * 0.4 +
            (1.0 - abs(brightness - 128) / 128.0) * 0.2 +
            min(contrast / 64.0, 1.0) * 0.2 +
            (1.0 - noise_score) * 0.2
        )
        
        return max(0.0, min(1.0, quality_score))
        
    except Exception as e:
        logger.error(f"Error calculating quality score for {image_path}: {e}")
        return 0.0


def calculate_noise_score(gray_image: np.ndarray) -> float:
    try:
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        noise = cv2.absdiff(gray_image, blurred)
        noise_score = np.mean(noise) / 255.0
        return min(noise_score, 1.0)
    except Exception:
        return 0.5


def get_image_metadata(image_path: str) -> Dict[str, Any]:
    try:
        with Image.open(image_path) as img:
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
            }
            
            if hasattr(img, "_getexif") and img._getexif():
                metadata["exif"] = dict(img._getexif())
            
            return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {image_path}: {e}")
        return {}


def resize_image_if_needed(image_path: str, max_size: Tuple[int, int] = (1024, 1024)) -> str:
    try:
        with Image.open(image_path) as img:
            if img.size[0] <= max_size[0] and img.size[1] <= max_size[1]:
                return image_path
            
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            output_path = image_path.replace(".", "_resized.")
            img.save(output_path)
            
            return output_path
    except Exception as e:
        logger.error(f"Error resizing image {image_path}: {e}")
        return image_path