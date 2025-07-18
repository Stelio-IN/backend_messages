from pydantic import BaseModel
import joblib
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import pandas as pd
import nltk

# Download NLTK resources
try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")

# Load ML models
try:
    text_fraud_model = joblib.load('text_fraud_model.pkl')
    url_fraud_model = joblib.load('url_fraud_model.pkl')
except FileNotFoundError:
    print("Error: Model files (text_fraud_model.pkl, url_fraud_model.pkl) not found.")
    exit(1)


# Pydantic model for fraud detection
class FraudDetectionRequest(BaseModel):
    content: str


# Preprocess text
def clean_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'http\S+', '', text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in filtered_words]
    return ' '.join(stemmed_words)


# Extract URL features
def extract_url_features(url):
    if not isinstance(url, str):
        url = ''
    return {
        'length': len(url),
        'num_subdomains': url.count('.') - 1 if url.startswith('http') else url.count('.'),
        'has_https': 1 if 'https' in url.lower() else 0,
        'has_suspicious_words': 1 if any(
            word in url.lower() for word in ['login', 'verify', 'account', 'secure']) else 0
    }


# Fraud detection function
async def detect_fraud(request: FraudDetectionRequest):
    content = request.content
    cleaned_text = clean_text(content)

    # Check for URLs in content
    urls = re.findall(r'http\S+', content)
    is_fraudulent = False
    fraud_probability = 0.0

    # Text classification
    text_prob = text_fraud_model.predict_proba([cleaned_text])[0][1]
    if text_prob > 0.7:
        is_fraudulent = True
        fraud_probability = max(fraud_probability, text_prob)

    # URL classification
    for url in urls:
        url_features = extract_url_features(url)
        url_features_df = pd.DataFrame([url_features])
        url_prob = url_fraud_model.predict_proba(url_features_df)[0][1]
        if url_prob > 0.7:
            is_fraudulent = True
            fraud_probability = max(fraud_probability, url_prob)

    return {
        "is_fraudulent": is_fraudulent,
        "fraud_probability": float(fraud_probability)
    }