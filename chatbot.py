"""
Multilingual Agricultural Advisory Chatbot for Indian Farmers.
Supports English, Hindi (हिन्दी), and Marathi (मराठी).
Uses verified database records, current scan context, and state agricultural university recommendations.
"""

from typing import Dict, Any, List, Optional
import json
from database import get_db_connection

# Predefined suggested question chips for farmers in 3 languages
SUGGESTED_QUESTIONS = {
    "en": [
        "What are the symptoms and cure for Tomato Early Blight?",
        "Which fertilizer is best for Rice tillering stage?",
        "How can I prevent Late Blight in Potato during cloudy weather?",
        "What is the recommended dose of Zinc Sulphate for Paddy?",
        "How to control Whitefly causing leaf curl virus in Tomato?",
        "Tell me about the current scan results and treatment."
    ],
    "hi": [
        "टमाटर के अगेती झुलसा रोग के लक्षण और उपचार क्या हैं?",
        "धान में कल्ले फूटने के समय कौन सा खाद डालना चाहिए?",
        "आलू में पछेती झुलसा से बचाव कैसे करें?",
        "धान में खैरा रोग के लिए जिंक सल्फेट की सही मात्रा क्या है?",
        "टमाटर में सफेद मक्खी और पत्ता मरोड़ रोग कैसे रोकें?",
        "मेरी वर्तमान जांच (स्कैन) के परिणाम और उपाय बताइए।"
    ],
    "mr": [
        "टोमॅटोवरील लवकर येणाऱ्या करपा रोगाची लक्षणे व उपाय काय आहेत?",
        "भाताच्या फुटव्यांच्या वाढीसाठी कोणते खत योग्य आहे?",
        "ढगाळ हवामानात बटाट्यावरील करपा कसा रोखावा?",
        "भातातील जस्त कमतरतेसाठी (खैरा) झिंक सल्फेट किती वापरावे?",
        "टोमॅटोमधील पांढरी माशी आणि चुरडा-मुरडा कसा नियंत्रित करावा?",
        "माझ्या आत्ताच्या स्कॅनचे परिणाम आणि उपाय काय आहेत?"
    ]
}

