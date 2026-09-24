import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).resolve().parent / "fonts" / "AmazonEmberDisplay_LtIt.ttf"

def create_certificate(name, template_path="certificate.png", output_path="output.png"):
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found. Please ensure you have the template image.")
        return False
        
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Bounding box coordinates
    left = 2150
    top = 1401
    width = 915
    height = 263
    
    # Try to load a font, fallback to default if not found
    try:
        # Increase font size to fit the bounding box appropriately
        font = ImageFont.truetype(str(FONT_PATH), 120)
    except IOError:
        print("Warning: project font not found. Using the Pillow default font.")
        font = ImageFont.load_default()
        
    # Get text bounding box to center it
    try:
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(name, font=font)
    
    # Calculate position to center the text in the bounding box
    x = left + (width - text_width) / 2
    y = top + (height - text_height) / 2
    
    # You can change the fill color if necessary
    draw.text((x, y), name, fill="black", font=font)
    
    img.save(output_path)
    return True
