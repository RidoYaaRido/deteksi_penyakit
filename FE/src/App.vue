<template>
  <div class="app-container">
    <div class="main-wrapper">
      <!-- Header -->
      <header class="app-header">
        <div class="header-content">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div>
            <h1>Sistem Prediksi Penyakit</h1>
            <p>Menggunakan Decision Tree Machine Learning</p>
          </div>
        </div>
      </header>

      <div class="content-grid">
        <!-- Input Section -->
        <div class="card input-section">
          <div class="card-header">
            <h2>Pilih Gejala</h2>
            <span class="badge">{{ selectedCount }} dipilih</span>
          </div>

          <div class="symptoms-list">
            <label 
              v-for="symptom in symptoms" 
              :key="symptom.id"
              class="symptom-item"
              :class="{ 'selected': symptomData[symptom.id] }"
            >
              <input 
                type="checkbox"
                v-model="symptomData[symptom.id]"
                @change="onSymptomChange"
              />
              <span>{{ symptom.label }}</span>
            </label>
          </div>

          <div class="button-group">
            <button 
              @click="predictDisease"
              :disabled="selectedCount === 0 || loading"
              class="btn btn-primary"
            >
              <span v-if="loading" class="spinner"></span>
              {{ loading ? 'Menganalisis...' : 'Prediksi Penyakit' }}
            </button>
            <button 
              @click="resetForm"
              class="btn btn-secondary"
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Result Section -->
        <div class="card result-section">
          <div class="card-header">
            <h2>Hasil Prediksi</h2>
          </div>

          <div v-if="!prediction" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p>Pilih gejala dan klik tombol prediksi untuk melihat hasil</p>
          </div>

          <div v-else class="result-content">
            <div class="disease-card">
              <div class="disease-header">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <div>
                  <h3>{{ prediction.disease }}</h3>
                  <p>{{ prediction.description }}</p>
                </div>
              </div>
            </div>

            <div class="stats">
              <div class="stat-item">
                <label>Tingkat Keyakinan</label>
                <span class="confidence-badge" :class="confidenceClass">
                  {{ prediction.confidence }}
                </span>
              </div>

              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: (prediction.probability * 100) + '%' }"
                ></div>
              </div>

              <div class="probability-box">
                <p>Probabilitas</p>
                <h2>{{ (prediction.probability * 100).toFixed(1) }}%</h2>
              </div>

              <div class="recommendation-box">
                <strong>Rekomendasi:</strong>
                <p>{{ prediction.recommendation }}</p>
              </div>
            </div>

            <div class="warning-box">
              <strong>Catatan:</strong>
              Hasil ini adalah prediksi sistem dan bukan diagnosis medis. 
              Konsultasikan dengan dokter untuk pemeriksaan lebih lanjut.
            </div>
          </div>
        </div>
      </div>

      <!-- Info Footer -->
      <div class="card info-footer">
        <h3>Tentang Sistem</h3>
        <p>
          Sistem ini menggunakan algoritma Decision Tree untuk memprediksi penyakit 
          berdasarkan gejala yang Anda alami. Backend dibangun dengan Python 
          (scikit-learn) dan frontend menggunakan Vue.js. Model dilatih menggunakan 
          data medis untuk memberikan prediksi yang akurat.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DiseasePredictorApp',
  data() {
    return {
      symptoms: [
        { id: 'demam', label: 'Demam' },
        { id: 'batuk', label: 'Batuk' },
        { id: 'sakit_kepala', label: 'Sakit Kepala' },
        { id: 'pilek', label: 'Pilek' },
        { id: 'sakit_tenggorokan', label: 'Sakit Tenggorokan' },
        { id: 'mual', label: 'Mual' },
        { id: 'nyeri_otot', label: 'Nyeri Otot' },
        { id: 'sesak_napas', label: 'Sesak Napas' },
        { id: 'diare', label: 'Diare' },
        { id: 'ruam_kulit', label: 'Ruam Kulit' }
      ],
      symptomData: {
        demam: false,
        batuk: false,
        sakit_kepala: false,
        pilek: false,
        sakit_tenggorokan: false,
        mual: false,
        nyeri_otot: false,
        sesak_napas: false,
        diare: false,
        ruam_kulit: false
      },
      prediction: null,
      loading: false,
      apiUrl: 'https://deteksi-penyakit-chi.vercel.app/api'
    };
  },
  computed: {
    selectedCount() {
      return Object.values(this.symptomData).filter(Boolean).length;
    },
    confidenceClass() {
      if (!this.prediction) return '';
      const confidence = this.prediction.confidence;
      if (confidence === 'Tinggi') return 'high';
      if (confidence === 'Sedang') return 'medium';
      return 'low';
    }
  },
  methods: {
    async predictDisease() {
      this.loading = true;
      
      try {
        const response = await axios.post(`${this.apiUrl}/predict`, {
          symptoms: this.symptomData
        });
        
        if (response.data.success) {
          this.prediction = response.data.prediction;
        }
      } catch (error) {
        console.error('Error predicting disease:', error);
        alert('Terjadi kesalahan saat memprediksi penyakit. Pastikan backend server berjalan.');
      } finally {
        this.loading = false;
      }
    },
    onSymptomChange() {
      this.prediction = null;
    },
    resetForm() {
      Object.keys(this.symptomData).forEach(key => {
        this.symptomData[key] = false;
      });
      this.prediction = null;
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}


.app-container {
  min-height: 100vh;
  
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
  overflow: hidden;
}

.app-container::before {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
  top: -250px;
  right: -250px;
  animation: float 20s ease-in-out infinite;
}

.app-container::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
  bottom: -200px;
  left: -200px;
  animation: float 15s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(50px, 50px) rotate(180deg); }
}

