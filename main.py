"""
FastAPI Backend for AI Crop Disease Analysis - Smart Farmer Assistant India.
Provides endpoints for AI image inference, scan history, agricultural knowledge base,
commercial input catalogue, multilingual AI chatbot, and administrative management.
"""

import os
import json
import shutil
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

from database import init_db, get_db_connection, UPLOAD_DIR
from ai_engine import run_ai_inference, SUPPORTED_CLASSES
from chatbot import generate_agricultural_response, SUGGESTED_QUESTIONS

# Initialize FastAPI application
app = FastAPI(
    title="AI Crop Disease Analysis API",
    description="Smart AI-Powered Plant Health Assistant for Indian Farmers",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists and mount static files
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def startup_event():
    init_db()

# --- Health & Stats ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Crop Disease Analysis API",
        "version": "1.0.0",
        "framework": "FastAPI with Computer Vision & ONNX Runtime",
        "supported_crops_count": len(SUPPORTED_CLASSES),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM crops")
    crops_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM diseases")
    diseases_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM products")
    products_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM scans")
    total_scans = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM scans WHERE detection_status = 'NO_DISEASE_DETECTED'")
    healthy_scans = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM scans WHERE detection_status = 'DISEASE_DETECTED'")
    diseased_scans = cursor.fetchone()["count"]

    conn.close()
    return {
        "supported_crops": crops_count,
        "disease_profiles": diseases_count,
        "verified_products": products_count,
        "total_scans": total_scans,
        "healthy_scans": healthy_scans,
        "diseased_scans": diseased_scans
    }

# --- Plant Disease Analysis (Scan) ---

@app.post("/api/scan")
async def scan_plant(
    file: UploadFile = File(...),
    selected_crop: Optional[str] = Form(None)
):
    """
    Performs fresh AI plant disease inference on the uploaded leaf image.
    Enforces state isolation, records results in database, and returns diagnosis.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (JPEG, PNG, WebP).")

    # Generate unique filename for persistent image storage
    file_ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run fresh inference (ensures no stale result is reused)
    result = run_ai_inference(saved_path, selected_crop)
    result["image_url"] = f"/uploads/{unique_filename}"
    result["original_filename"] = file.filename

    # Save record to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO scans (
        scan_id, timestamp, image_url, original_filename, identified_crop,
        detection_status, disease_name, disease_name_hi, disease_name_mr,
        confidence_percent, severity_level, severity_score, symptoms, symptoms_hi, symptoms_mr,
        recommended_action, recommended_action_hi, recommended_action_mr,
        fertilizer_recommendation, fertilizer_recommendation_hi, fertilizer_recommendation_mr,
        source_reference, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result["scan_id"],
        result["timestamp"],
        result["image_url"],
        result["original_filename"],
        result["identified_crop"],
        result["detection_status"],
        result.get("disease_name"),
        result.get("disease_name_hi"),
        result.get("disease_name_mr"),
        result.get("confidence_percent", 0.0),
        result.get("severity_level"),
        result.get("severity_score"),
        result.get("symptoms"),
        result.get("symptoms_hi"),
        result.get("symptoms_mr"),
        result.get("recommended_action"),
        result.get("recommended_action_hi"),
        result.get("recommended_action_mr"),
        result.get("fertilizer_recommendation"),
        result.get("fertilizer_recommendation_hi"),
        result.get("fertilizer_recommendation_mr"),
        result.get("source_reference"),
        result.get("guidance") or result.get("care_guidance")
    ))
    conn.commit()
    conn.close()

    return result

@app.get("/api/scans")
def get_scan_history(
    status: Optional[str] = Query(None),
    limit: int = 50
):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM scans WHERE detection_status = ? ORDER BY timestamp DESC LIMIT ?", (status, limit))
    else:
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/scans/{scan_id}")
def get_scan_detail(scan_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return dict(row)

@app.delete("/api/scans/{scan_id}")
def delete_scan(scan_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM scans WHERE scan_id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan not found.")
    
    # Try to clean up image on disk
    if row["image_url"]:
        img_name = os.path.basename(row["image_url"])
        local_file = os.path.join(UPLOAD_DIR, img_name)
        if os.path.exists(local_file):
            try:
                os.remove(local_file)
            except Exception:
                pass

    cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Scan {scan_id} deleted successfully."}

# --- Crops Database ---

@app.get("/api/crops")
def get_crops(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM crops WHERE 1=1"
    params = []
    
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
        
    if search:
        search_like = f"%{search}%"
        query += " AND (name_en LIKE ? OR name_hi LIKE ? OR name_mr LIKE ? OR scientific_name LIKE ?)"
        params.extend([search_like, search_like, search_like, search_like])
        
    query += " ORDER BY category, name_en"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    crops_list = []
    for r in rows:
        d = dict(r)
        d["growth_stages"] = json.loads(d["growth_stages"]) if d.get("growth_stages") else []
        d["common_pests"] = json.loads(d["common_pests"]) if d.get("common_pests") else []
        d["common_deficiencies"] = json.loads(d["common_deficiencies"]) if d.get("common_deficiencies") else []
        crops_list.append(d)
        
    return crops_list

@app.get("/api/crops/{crop_id}")
def get_crop_detail(crop_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crops WHERE id = ?", (crop_id,))
    crop = cursor.fetchone()
    if not crop:
        conn.close()
        raise HTTPException(status_code=404, detail="Crop not found")
        
    cursor.execute("SELECT * FROM diseases WHERE crop_id = ?", (crop_id,))
    diseases = [dict(d) for d in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM fertilizers WHERE crop_id = ?", (crop_id,))
    fertilizers = [dict(f) for f in cursor.fetchall()]
    
    conn.close()
    
    d = dict(crop)
    d["growth_stages"] = json.loads(d["growth_stages"]) if d.get("growth_stages") else []
    d["common_pests"] = json.loads(d["common_pests"]) if d.get("common_pests") else []
    d["common_deficiencies"] = json.loads(d["common_deficiencies"]) if d.get("common_deficiencies") else []
    d["diseases"] = diseases
    d["fertilizers"] = fertilizers
    return d

# --- Diseases & Fertilizers Knowledge ---

@app.get("/api/diseases")
def get_diseases(crop_id: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if crop_id:
        cursor.execute("SELECT * FROM diseases WHERE crop_id = ?", (crop_id,))
    else:
        cursor.execute("SELECT * FROM diseases ORDER BY crop_name, name_en")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/fertilizers")
def get_fertilizers(crop_id: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if crop_id:
        cursor.execute("SELECT * FROM fertilizers WHERE crop_id = ?", (crop_id,))
    else:
        cursor.execute("SELECT * FROM fertilizers ORDER BY crop_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Commercial Products Catalogue ---

@app.get("/api/products")
def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category and category != "All":
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
        
    if search:
        search_like = f"%{search}%"
        query += " AND (name LIKE ? OR brand LIKE ? OR manufacturer LIKE ? OR nutrient_composition LIKE ?)"
        params.extend([search_like, search_like, search_like, search_like])
        
    query += " ORDER BY name"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Multilingual AI Chatbot ---

class ChatRequest(BaseModel):
    query: str
    language: str = "en"
    current_scan: Optional[Dict[str, Any]] = None

@app.post("/api/chat")
def chat_with_assistant(req: ChatRequest):
    return generate_agricultural_response(
        query=req.query,
        language=req.language,
        current_scan=req.current_scan
    )

@app.get("/api/suggested-questions")
def get_suggested_questions():
    return SUGGESTED_QUESTIONS

# --- Admin API ---

class ProductCreate(BaseModel):
    name: str
    brand: str
    manufacturer: str
    category: str
    nutrient_composition: str
    pack_size: str
    approx_price_inr: float
    usage_instructions: str
    safety_precautions: str
    source_and_date: str

@app.post("/api/admin/products")
def create_product(prod: ProductCreate):
    prod_id = f"prod_{uuid.uuid4().hex[:8]}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (id, name, brand, manufacturer, category, nutrient_composition, pack_size, approx_price_inr, usage_instructions, safety_precautions, source_and_date, verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        prod_id, prod.name, prod.brand, prod.manufacturer, prod.category,
        prod.nutrient_composition, prod.pack_size, prod.approx_price_inr,
        prod.usage_instructions, prod.safety_precautions, prod.source_and_date
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "id": prod_id, "message": "Agricultural product added successfully."}

# --- Automated Verification Tests Suite ---

@app.post("/api/test/run")
def run_automated_tests():
    """
    Automated test suite verifying:
    1. Healthy plant analysis (Case B: NO DISEASE DETECTED)
    2. Diseased plant analysis (Case A: DISEASE DETECTED with severity)
    3. Unclear / blurry image handling (Case C: UNABLE TO CONFIRM DISEASE)
    4. Out-of-distribution non-plant image (Case C: UNABLE TO CONFIRM)
    5. Rapid consecutive uploads state reset (isolation test)
    """
    import numpy as np
    from PIL import Image, ImageDraw
    import tempfile

    test_results = []
    
    # Helper to test an image safely
    def test_image(img, crop, expected_status, test_name):
        tmp_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex}.jpg")
        try:
            img.save(tmp_path, "JPEG")
            res = run_ai_inference(tmp_path, crop)
            passed = res["detection_status"] == expected_status
            entry = {
                "test_name": test_name,
                "passed": passed,
                "status": res["detection_status"],
                "confidence": res.get("confidence_percent"),
                "expected": expected_status
            }
            if "disease_name" in res:
                entry["disease"] = res.get("disease_name")
            if "severity_level" in res:
                entry["severity"] = res.get("severity_level")
            if "reason" in res:
                entry["reason"] = res.get("reason")
            return res, entry
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # Test 1: Synthetic Healthy Leaf (Pure green, zero necrosis)
    healthy_img = Image.new("RGB", (256, 256), color=(40, 160, 45))
    draw = ImageDraw.Draw(healthy_img)
    draw.line([(128, 20), (128, 236)], fill=(55, 185, 60), width=3)
    draw.line([(128, 100), (60, 60)], fill=(55, 185, 60), width=2)
    draw.line([(128, 140), (200, 100)], fill=(55, 185, 60), width=2)
    _, t1 = test_image(healthy_img, "tomato", "NO_DISEASE_DETECTED", "Healthy Plant Detection (Case B)")
    test_results.append(t1)

    # Test 2: Diseased Leaf with Concentric Necrotic Lesions (Early Blight)
    diseased_img = Image.new("RGB", (256, 256), color=(60, 140, 50))
    draw2 = ImageDraw.Draw(diseased_img)
    draw2.ellipse([(60, 60), (140, 140)], fill=(65, 45, 30))
    draw2.ellipse([(80, 80), (120, 120)], fill=(35, 25, 15))
    draw2.ellipse([(150, 130), (210, 190)], fill=(160, 140, 40)) # chlorosis halo
    draw2.ellipse([(165, 145), (195, 175)], fill=(50, 30, 20))
    _, t2 = test_image(diseased_img, "tomato", "DISEASE_DETECTED", "Disease Detection & Severity Assessment (Case A)")
    test_results.append(t2)

    # Test 3: Blurry / low feature image (Case C: UNABLE TO CONFIRM)
    blurry_img = Image.new("RGB", (256, 256), color=(128, 128, 128))
    _, t3 = test_image(blurry_img, "tomato", "UNABLE_TO_CONFIRM", "Blurry / Featureless Image Rejection (Case C)")
    test_results.append(t3)

    # Test 4: Out-Of-Distribution Non-Plant (e.g., blue abstract object)
    ood_img = Image.new("RGB", (256, 256), color=(20, 40, 180)) # bright blue
    _, t4 = test_image(ood_img, "tomato", "UNABLE_TO_CONFIRM", "Out-Of-Distribution Non-Plant Rejection (Case C)")
    test_results.append(t4)

    # Test 5: Scan ID Isolation & No Fallback Leakage
    p_a = os.path.join(tempfile.gettempdir(), f"test_a_{uuid.uuid4().hex}.jpg")
    p_b = os.path.join(tempfile.gettempdir(), f"test_b_{uuid.uuid4().hex}.jpg")
    try:
        healthy_img.save(p_a, "JPEG")
        diseased_img.save(p_b, "JPEG")
        scan_a = run_ai_inference(p_a, "tomato")
        scan_b = run_ai_inference(p_b, "potato")
        passed_isolation = (
            scan_a["scan_id"] != scan_b["scan_id"] and
            scan_a["detection_status"] == "NO_DISEASE_DETECTED" and
            scan_b["detection_status"] == "DISEASE_DETECTED" and
            scan_a.get("disease_name") is None and
            scan_b.get("disease_name") is not None
        )
        test_results.append({
            "test_name": "Scan Isolation & Anti-Leakage Verification",
            "passed": passed_isolation,
            "scan_a_id": scan_a["scan_id"],
            "scan_b_id": scan_b["scan_id"],
            "expected": "Unique Scan IDs and zero prediction crosstalk"
        })
    finally:
        for p in [p_a, p_b]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    all_passed = all(t["passed"] for t in test_results)
    return {
        "status": "PASS" if all_passed else "FAIL",
        "total_tests": len(test_results),
        "passed_tests": sum(1 for t in test_results if t["passed"]),
        "results": test_results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
