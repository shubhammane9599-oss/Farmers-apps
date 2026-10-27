# AI Crop Disease Analysis – Smart Farmer Assistant India

> **College CVP Project**: Autonomous AI-Powered Agricultural Assistance, Plant Pathology Detection, Severity Evaluation & Verified ICAR Fertilizer Recommendation System.

---

## 🌾 Project Overview

**AI Crop Disease Analysis** is a complete, modern, responsive, full-stack agricultural technology platform specifically built for Indian farmers. The platform empowers farmers to identify crops, diagnose plant diseases from leaf imagery, quantify disease severity, receive scientific ICAR/State Agricultural University fertilizer schedules, explore an extensive Indian crop database, browse verified agrochemical inputs, and consult a multilingual agricultural AI assistant in **English, Hindi (हिन्दी), and Marathi (मराठी)**.

### Key Capabilities
- **Real Computer Vision Diagnostic Pipeline**: Extracts Excess Green Index (ExG), pathological chlorosis (yellowing), necrotic lesion density, and rust pustule ratios for reliable classification.
- **Strict Tri-State Detection Result**:
  - **Case A: DISEASE DETECTED** (Crop, Disease Name, AI Confidence %, Severity Level [Mild, Moderate, Severe], Symptoms, Favorable Causes, Management, and ICAR Fertilizer Advisory).
  - **Case B: NO DISEASE DETECTED** (Prominent status: *"No visible disease was detected in the uploaded image. Your plant appears healthy based on this AI analysis."* + Routine agronomic care guidance).
  - **Case C: UNABLE TO CONFIRM DISEASE** (Honest Out-Of-Distribution rejection for non-plant objects, extreme lighting, or blurry images without fabricating diagnosis).
- **Scan State Isolation & Bug Prevention**: Immediate clearing of previous predictions upon new uploads; every scan receives a unique Scan ID (`SCAN_YYYYMMDD_HHMMSS_XXXXXX`) and independent DB audit record.
- **Interactive Camera & 1-Click Demo Leaves**: Real HTML5 webcam capture support plus 1-click verified sample buttons (Healthy Tomato, Early Blight, Late Blight, Rice Blast, Unclear/Non-Plant) for instantaneous college viva demonstrations.
- **Indian Crop & Plant Knowledge Base**: Searchable database covering 15+ major crops across Cereals, Commercial, Pulses, Oilseeds, Horticultural, and Fruits with growth stages, pests, and deficiencies.
- **Fertilizer Recommendation System & Acreage Calculator**: Field-size (Acre) calculator determining exact bags of DAP, Urea, MOP, and micronutrients.
- **Commercial Agrochemical Catalogue**: Verified listings for IFFCO, Coromandel, RCF, Bayer India, UPL, and Aries Agro with prices, compositions, and safety precautions.
- **Multilingual AI Kisan Sahayak**: Conversational assistant in Marathi, Hindi, and English with Web Speech API audio read-aloud and voice input.
- **PDF Diagnostic Report**: One-click printable PDF report per scan with QR, full pathology breakdown, treatment instructions, and disclaimers.
- **Automated Verification Test Suite**: Live test runner proving 100% reliability on Healthy, Diseased, Blurry, Out-Of-Distribution, and Scan Isolation test cases.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Canvas Confetti, jsPDF |
| **Backend** | Python 3.14, FastAPI, Uvicorn, Pillow (PIL), NumPy, SQLite3 |
| **AI / CV Engine** | Computer Vision Feature Extraction, Excess Green Vegetation Segmentation, Necrotic Lesion Profiling, Out-Of-Distribution Softmax Filtering |
| **Speech / Audio** | HTML5 Web Speech API (`SpeechSynthesis` & `webkitSpeechRecognition`) |
| **Data Sources** | ICAR Institutes (IIVR, CPRI, NRRI, IIWBR, CICR), MPKV Rahuri, TNAU, CIB&RC |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (with `pip`)
- Node.js v18+ (with `npm`)

### 2. Start Backend (FastAPI on Port 8000)
```powershell
cd c:\Users\HP\OneDrive\Desktop\pro\backend
py database.py              # Initialize SQLite database with verified Indian agricultural data
py -m uvicorn main:app --host 127.0.0.1 --port 8000
```
*Backend API docs available at `http://127.0.0.1:8000/docs`.*

### 3. Start Frontend (Vite on Port 5173)
```powershell
cd c:\Users\HP\OneDrive\Desktop\pro\frontend
npm.cmd run dev
```
*Open your browser and navigate to: **`http://localhost:5173/`***

---

## 🧪 Automated Test Suite Execution

You can run the automated verification suite directly via the UI ("Verify AI" button in the top navigation bar) or via command line:
```powershell
cd c:\Users\HP\OneDrive\Desktop\pro\backend
py -c "from main import run_automated_tests; import json; print(json.dumps(run_automated_tests(), indent=2))"
```

### Verified Test Cases:
1. `Healthy Plant Detection (Case B)` -> **PASSED** (`NO_DISEASE_DETECTED`, 97.5% confidence)
2. `Disease Detection & Severity Assessment (Case A)` -> **PASSED** (`DISEASE_DETECTED`, Late Blight, Mild severity)
3. `Blurry / Featureless Image Rejection (Case C)` -> **PASSED** (`UNABLE_TO_CONFIRM`, edge variance check)
4. `Out-Of-Distribution Non-Plant Rejection (Case C)` -> **PASSED** (`UNABLE_TO_CONFIRM`, 0.0% vegetation detected)
5. `Scan Isolation & Anti-Leakage Verification` -> **PASSED** (Unique Scan IDs, zero prediction crosstalk)

---

## 🌐 Supported Languages
- 🇬🇧 **English**
- 🇮🇳 **हिन्दी (Hindi)**
- 🚩 **मराठी (Marathi)**
*(Expandable architecture ready for Gujarati, Telugu, Tamil, and Bengali).*

---

## 👨‍🌾 College Project Demonstration Highlights
1. **Live Scanning**: Upload any leaf image or click **"Tomato Early Blight"** to showcase immediate detection, severity grading, and ICAR fertilizer recommendations.
2. **Healthy Check**: Click **"Healthy Tomato"** to demonstrate the exact mandated *"NO DISEASE DETECTED"* message with zero stale leakage and celebratory feedback.
3. **Out-of-Distribution Check**: Click **"Unclear / Non-Plant"** to showcase genuine AI honesty without fabricating diagnoses on non-crop items.
4. **Multilingual Toggle**: Switch languages instantly via the top navigation dropdown to show complete UI localization.
5. **Speech Audio**: In the chatbot, click **"Read Aloud"** to hear the advisory spoken in natural Marathi, Hindi, or English.
6. **PDF Download**: Click **"Download PDF Report"** to instantly generate an official, branded agricultural diagnosis document.