.main-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.app-header {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  color: #667eea;
}

.app-header h1 {
  font-size: 2rem;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.app-header p {
  color: #718096;
  font-size: 0.9rem;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h2 {
  font-size: 1.25rem;
  color: #1a202c;
}

.badge {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.symptoms-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.symptom-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.symptom-item:hover {
  background: #f7fafc;
  border-color: #667eea;
}

.symptom-item.selected {
  background: #edf2f7;
  border-color: #667eea;
}

.symptom-item input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.75rem;
  cursor: pointer;
}

.symptom-item span {
  color: #2d3748;
  font-weight: 500;
}

.button-group {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  flex: 1;
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-primary:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.875rem 1.5rem;
  background: white;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f7fafc;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #a0aec0;
  text-align: center;
  padding: 2rem;
}

.empty-state svg {
  margin-bottom: 1rem;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.disease-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 0.75rem;
}

.disease-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.disease-header h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.disease-header p {
  font-size: 0.9rem;
  opacity: 0.9;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item label {
  color: #4a5568;
  font-weight: 500;
}

.confidence-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.confidence-badge.high {
  background: #c6f6d5;
  color: #22543d;
}

.confidence-badge.medium {
  background: #feebc8;
  color: #7c2d12;
}

.confidence-badge.low {
  background: #fed7d7;
  color: #742a2a;
}

.progress-bar {
  width: 100%;
  height: 0.75rem;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 1s ease;
  border-radius: 9999px;
}

.probability-box {
  background: #ebf4ff;
  border-left: 4px solid #4299e1;
  padding: 1rem;
  border-radius: 0.5rem;
}

.probability-box p {
  color: #2c5282;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.probability-box h2 {
  color: #2b6cb0;
  font-size: 2rem;
}

.recommendation-box {
  background: #f0fff4;
  border: 1px solid #9ae6b4;
  padding: 1rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
}

.recommendation-box strong {
  color: #22543d;
  display: block;
  margin-bottom: 0.5rem;
}

.recommendation-box p {
  color: #2f855a;
  line-height: 1.5;
}

.warning-box {
  background: #fffaf0;
  border: 1px solid #fbd38d;
  padding: 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #7c2d12;
}

.warning-box strong {
  display: block;
  margin-bottom: 0.25rem;
}

.info-footer {
  margin-top: 2rem;
}

.info-footer h3 {
  color: #1a202c;
  margin-bottom: 0.75rem;
}

.info-footer p {
  color: #4a5568;
  line-height: 1.6;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .app-header h1 {
    font-size: 1.5rem;
  }
}
</style>
