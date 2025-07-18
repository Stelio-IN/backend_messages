import pandas as pd
import numpy as np
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import joblib
import nltk

# Download required NLTK resources
try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")
    exit(1)

# Load datasets
try:
    sms_data = pd.read_csv('sms_spam.csv', encoding='latin-1')
    sms_data = sms_data.rename(columns={'v1': 'label', 'v2': 'text'})
except FileNotFoundError:
    print("Error: sms_spam.csv not found. Please provide the SMS Spam Collection Dataset.")
    exit(1)

try:
    url_data = pd.read_csv('phishing_urls.csv', encoding='latin-1')
except FileNotFoundError:
    print("Error: phishing_urls.csv not found. Please provide the UCI Phishing Sites Dataset.")
    exit(1)

# Debug: Print column names
print("Columns in phishing_urls.csv:", url_data.columns.tolist())

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

# Extract URL features (for backend compatibility)
def extract_url_features(url):
    if not isinstance(url, str):
        url = ''
    return {
        'length': len(url),
        'num_subdomains': url.count('.') - 1 if url.startswith('http') else url.count('.'),
        'has_https': 1 if 'https' in url.lower() else 0,
        'has_suspicious_words': 1 if any(word in url.lower() for word in ['login', 'verify', 'account', 'secure']) else 0
    }

# Prepare message data
sms_data['clean_text'] = sms_data['text'].apply(clean_text)
sms_data['label'] = sms_data['label'].map({'ham': 0, 'spam': 1})

# Prepare URL data (use existing features)
# Map dataset columns to expected features
url_data = url_data.rename(columns={
    'LongURL': 'length',
    'SubDomains': 'num_subdomains',
    'HTTPS': 'has_https'
})
# Add has_suspicious_words (simplified, as we don't have raw URLs)
url_data['has_suspicious_words'] = 0  # Assume 0 if no raw URLs available; adjust if URLs are present

# Train message classifier
X_text = sms_data['clean_text']
y_text = sms_data['label']
text_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000)),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
])
X_train_text, X_test_text, y_train_text, y_test_text = train_test_split(X_text, y_text, test_size=0.2, random_state=42)
text_pipeline.fit(X_train_text, y_train_text)

# Train URL classifier
X_url = url_data[['length', 'num_subdomains', 'has_https', 'has_suspicious_words']]
y_url = url_data['class']
url_pipeline = Pipeline([
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
])
X_train_url, X_test_url, y_train_url, y_test_url = train_test_split(X_url, y_url, test_size=0.2, random_state=42)
url_pipeline.fit(X_train_url, y_train_url)

# Save models
joblib.dump(text_pipeline, 'text_fraud_model.pkl')
joblib.dump(url_pipeline, 'url_fraud_model.pkl')

print("Models trained and saved successfully.")