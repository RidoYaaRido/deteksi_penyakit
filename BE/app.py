from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

# Dataset gejala dan penyakit
def create_training_data():
    """
    Membuat dataset training untuk Decision Tree
    Format: setiap baris adalah kombinasi gejala dan label penyakit
    """
    data = {
        'demam': [1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0],
        'batuk': [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        'sakit_kepala': [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        'pilek': [1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0],
        'sakit_tenggorokan': [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1],
        'mual': [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        'nyeri_otot': [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
        'sesak_napas': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        'diare': [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        'ruam_kulit': [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
        'penyakit': [
            'Influenza', 'Common Cold', 'Demam Berdarah', 'Influenza', 
            'Common Cold', 'Common Cold', 'Demam Berdarah', 'Pneumonia',
            'Common Cold', 'Gastroenteritis', 'Pneumonia', 'Demam Berdarah',
            'Common Cold', 'Gastroenteritis', 'Pneumonia', 'Demam Berdarah',
            'Common Cold', 'Pneumonia', 'Gastroenteritis', 'Common Cold'
        ]
    }
    return pd.DataFrame(data)

# Train the model
def train_model():
    """
    Melatih model Decision Tree dengan dataset
    """
    df = create_training_data()
    
    # Pisahkan fitur dan target
    X = df.drop('penyakit', axis=1)
    y = df['penyakit']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train Decision Tree
    model = DecisionTreeClassifier(
        criterion='gini',
        max_depth=5,
        min_samples_split=2,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluasi model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Simpan model
    with open('disease_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    return model, accuracy

# Load atau train model saat startup
if os.path.exists('disease_model.pkl'):
    with open('disease_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded from file")
else:
    model, accuracy = train_model()
    print("New model trained")

# Deskripsi penyakit
disease_info = {
    'Influenza': {
        'description': 'Infeksi virus pada sistem pernapasan yang menyebabkan demam, batuk, dan gejala flu',
        'recommendation': 'Istirahat cukup, minum banyak air, dan konsumsi obat penurun demam'
    },
    'Common Cold': {
        'description': 'Infeksi virus ringan pada saluran pernapasan atas',
        'recommendation': 'Istirahat, minum air hangat, dan konsumsi vitamin C'
    },
    'Demam Berdarah': {
        'description': 'Penyakit infeksi yang disebabkan oleh virus dengue, ditularkan melalui gigitan nyamuk',
        'recommendation': 'SEGERA konsultasi ke dokter, perbanyak cairan, dan istirahat total'
    },
    'Pneumonia': {
        'description': 'Infeksi yang menyebabkan peradangan pada kantung udara di paru-paru',
        'recommendation': 'Segera konsultasi ke dokter untuk mendapat antibiotik dan perawatan'
    },
    'Gastroenteritis': {
        'description': 'Infeksi atau peradangan pada saluran pencernaan',
        'recommendation': 'Minum oralit, hindari makanan berat, dan istirahat'
    }
}

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Endpoint untuk prediksi penyakit berdasarkan gejala
    """
    try:
        data = request.json
        symptoms = data.get('symptoms', {})
        
        # Validasi input
        required_symptoms = [
            'demam', 'batuk', 'sakit_kepala', 'pilek', 'sakit_tenggorokan',
            'mual', 'nyeri_otot', 'sesak_napas', 'diare', 'ruam_kulit'
        ]
        
        # Konversi ke format yang dibutuhkan model
        input_data = []
        for symptom in required_symptoms:
            input_data.append(1 if symptoms.get(symptom, False) else 0)
        
        # Prediksi
        input_array = np.array([input_data])
        prediction = model.predict(input_array)[0]
        
        # Get probability
        probabilities = model.predict_proba(input_array)[0]
        max_prob = max(probabilities)
        
        # Tentukan confidence level
        if max_prob >= 0.8:
            confidence = 'Tinggi'
        elif max_prob >= 0.6:
            confidence = 'Sedang'
        else:
            confidence = 'Rendah'
        
        # Buat response
        response = {
            'success': True,
            'prediction': {
                'disease': prediction,
                'probability': float(max_prob),
                'confidence': confidence,
                'description': disease_info.get(prediction, {}).get('description', ''),
                'recommendation': disease_info.get(prediction, {}).get('recommendation', '')
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """
    Endpoint untuk mendapatkan daftar gejala yang tersedia
    """
    symptoms_list = [
        {'id': 'demam', 'label': 'Demam'},
        {'id': 'batuk', 'label': 'Batuk'},
        {'id': 'sakit_kepala', 'label': 'Sakit Kepala'},
        {'id': 'pilek', 'label': 'Pilek'},
        {'id': 'sakit_tenggorokan', 'label': 'Sakit Tenggorokan'},
        {'id': 'mual', 'label': 'Mual'},
        {'id': 'nyeri_otot', 'label': 'Nyeri Otot'},
        {'id': 'sesak_napas', 'label': 'Sesak Napas'},
        {'id': 'diare', 'label': 'Diare'},
        {'id': 'ruam_kulit', 'label': 'Ruam Kulit'}
    ]
    return jsonify({
        'success': True,
        'symptoms': symptoms_list
    })

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """
    Endpoint untuk mendapatkan informasi penyakit
    """
    return jsonify({
        'success': True,
        'diseases': disease_info
    })

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """
    Endpoint untuk melatih ulang model (opsional)
    """
    try:
        global model
        model, accuracy = train_model()
        return jsonify({
            'success': True,
            'message': 'Model retrained successfully',
            'accuracy': accuracy
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)