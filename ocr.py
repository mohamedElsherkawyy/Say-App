# import cv2
# import pytesseract as pyt
# from pytesseract import Output
# import pandas as pd
# import numpy as np
# import os

# pyt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# def preprocess_image_from_bytes(image_bytes):
#     np_arr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.resize(gray, None, fx=2, fy=2)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return thresh

# def extract_table_data(img):
#     custom_oem_psm_config = r'--oem 3 --psm 6 -l ara+eng'
#     details = pyt.image_to_data(img, output_type=Output.DICT, config=custom_oem_psm_config)
#     rows = []
#     current_row = []
#     last_top = None
#     for i in range(len(details['text'])):
#         word = details['text'][i].strip()
#         conf = int(details['conf'][i])
#         top = details['top'][i]
#         if conf > 50 and word != '':
#             if last_top is None:
#                 last_top = top
#             if abs(top - last_top) > 15:
#                 if current_row:
#                     rows.append(current_row)
#                 current_row = [word]
#                 last_top = top
#             else:
#                 current_row.append(word)
#     if current_row:
#         rows.append(current_row)
#     return rows

# def rows_to_string(rows):
#     return '\n'.join([' '.join(row) for row in rows])

# def process_image_from_bytes(image_bytes):
#     img = preprocess_image_from_bytes(image_bytes)
#     rows = extract_table_data(img)
#     result_str = rows_to_string(rows)
#     print(result_str)
#     return result_str
import base64
from io import BytesIO

from PIL import Image


def _compress_image(image_bytes: bytes, max_size: int = 800, quality: int = 70) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def encode_image(image_path):
    """Encode image from file path to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_image(image_bytes, compress: bool = True):
    if compress:
        image_bytes = _compress_image(image_bytes)
    return base64.b64encode(image_bytes).decode("utf-8")