import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

FIELD_KEYWORD_PATTERNS: List[Tuple[str, "re.Pattern"]] = [
    ("nitrogen", re.compile(r"nitrogen|available\s*n\b", re.IGNORECASE)),
    ("phosphorus", re.compile(r"phosphorus|available\s*p\b", re.IGNORECASE)),
    ("potassium", re.compile(r"potassium|available\s*k\b", re.IGNORECASE)),
    ("organic_carbon", re.compile(r"organic\s*carbon|\boc\b", re.IGNORECASE)),
    ("ph", re.compile(r"\bph\b|p\s*h\s*value", re.IGNORECASE)),
]

NUMBER_PATTERN = re.compile(r"(\d+\.\d+|\d+)")
CONFIDENCE_THRESHOLD = 70.0


def deskew(gray_image: np.ndarray) -> np.ndarray:
    thresh = cv2.threshold(
        gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )[1]
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 10:
        return gray_image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.1:
        return gray_image

    (h, w) = gray_image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray_image,
        rotation_matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image. Please upload a valid jpg/png file.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)

    deskewed = deskew(contrast_enhanced)
    return deskewed


@lru_cache(maxsize=1)
def get_ocr_reader():
    import easyocr
    import torch

    gpu_available = torch.cuda.is_available()
    return easyocr.Reader(["en"], gpu=gpu_available, verbose=False)


def run_ocr(preprocessed_image: np.ndarray) -> List[Tuple[list, str, float]]:
    reader = get_ocr_reader()
    return reader.readtext(preprocessed_image)


def extract_soil_values(
    ocr_results: List[Tuple[list, str, float]]
) -> Dict[str, dict]:
    lines = [(text.strip(), float(conf)) for (_, text, conf) in ocr_results if text.strip()]

    extracted: Dict[str, dict] = {}
    used_fields = set()

    for idx, (text, conf) in enumerate(lines):
        for field, pattern in FIELD_KEYWORD_PATTERNS:
            if field in used_fields:
                continue
            if not pattern.search(text):
                continue

            match = NUMBER_PATTERN.search(text)
            value_text: Optional[str] = None
            value_conf = conf

            if match:
                value_text = match.group(1)
            else:
                for j in range(idx + 1, min(idx + 3, len(lines))):
                    next_text, next_conf = lines[j]
                    next_match = NUMBER_PATTERN.fullmatch(next_text.strip())
                    if next_match:
                        value_text = next_match.group(1)
                        value_conf = (conf + next_conf) / 2
                        break

            if value_text is not None:
                confidence_pct = round(value_conf * 100, 2)
                extracted[field] = {
                    "value": float(value_text),
                    "confidence": confidence_pct,
                    "raw_text": text,
                    "needs_manual_correction": confidence_pct < CONFIDENCE_THRESHOLD,
                }
                used_fields.add(field)
            break

    for field, _ in FIELD_KEYWORD_PATTERNS:
        if field not in extracted:
            extracted[field] = {
                "value": None,
                "confidence": 0.0,
                "raw_text": None,
                "needs_manual_correction": True,
            }

    return extracted
