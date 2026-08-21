import cv2
import numpy as np
import tensorflow as tf
import pytesseract
from PIL import Image
import io

model = tf.keras.applications.MobileNetV2(weights='imagenet', input_shape=(224,224,3))

def classify_image(image):
    if image is None:
        return None, None
    img = cv2.resize(image, (224, 224))
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    img = np.expand_dims(img, axis=0)
    preds = model.predict(img, verbose=0)
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0]
    return decoded[0][1], decoded[0][2]

def extract_text(image):
    if image is None:
        return ""
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    text = pytesseract.image_to_string(pil_img)
    return text.strip()

def contains_keywords(text, keywords):
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False

def analyze_data(data, config):
    results = {}
    interesting = False
    reason = ""
    keywords = config.get('keywords', [])

    if data.get('image') is not None:
        label, conf = classify_image(data['image'])
        if label and conf > config.get('ai_confidence_threshold', 0.6):
            results['label'] = label
            results['conf'] = f"{conf:.2f}"
        text = extract_text(data['image'])
        if text:
            results['ocr'] = text[:300]
            if contains_keywords(text, keywords):
                interesting = True
                reason = "keyword in image"

    if data.get('location'):
        results['location'] = data['location'][:200]

    if data.get('screenshot'):
        try:
            pil = Image.open(io.BytesIO(data['screenshot']))
            img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            text = extract_text(img)
            if text and contains_keywords(text, keywords):
                interesting = True
                reason = "keyword in screenshot"
                results['screenshot_ocr'] = text[:300]
        except:
            pass

    return results, interesting, reason