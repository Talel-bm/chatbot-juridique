from flask import Flask, request, jsonify
import json
import os
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import unicodedata
import re
from nltk.corpus import stopwords

# Download French stopwords if not already downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load summaries from JSON file
with open(r"C:\Users\talelbm\Travaux Tarification STAR\Tarification et assainissement du portefeuille Automobile STAR\Code Tarification\summary_data.json", 'r', encoding='utf-8') as file:
    summaries = json.load(file)

class FrenchQuestionTextMatcher:
    def __init__(self, threshold=0.1):
        self.vectorizer = TfidfVectorizer(
            stop_words=list(stopwords.words('french')),
            max_features=5000,
            ngram_range=(1, 2),
            analyzer='word',
            token_pattern=r'\b\w+\b'
        )
        self.threshold = threshold
        self.summaries = None
        self.file_names = None
        self.vectors = None
        
    def preprocess_french_text(self, text):
        text = text.lower()
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'[^a-záàâäéèêëíìîïóòôöúùûüýÿæœç\s]', ' ', text)
        text = ' '.join(text.split())
        return text
        
    def fit(self, text_dict):
        self.file_names = list(text_dict.keys())
        self.summaries = [self.preprocess_french_text(text) for text in text_dict.values()]
        self.vectors = self.vectorizer.fit_transform(self.summaries)
        
    def find_relevant_texts(self, question, top_k=3):
        processed_question = self.preprocess_french_text(question)
        question_vector = self.vectorizer.transform([processed_question])
        similarities = cosine_similarity(question_vector, self.vectors).flatten()
        relevant_indices = np.where(similarities >= self.threshold)[0]
        relevant_indices = relevant_indices[np.argsort(-similarities[relevant_indices])]
        relevant_indices = relevant_indices[:top_k]
        return [self.file_names[i] for i in relevant_indices]

def merge_documents(folder_path, relevant_docs):
    merged_text = ""
    
    for doc_name in relevant_docs:
        doc_path = os.path.join(folder_path, doc_name)
        with open(doc_path, 'r', encoding='utf-8') as file:
            merged_text += file.read() + "\n==================================================\n"
    
    return merged_text.strip()

def make_gemini_request(document, contexte, question, api_key):
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    chat_session = model.start_chat(history=[])
    
    prompt = f"contexte : {contexte}\n document : {document}\n reponder à cette question : {question}"
    
    response = chat_session.send_message(prompt)
    
    return response.text

def query_gemini(question):
    folder_path = 'YOUR FOLDER OF LEGAL DOCS'
    api_key = "YOUR_GOOGLE_API_KEY" 
    matcher = FrenchQuestionTextMatcher(threshold=0.1)
    matcher.fit(summaries)
    try:
        relevant_docs = matcher.find_relevant_texts(question, top_k=2)
    except TypeError:
        return "Votre question n'est pas reliée à l'assurance en Tunisie"
    merged_document = merge_documents(folder_path, relevant_docs)
    
    contexte = """vous etes un expert juridique dans l'assurance en tunisie. Vous etes donnez des documents juridique et vous etes
    censés repondre à la question avec precision et en se referant aux documents. etre exhaustif et  citer vos sources à la fin. si la question
    n'est pas relié au domaine de l'assurance en Tunisie, informer l'utilisateur que vous ne pouvez pas répondre à sa question"""
    
    result = make_gemini_request(merged_document, contexte, question, api_key)
    
    return result

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        response = query_gemini(question)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)