def generate_agricultural_response(
    query: str,
    language: str = "en",
    current_scan: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates verified agricultural advice tailored to the query, language,
    and optional active scan context.
    """
    lang = language.lower() if language in ["en", "hi", "mr"] else "en"
    q_lower = query.lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Check if user asks about their recent/current scan
    if ("scan" in q_lower or "result" in q_lower or "disease" in q_lower or "तपासणी" in q_lower or "स्कॅन" in q_lower or "जांच" in q_lower or "परिणाम" in q_lower) and current_scan:
        status = current_scan.get("detection_status")
        crop = current_scan.get("identified_crop", "Crop")
        
        if status == "DISEASE_DETECTED":
            d_name = current_scan.get("disease_name", "Disease")
            conf = current_scan.get("confidence_percent", 90)
            sev = current_scan.get("severity_level", "Moderate")
            action = current_scan.get("recommended_action")
            fert = current_scan.get("fertilizer_recommendation")

            if lang == "hi":
                d_name_hi = current_scan.get("disease_name_hi", d_name)
                action_hi = current_scan.get("recommended_action_hi", action)
                response_text = (
                    f"🌾 **आपकी जांच (Scan {current_scan.get('scan_id', '')}) का परिणाम:**\n\n"
                    f"• **फसल:** {crop}\n"
                    f"• **पहचाना गया रोग:** {d_name_hi}\n"
                    f"• **एआई विश्वसनीयता (Confidence):** {conf}%\n"
                    f"• **रोग की तीव्रता:** {sev}\n\n"
                    f"📋 **अनुशंसित उपचार (ICAR अनुसार):**\n{action_hi}\n\n"
                    f"🌱 **उर्वरक सलाह:**\n{current_scan.get('fertilizer_recommendation_hi', fert)}\n\n"
                    f"⚠️ *कृषि विश्वविद्यालय की सलाह:* हमेशा रोग की शुरुआती अवस्था में ही अनुशंसित मात्रा में छिड़काव करें और सुरक्षा उपकरण पहनें।"
                )
            elif lang == "mr":
                d_name_mr = current_scan.get("disease_name_mr", d_name)
                action_mr = current_scan.get("recommended_action_mr", action)
                response_text = (
                    f"🌾 **तुमच्या पीक तपासणीचा (Scan {current_scan.get('scan_id', '')}) तपशील:**\n\n"
                    f"• **पीक:** {crop}\n"
                    f"• **आढळलेला रोग:** {d_name_mr}\n"
                    f"• **एआय खात्री (Confidence):** {conf}%\n"
                    f"• **रोगाची तीव्रता:** {sev}\n\n"
                    f"📋 **शिफारस केलेले उपाय (कृषी विद्यापीठ सल्ला):**\n{action_mr}\n\n"
                    f"🌱 **खत व्यवस्थापन:**\n{current_scan.get('fertilizer_recommendation_mr', fert)}\n\n"
                    f"⚠️ *महत्त्वाची सूचना:* कीटकनाशकांची फवारणी करताना तोंडाला मास्क लावा आणि योग्य ती खबरदारी घ्या."
                )
            else:
                response_text = (
                    f"🌾 **Your Scan Analysis ({current_scan.get('scan_id', '')}):**\n\n"
                    f"• **Crop:** {crop}\n"
                    f"• **Disease Detected:** {d_name}\n"
                    f"• **AI Confidence:** {conf}%\n"
                    f"• **Assessed Severity:** {sev}\n\n"
                    f"📋 **Recommended Management (ICAR Verified):**\n{action}\n\n"
                    f"🌱 **Nutrient & Fertilizer Care:**\n{fert}\n\n"
                    f"⚠️ *Precaution:* Avoid overhead sprinkler watering to reduce humidity around foliage."
                )
            conn.close()
            return {
                "response": response_text,
                "language": lang,
                "references": [current_scan.get("source_reference", "ICAR Verified Guidelines")]
            }
        elif status == "NO_DISEASE_DETECTED":
            if lang == "hi":
                response_text = (
                    f"✅ **आपकी फसल स्वस्थ है!**\n\n"
                    f"आपके अपलोड किए गए {crop} के पत्ते पर कोई रोग नहीं पाया गया है (विश्वसनीयता: {current_scan.get('confidence_percent')}%)।\n\n"
                    f"🌿 **देखभाल सलाह:**\n{current_scan.get('care_guidance_hi', current_scan.get('care_guidance'))}\n\n"
                    f"उचित सिंचाई और संतुलित खाद जारी रखें।"
                )
            elif lang == "mr":
                response_text = (
                    f"✅ **तुमचे पीक पूर्णपणे निरोगी आहे!**\n\n"
                    f"तुमच्या {crop} पिकाच्या पानावर कोणताही बुरशी अथवा कीड आढळली नाही (खात्री: {current_scan.get('confidence_percent')}%)।\n\n"
                    f"🌿 **पिकाची काळजी:**\n{current_scan.get('care_guidance_mr', current_scan.get('care_guidance'))}\n\n"
                    f"वेळेवर पाणी व निंबोळी अर्काची फवारणी चालू ठेवा."
                )
            else:
                response_text = (
                    f"✅ **Your Plant is Healthy!**\n\n"
                    f"No disease was detected on your {crop} foliage (Confidence: {current_scan.get('confidence_percent')}%).\n\n"
                    f"🌿 **Care Guidance:**\n{current_scan.get('care_guidance')}"
                )
            conn.close()
            return {
                "response": response_text,
                "language": lang,
                "references": ["ICAR Good Agricultural Practices"]
            }

    # 2. Database Keyword Match for Disease
    cursor.execute("SELECT * FROM diseases")
    all_diseases = cursor.fetchall()
    matched_disease = None
    for d in all_diseases:
        if (d["name_en"].lower() in q_lower or 
            d["name_hi"] in query or 
            d["name_mr"] in query or
            d["crop_name"].lower() in q_lower or
            d["id"] in q_lower):
            matched_disease = d
            break

    if matched_disease:
        if lang == "hi":
            response_text = (
                f"🌿 **{matched_disease['name_hi']} ({matched_disease['name_en']}) - {matched_disease['crop_name']}**\n\n"
                f"🔍 **लक्षण:**\n{matched_disease['symptoms_hi']}\n\n"
                f"⚠️ **कारण:**\n{matched_disease['causes_hi']}\n\n"
                f"🛡️ **रोकथाम:**\n{matched_disease['prevention_hi']}\n\n"
                f"💊 **उपचार (रासायनिक व जैविक):**\n{matched_disease['treatment_hi']}\n\n"
                f"📌 *स्रोत:* भारतीय कृषि अनुसंधान परिषद (ICAR) दिशा-निर्देश"
            )
        elif lang == "mr":
            response_text = (
                f"🌿 **{matched_disease['name_mr']} ({matched_disease['name_en']}) - {matched_disease['crop_name']}**\n\n"
                f"🔍 **लक्षणे:**\n{matched_disease['symptoms_mr']}\n\n"
                f"⚠️ **कारणे:**\n{matched_disease['causes_mr']}\n\n"
                f"🛡️ **प्रतिबंधात्मक उपाय:**\n{matched_disease['prevention_mr']}\n\n"
                f"💊 **उपचार व फवारणी:**\n{matched_disease['treatment_mr']}\n\n"
                f"📌 *स्रोत:* महात्मा फुले कृषी विद्यापीठ (MPKV) व ICAR शिफारसी"
            )
        else:
            response_text = (
                f"🌿 **{matched_disease['name_en']} ({matched_disease['crop_name']})**\n\n"
                f"🔍 **Visible Symptoms:**\n{matched_disease['symptoms_en']}\n\n"
                f"⚠️ **Favorable Causes:**\n{matched_disease['causes_en']}\n\n"
                f"🛡️ **Prevention Practices:**\n{matched_disease['prevention_en']}\n\n"
                f"💊 **Treatment & Management:**\n{matched_disease['treatment_en']}\n\n"
                f"📌 *Authority:* ICAR Approved Agrochemical & IPM Framework"
            )
        conn.close()
        return {
            "response": response_text,
            "language": lang,
            "references": ["ICAR Crop Protection Advisory"]
        }

    # 3. Fertilizer Keyword Match
    cursor.execute("SELECT * FROM fertilizers")
    all_ferts = cursor.fetchall()
    matched_fert = None
    for f in all_ferts:
        if (f["crop_name"].lower() in q_lower or 
            "fertilizer" in q_lower or 
            "खाद" in query or 
            "खत" in query or
            "urea" in q_lower or
            "dap" in q_lower or
            "zinc" in q_lower or
            "जिंक" in query):
            matched_fert = f
            break

    if matched_fert:
        if lang == "hi":
            response_text = (
                f"🌱 **{matched_fert['crop_name']} के लिए उर्वरक व पोषण प्रबंधन:**\n\n"
                f"• **पोषक तत्व:** {matched_fert['nutrient_name']}\n"
                f"• **उद्देश्य:** {matched_fert['purpose_hi']}\n"
                f"• **संरचना:** {matched_fert['composition']}\n"
                f"• **अनुशंसित खुराक:** {matched_fert['dosage']}\n"
                f"• **डालने का सही समय व तरीका:** {matched_fert['application_timing']}\n"
                f"• **ज़रूरी सावधानियां:** {matched_fert['precautions']}\n\n"
                f"📌 *स्रोत:* {matched_fert['source_authority']}"
            )
        elif lang == "mr":
            response_text = (
                f"🌱 **{matched_fert['crop_name']} पिकासाठी खत व्यवस्थापन सल्ला:**\n\n"
                f"• **खताचे नाव:** {matched_fert['nutrient_name']}\n"
                f"• **महत्त्व:** {matched_fert['purpose_mr']}\n"
                f"• **प्रमाण व घटक:** {matched_fert['composition']}\n"
                f"• **शिफारस केलेली मात्रा:** {matched_fert['dosage']}\n"
                f"• **देण्याची वेळ व पद्धत:** {matched_fert['application_timing']}\n"
                f"• **महत्त्वाची काळजी:** {matched_fert['precautions']}\n\n"
                f"📌 *स्रोत:* {matched_fert['source_authority']}"
            )
        else:
            response_text = (
                f"🌱 **{matched_fert['crop_name']} Fertilizer & Nutrient Guidance:**\n\n"
                f"• **Nutrient / Formulation:** {matched_fert['nutrient_name']}\n"
                f"• **Agronomic Purpose:** {matched_fert['purpose_en']}\n"
                f"• **Composition:** {matched_fert['composition']}\n"
                f"• **Recommended Dosage:** {matched_fert['dosage']}\n"
                f"• **Timing & Application:** {matched_fert['application_timing']}\n"
                f"• **Precautions:** {matched_fert['precautions']}\n\n"
                f"📌 *Authority Source:* {matched_fert['source_authority']}"
            )
        conn.close()
        return {
            "response": response_text,
            "language": lang,
            "references": [matched_fert['source_authority']]
        }

    conn.close()

    # Default fallback response in chosen language
    if lang == "hi":
        return {
            "response": (
                "नमस्ते किसान भाई! 🙏 मैं आपका **स्मार्ट कृषि मित्र एआई सहायक** हूँ।\n\n"
                "मैं आपकी इन विषयों पर सहायता कर सकता हूँ:\n"
                "1. 📸 **पौधे की बीमारी की पहचान:** ऊपर फोटो अपलोड करें और तुरंत सटीक जांच पाएं।\n"
                "2. 🌾 **फसल सुरक्षा:** टमाटर, आलू, धान, गेहूं, मक्का, कपास, मिर्च, सोयाबीन के रोगों का इलाज।\n"
                "3. 🌱 **उर्वरक सलाह:** यूरिया, डीएपी, 19:19:19, जिंक सल्फेट की वैज्ञानिक खुराक (ICAR अनुसार)।\n"
                "4. 💧 **सिंचाई व कीटनाशक सावधानी।**\n\n"
                "कृपया अपनी फसल या समस्या का नाम लिखकर पूछें या सुझाए गए प्रश्नों में से चुनें!"
            ),
            "language": "hi",
            "references": ["ICAR Agricultural Knowledge Repository"]
        }
    elif lang == "mr":
        return {
            "response": (
                "नमस्कार शेतकरी मित्रहो! 🙏 मी तुमचा **स्मार्ट कृषी मित्र एआई सहाय्यक** आहे.\n\n"
                "मी तुम्हाला खालील गोष्टींमध्ये मदत करू शकतो:\n"
                "1. 📸 **पीक रोग निदान:** पिकाच्या किंवा पानाचा फोटो अपलोड करून अचूक निदान मिळवा.\n"
                "2. 🌾 **पीक संरक्षण:** टोमॅटो, बटाटा, भात, गहू, कापूस, मिरची, द्राक्षे आणि सोयाबीनवरील रोगांचे उपाय.\n"
                "3. 🌱 **खत व्यवस्थापन:** युरिया, डीएपी, पोटॅश, १९:१९:१९ व सूक्ष्म अन्नद्रव्यांची योग्य मात्रा (MPKV नुसार).\n"
                "4. 💧 **हवामानानुसार सिंचन व फवारणी सल्ला.**\n\n"
                "कृपया तुमचा प्रश्न किंवा पिकाचे नाव विचारा किंवा वरील पर्यायांवर क्लिक करा!"
            ),
            "language": "mr",
            "references": ["MPKV Rahuri & ICAR Portal"]
        }
    else:
        return {
            "response": (
                "Hello Farmer! 🙏 I am your **Smart Agricultural AI Assistant** for India.\n\n"
                "I can assist you with:\n"
                "1. 📸 **Plant Disease Diagnosis:** Upload a leaf image to get instant AI analysis with severity assessment.\n"
                "2. 🌾 **Crop Protection:** Comprehensive IPM remedies for Tomato, Potato, Rice, Wheat, Cotton, Chilli, Grapes, and Soybean.\n"
                "3. 🌱 **Fertilizer Guidance:** ICAR-verified dosage for Urea, DAP, NPK complexes, Zinc Sulphate, and Calcium Nitrate.\n"
                "4. 💧 **Irrigation & Weather Alerts.**\n\n"
                "Feel free to ask a question, select a prompt chip, or scan a plant above!"
            ),
            "language": "en",
            "references": ["ICAR & State Agricultural Universities"]
        }
