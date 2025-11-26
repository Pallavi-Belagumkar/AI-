from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import base64
from PIL import Image
import io
import numpy as np

app = Flask(__name__)
CORS(app)

# Agricultural knowledge database
agricultural_database = {
    "currentWeather": {
        "temperature": "28°C",
        "humidity": "65%",
        "rainfall": "15mm",
        "windSpeed": "12 km/h",
        "condition": "ಬೆಳಗಿನ ಚಳಿ"
    },
    
    "soilTypes": {
        "ಕಪ್ಪು ಮಣ್ಣು": "ಇದು ಕಪ್ಪು ಬಣ್ಣದ ಮಣ್ಣು, ಹೆಚ್ಚು ನೀರು ತಡೆಹಿಡಿಯುವ ಸಾಮರ್ಥ್ಯ, ಹೆಚ್ಚು ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ",
        "ಕೆಂಪು ಮಣ್ಣು": "ಕಬ್ಬು, ಹತ್ತಿ, ಗೋದಿ ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ, ಕಬ್ಬಿಣ ಆಕ್ಸೈಡ್ ಹೆಚ್ಚು",
        "ಜೇಡಿ ಮಣ್ಣು": "ನೀರು ತಡೆಹಿಡಿಯುವ ಸಾಮರ್ಥ್ಯ ಹೆಚ್ಚು, ಭತ್ತ, ಕಬ್ಬು ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ",
        "ಮರಳು ಮಣ್ಣು": "ನೀರು ತಡೆಹಿಡಿಯುವ ಸಾಮರ್ಥ್ಯ ಕಡಿಮೆ, ಕಡಲೆಕಾಯಿ, ರಾಗಿ ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ",
        "ಮೆಕ್ಕಲು ಮಣ್ಣು": "ನದಿ ಕಣಿವೆಗಳಲ್ಲಿ ಕಂಡುಬರುತ್ತದೆ, ಎಲ್ಲಾ ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ"
    },
    
    "irrigationMethods": {
        "ಸಾಂಪ್ರದಾಯಿಕ ನೀರಾವರಿ": "ನೀರಿನ ದುರ್ಬಳಕೆ ಹೆಚ್ಚು, ಕಾರ್ಯಕ್ಷಮತೆ ಕಡಿಮೆ",
        "ಟಪ್ಪಾವರಿ ವಿಧಾನ": "ನೀರು ಉಳಿತಾಯ 70%, ಗಿಡಮೂಲಿಕೆಗಳಿಗೆ ನೇರವಾಗಿ ನೀರು",
        "ಸ್ಪ್ರಿಂಕ್ಲರ್ ವಿಧಾನ": "ನೀರು ಚದುರಿಸುವ ವಿಧಾನ, ದೊಡ್ಡ ಪ್ರದೇಶಗಳಿಗೆ ಉತ್ತಮ",
        "ಡ್ರಿಪ್ ಇರಿಗೇಶನ್": "ನೀರು ಉಳಿತಾಯ 90%, ಪ್ರತಿ ಗಿಡಕ್ಕೆ ನೇರವಾಗಿ ನೀರು",
        "ಮಳೆ ನೀರು ಸಂಗ್ರಹ": "ಮಳೆ ನೀರು ಸಂಗ್ರಹಿಸಿ ಬಳಸುವ ವಿಧಾನ"
    },
    
    "plantTypes": {
        "ಧಾನ್ಯ ಬೆಳೆಗಳು": "ಭತ್ತ, ಗೋದಿ, ಜೋಳ, ರಾಗಿ, ಬಾರ್ಲಿ",
        "ದ್ವಿದಳ ಧಾನ್ಯಗಳು": "ಕಡಲೆಕಾಯಿ, ಹರಿಕೆ, ಅವರೆ, ಹೆಸರು",
        "ತೈಲ ಬೀಜ ಬೆಳೆಗಳು": "ಸೂರ್ಯಕಾಂತಿ, ನೆಲಗಡಲೆ, ಸೋಯಾ, ಎಳ್ಳು",
        "ನಾರು ಬೆಳೆಗಳು": "ಹತ್ತಿ, ಪಟ್ಟು, ಜುಟ್",
        "ತರಕಾರಿ ಬೆಳೆಗಳು": "ಟೊಮ್ಯಾಟೊ, ಈರುಳ್ಳಿ, ಬಟಾಟೆ, ಮೆಣಸಿನಕಾಯಿ",
        "ಹಣ್ಣು ಬೆಳೆಗಳು": "ಮಾವು, ಕಿತ್ತಳೆ, ದ್ರಾಕ್ಷಿ, ಬಾಳೆ",
        "ಮಸಾಲೆ ಬೆಳೆಗಳು": "ಮೆಣಸು, ಏಲಕ್ಕಿ, ಲವಂಗ, ಅರಿಶಿನ"
    },
    
    "fertilizers": {
        "ಸಾವಯವ ಗೊಬ್ಬರ": "ಕಂಪೋಸ್ಟ್, ಹಸಿರೆಲೆ ಗೊಬ್ಬರ, ಜೀವಾಣು ಗೊಬ್ಬರ, ಕೊಬ್ಬರಿ ತಿರುಳು",
        "ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ": "ಯೂರಿಯಾ, DAP, ಪೊಟಾಷ್, ಸೂಪರ್ ಫಾಸ್ಫೇಟ್",
        "ಜೈವಿಕ ಗೊಬ್ಬರ": "ರೈಜೋಬಿಯಂ, ಅಜೋಟೊಬ್ಯಾಕ್ಟರ್, ನೀಲಿ ಹಸಿರು ಶೈವಲ"
    },
    
    "cropDiseases": {
        "ಭತ್ತ": ["ಬ್ಲಾಸ್ಟ್", "ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಬ್ಲೈಟ್", "ಟಂಗ್ರೋ", "ಭತ್ತ ಕಾಂಡ ಕೊಳೆ"],
        "ಗೋದಿ": ["ತುರುಚೆ ಹುಳು", "ಕಂದು ತುಕ್ಕು", "ಪುಡಿತುಕ್ಕು"],
        "ಕಬ್ಬು": ["ಕೆಂಪು ಕೊಳೆ", "ಚಿಟ್ಟೆ ಹುಳು", "ಸಿಡುಬು"],
        "ಹತ್ತಿ": ["ಬಿಳಿ ಹುಳು", "ಕೆಂಪು ಹುಳು", "ಎಲೆ ಸುಕ್ಕು"]
    },
    
    "cropCalendar": {
        "ಭತ್ತ": {
            "sowing": ["ಜೂನ್", "ಜುಲೈ"],
            "harvesting": ["ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್"]
        },
        "ರಾಗಿ": {
            "sowing": ["ಜೂನ್", "ಜುಲೈ"],
            "harvesting": ["ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್"]
        },
        "ಜೋಳ": {
            "sowing": ["ಜೂನ್", "ಜುಲೈ"],
            "harvesting": ["ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್"]
        },
        "ಕಬ್ಬು": {
            "sowing": ["ಜನವರಿ", "ಫೆಬ್ರವರಿ"],
            "harvesting": ["ಡಿಸೆಂಬರ್", "ಜನವರಿ"]
        },
        "ಹತ್ತಿ": {
            "sowing": ["ಜೂನ್", "ಜುಲೈ"],
            "harvesting": ["ಡಿಸೆಂಬರ್", "ಜನವರಿ"]
        }
    }
}

# Language-specific responses
responses = {
    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು KrishiSiri AI ಸಹಾಯಕ. ನಿಮ್ಮ ಕೃಷಿ ಸಮಸ್ಯೆಗಳ ಬಗ್ಗೆ ಹೇಳಿ.",
        "unknown": "ಕ್ಷಮಿಸಿ, ನಾನು ಇನ್ನೂ ಆ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಸಿದ್ಧನಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಕೃಷಿ ಸಮಸ್ಯೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ.",
        "weather": "ನಿಮ್ಮ ಪ್ರದೇಶದ ಪ್ರಸ್ತುತ ಹವಾಮಾನ: ತಾಪಮಾನ: 28°C, ಆರ್ದ್ರತೆ: 65%, ಮಳೆ: 15mm, ಗಾಳಿ ವೇಗ: 12 km/h, ಸ್ಥಿತಿ: ಬೆಳಗಿನ ಚಳಿ. ಸಲಹೆ: ಇಂದಿನ ಹವಾಮಾನಕ್ಕೆ ತಕ್ಕಂತೆ ಕೃಷಿ ಕಾರ್ಯಗಳನ್ನು ನಿರ್ವಹಿಸಿ.",
        "soil": "ಮಣ್ಣಿನ ಪ್ರಕಾರಗಳು: ಕಪ್ಪು ಮಣ್ಣು, ಕೆಂಪು ಮಣ್ಣು, ಜೇಡಿ ಮಣ್ಣು, ಮರಳು ಮಣ್ಣು, ಮೆಕ್ಕಲು ಮಣ್ಣು. ಸಲಹೆ: ನಿಮ್ಮ ಪ್ರದೇಶದ ಮಣ್ಣಿನ ಪ್ರಕಾರ ತಿಳಿದುಕೊಂಡು ಅದಕ್ಕೆ ತಕ್ಕ ಬೆಳೆ ಆಯ್ಕೆ ಮಾಡಿ.",
        "irrigation": "ನೀರಾವರಿ ವಿಧಾನಗಳು: ಸಾಂಪ್ರದಾಯಿಕ ನೀರಾವರಿ, ಟಪ್ಪಾವರಿ ವಿಧಾನ, ಸ್ಪ್ರಿಂಕ್ಲರ್ ವಿಧಾನ, ಡ್ರಿಪ್ ಇರಿಗೇಶನ್, ಮಳೆ ನೀರು ಸಂಗ್ರಹ. ಸಲಹೆ: ನಿಮ್ಮ ಬೆಳೆ ಮತ್ತು ಮಣ್ಣಿನ ಪ್ರಕಾರಕ್ಕೆ ತಕ್ಕ ನೀರಾವರಿ ವಿಧಾನ ಆಯ್ಕೆ ಮಾಡಿ.",
        "fertilizer": "ಗೊಬ್ಬರದ ಪ್ರಕಾರಗಳು: ಸಾವಯವ ಗೊಬ್ಬರ, ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ, ಜೈವಿಕ ಗೊಬ್ಬರ. ಸಲಹೆ: ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ ಮತ್ತು ಅದರ ಆಧಾರದ ಮೇಲೆ ಗೊಬ್ಬರ ಬಳಸಿ. ಸಾವಯವ ಗೊಬ್ಬರಗಳು ಮಣ್ಣಿನ ಆರೋಗ್ಯವನ್ನು ಸುಧಾರಿಸುತ್ತವೆ.",
        "cropCalendar": "ನಿಮ್ಮ ಪ್ರದೇಶ ಮತ್ತು ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ಅವಲಂಬಿಸಿ ಬೆಳೆ ಸಮಯ ಬದಲಾಗುತ್ತದೆ. ಮೇಲಿನ ಬೆಳೆ ಕ್ಯಾಲೆಂಡರ್ ನೋಡಿ ಅಥವಾ ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಬೆಳೆಯ ಹೆಸರು ಹೇಳಿ."
    },
    "en": {
        "greeting": "Hello! I am KrishiSiri AI assistant. Tell me about your farming problems.",
        "unknown": "Sorry, I'm not yet prepared to answer that question. Please ask about your farming problems.",
        "weather": "Current weather in your area: Temperature: 28°C, Humidity: 65%, Rainfall: 15mm, Wind Speed: 12 km/h, Condition: Morning chill. Advice: Manage farming activities according to today's weather.",
        "soil": "Soil types: Black soil, Red soil, Clay soil, Sandy soil, Alluvial soil. Advice: Know your area's soil type and choose crops accordingly.",
        "irrigation": "Irrigation methods: Traditional irrigation, Drip irrigation, Sprinkler irrigation, Drip irrigation, Rainwater harvesting. Advice: Choose irrigation method suitable for your crop and soil type.",
        "fertilizer": "Fertilizer types: Organic fertilizer, Chemical fertilizer, Biofertilizer. Advice: Get soil testing done and use fertilizer based on that. Organic fertilizers improve soil health.",
        "cropCalendar": "Crop timing varies depending on your area and soil type. Check the crop calendar above or tell me your specific crop name."
    },
    "hi": {
        "greeting": "नमस्ते! मैं KrishiSiri AI सहायक हूं। अपनी कृषि समस्याओं के बारे में बताएं।",
        "unknown": "क्षमा करें, मैं अभी तक उस प्रश्न का उत्तर देने के लिए तैयार नहीं हूं। कृपया अपनी कृषि समस्याओं के बारे में पूछें।",
        "weather": "आपके क्षेत्र का वर्तमान मौसम: तापमान: 28°C, आर्द्रता: 65%, वर्षा: 15mm, हवा की गति: 12 km/h, स्थिति: सुबह की ठंड। सलाह: आज के मौसम के अनुसार कृषि गतिविधियों का प्रबंधन करें।",
        "soil": "मिट्टी के प्रकार: काली मिट्टी, लाल मिट्टी, चिकनी मिट्टी, बलुई मिट्टी, जलोढ़ मिट्टी। सलाह: अपने क्षेत्र की मिट्टी का प्रकार जानें और उसके अनुसार फसलें चुनें।",
        "irrigation": "सिंचाई के तरीके: पारंपरिक सिंचाई, ड्रिप सिंचाई, स्प्रिंकलर सिंचाई, ड्रिप सिंचाई, वर्षा जल संचयन। सलाह: अपनी फसल और मिट्टी के प्रकार के लिए उपयुक्त सिंचाई विधि चुनें।",
        "fertilizer": "उर्वरक के प्रकार: जैविक उर्वरक, रासायनिक उर्वरक, जैव उर्वरक। सलाह: मिट्टी की जांच करवाएं और उसके आधार पर उर्वरक का उपयोग करें। जैविक उर्वरक मिट्टी के स्वास्थ्य में सुधार करते हैं।",
        "cropCalendar": "आपके क्षेत्र और मिट्टी के प्रकार के आधार पर फसल का समय बदलता रहता है। ऊपर दिए गए फसल कैलेंडर को देखें या मुझे अपनी विशिष्ट फसल का नाम बताएं।"
    },
    "ta": {
        "greeting": "வணக்கம்! நான் KrishiSiri AI உதவியாளர். உங்கள் விவசாய பிரச்சினைகளைப் பற்றி சொல்லுங்கள்.",
        "unknown": "மன்னிக்கவும், அந்த கேள்விக்கு பதிலளிக்க இன்னும் தயாராக இல்லை. தயவு செய்து உங்கள் விவசாய பிரச்சினைகளைப் பற்றி கேளுங்கள்.",
        "weather": "உங்கள் பகுதியின் தற்போதைய வானிலை: வெப்பநிலை: 28°C, ஈரப்பதம்: 65%, மழை: 15mm, காற்றின் வேகம்: 12 km/h, நிலை: காலை குளிர். ஆலோசனை: இன்றைய வானிலைக்கு ஏற்றவாறு விவசாய நடவடிக்கைகளை நிர்வகிக்கவும்.",
        "soil": "மண் வகைகள்: கருமண், சிவப்பு மண், களிமண், மணல் மண், வண்டல் மண். ஆலோசனை: உங்கள் பகுதியின் மண் வகையை அறிந்து அதற்கு ஏற்ற பயிர்களைத் தேர்ந்தெடுக்கவும்.",
        "irrigation": "பாசன முறைகள்: பாரம்பரிய பாசனம், சொட்டுநீர் பாசனம், தெளிப்பான் பாசனம், சொட்டுநீர் பாசனம், மழைநீர் சேகரிப்பு. ஆலோசனை: உங்கள் பயிர் மற்றும் மண் வகைக்கு ஏற்ற பாசன முறையைத் தேர்ந்தெடுக்கவும்.",
        "fertilizer": "உர வகைகள்: கரிம உரம், இரசாயன உரம், உயிர் உரம். ஆலோசனை: மண் சோதனை செய்து, அதன் அடிப்படையில் உரம் பயன்படுத்தவும். கரிம உரங்கள் மண்ணின் ஆரோக்கியத்தை மேம்படுத்துகின்றன.",
        "cropCalendar": "உங்கள் பகுதி மற்றும் மண் வகையைப் பொறுத்து பயிர் நேரம் மாறுபடும். மேலே உள்ள பயிர் காலண்டரைப் பாருங்கள் அல்லது உங்கள் குறிப்பிட்ட பயிரின் பெயரைச் சொல்லுங்கள்."
    },
    "te": {
        "greeting": "నమస్కారం! నేను KrishiSiri AI సహాయకుడిని. మీ వ్యవసాయ సమస్యల గురించి చెప్పండి.",
        "unknown": "క్షమించండి, ఆ ప్రశ్నకు సమాధానం ఇవ్వడానికి నేను ఇంకా సిద్ధంగా లేను. దయచేసి మీ వ్యవసాయ సమస్యల గురించి అడగండి.",
        "weather": "మీ ప్రాంతం యొక్క ప్రస్తుత వాతావరణం: ఉష్ణోగ్రత: 28°C, ఆర్ద్రత: 65%, వర్షపాతం: 15mm, గాలి వేగం: 12 km/h, స్థితి: ఉదయం చలి. సలహా: నేటి వాతావరణానికి అనుగుణంగా వ్యవసాయ కార్యకలాపాలను నిర్వహించండి.",
        "soil": "నేల రకాలు: నల్ల నేల, ఎరుపు నేల, బంకమన్ను, ఇసుక నేల, వెల్లువ నేల. సలహా: మీ ప్రాంతం యొక్క నేల రకాన్ని తెలుసుకుని దానికి తగిన పంటలను ఎంచుకోండి.",
        "irrigation": "నీటిపారుదల పద్ధతులు: సాంప్రదాయ నీటి�पారుదల, డ్రిప్ నీటిపారుదల, స్ప్రింక్లర్ నీటిపారుదల, డ్రిప్ నీటిపారుదల, వర్షపు నీటి సేకరణ. సలహా: మీ పంట మరియు నేల రకానికి తగిన నీటిపారుదల పద్ధతిని ఎంచుకోండి.",
        "fertilizer": "ఎరువుల రకాలు: సేంద్రీయ ఎరువు, రసాయన ఎరువు, బయోఫర్టిలైజర్. సలహా: నేల పరీక్ష చేయించి, దాని ఆధారంగా ఎరువు వాడండి. సేంద్రీయ ఎరువులు నేల ఆరోగ్యాన్ని మెరుగుపరుస్తాయి.",
        "cropCalendar": "మీ ప్రాంతం మరియు నేల రకాన్ని బట్టి పంట సమయం మారుతుంది. పైన ఉన్న పంట క్యాలెండర్‌ను చూడండి లేదా మీ నిర్దిష్ట పంట పేరు చెప్పండి."
    }
}

def get_ai_response(message, language='kn'):
    lower_message = message.lower()
    lang_responses = responses.get(language, responses['kn'])
    
    # Expanded response logic with more agricultural knowledge
    if any(word in lower_message for word in ['ನಮಸ್ಕಾರ', 'hello', 'hi', 'नमस्ते', 'வணக்கம்', 'నమస్కారం']):
        return lang_responses["greeting"]
    
    elif any(word in lower_message for word in ['ಹವಾಮಾನ', 'weather', 'मौसम', 'வானிலை', 'వాతావరణం']):
        return lang_responses["weather"]
    
    elif any(word in lower_message for word in ['ನೀರಾವರಿ', 'irrigation', 'सिंचाई', 'பாசனம்', 'నీటిపారుదల']):
        return lang_responses["irrigation"]
    
    elif any(word in lower_message for word in ['ಮಣ್ಣು', 'soil', 'मिट्टी', 'மண்', 'నేల']):
        return lang_responses["soil"]
    
    elif any(word in lower_message for word in ['ಬೆಳೆ', 'crop', 'फसल', 'பயிர்', 'పంట']) and any(word in lower_message for word in ['ಸಮಯ', 'time', 'समय', 'நேரம்', 'సమయం']):
        return lang_responses["cropCalendar"]
    
    elif any(word in lower_message for word in ['ರೋಗ', 'disease', 'रोग', 'நோய்', 'రోగం']):
        return "ಸಸ್ಯ ರೋಗಗಳು ಮತ್ತು ಕೀಟಗಳ ಬಗ್ಗೆ ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ದಯವಿಟ್ಟು ರೋಗದ ಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ ಅಥವಾ ಸಸ್ಯದ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ. ಸಾಮಾನ್ಯ ರೋಗ ನಿಯಂತ್ರಣ: ನಿಯಮಿತ ನಿಗಾ, ಸೂಕ್ತ ಕೀಟನಾಶಕಗಳು, ಮತ್ತು ರೋಗನಿರೋಧಕ ಬೆಳೆ ಜಾತಿಗಳು."
    
    elif any(word in lower_message for word in ['ಗೊಬ್ಬರ', 'fertilizer', 'उर्वरक', 'உரம்', 'ఎరువు']):
        return lang_responses["fertilizer"]
    
    elif any(word in lower_message for word in ['ಭತ್ತ', 'rice', 'चावल', 'நெல்', 'బియ్యం']):
        crop_info = agricultural_database["cropCalendar"].get("ಭತ್ತ", {})
        sowing = ", ".join(crop_info.get("sowing", []))
        harvesting = ", ".join(crop_info.get("harvesting", []))
        return f"ಭತ್ತ ಬೆಳೆಯ ಸಮಯ: {sowing} ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ, {harvesting} ನಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಬಹುದು. ಭತ್ತ ಬೆಳೆಗೆ ಸಮೃದ್ಧ ನೀರು ಅಗತ್ಯ. ಸಾಮಾನ್ಯ ರೋಗಗಳು: ಬ್ಲಾಸ್ಟ್, ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಬ್ಲೈಟ್."
    
    elif any(word in lower_message for word in ['ರಾಗಿ', 'ragi', 'रागी', 'கேழ்வரகு', 'రాగి']):
        crop_info = agricultural_database["cropCalendar"].get("ರಾಗಿ", {})
        sowing = ", ".join(crop_info.get("sowing", []))
        harvesting = ", ".join(crop_info.get("harvesting", []))
        return f"ರಾಗಿ ಬೆಳೆಯ ಸಮಯ: {sowing} ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ, {harvesting} ನಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಬಹುದು. ರಾಗಿ ಶುಷ್ಕ ಪ್ರದೇಶಗಳಿಗೆ ಉತ್ತಮ. ಇದು ಕ್ಯಾಲ್ಷಿಯಂ ಮತ್ತು ಜೀವಸತ್ವಗಳಿಂದ ಸಮೃದ್ಧವಾಗಿದೆ."
    
    elif any(word in lower_message for word in ['ಕಬ್ಬು', 'sugarcane', 'गन्ना', 'கரும்பு', 'చెరకు']):
        crop_info = agricultural_database["cropCalendar"].get("ಕಬ್ಬು", {})
        sowing = ", ".join(crop_info.get("sowing", []))
        harvesting = ", ".join(crop_info.get("harvesting", []))
        return f"ಕಬ್ಬು ಬೆಳೆಯ ಸಮಯ: {sowing} ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ, {harvesting} ನಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಬಹುದು. ಕಬ್ಬು ಬೆಳೆಗೆ ಸಮೃದ್ಧ ನೀರು ಮತ್ತು ಗೊಬ್ಬರ ಅಗತ್ಯ."
    
    elif any(word in lower_message for word in ['ಹತ್ತಿ', 'cotton', 'कपास', 'பருத்தி', 'పత్తి']):
        crop_info = agricultural_database["cropCalendar"].get("ಹತ್ತಿ", {})
        sowing = ", ".join(crop_info.get("sowing", []))
        harvesting = ", ".join(crop_info.get("harvesting", []))
        return f"ಹತ್ತಿ ಬೆಳೆಯ ಸಮಯ: {sowing} ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ, {harvesting} ನಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಬಹುದು. ಹತ್ತಿ ಬೆಳೆಗೆ ಬೆಳಕು ಮತ್ತು ಉಷ್ಣಾಂಶ ಅಗತ್ಯ."
    
    elif any(word in lower_message for word in ['ಸಾವಯವ', 'organic', 'जैविक', 'கரிம', 'సేంద్రీయ']):
        return "ಸಾವಯವ ಕೃಷಿ ಪರಿಸರ ಸ್ನೇಹಿ ಮತ್ತು ಆರೋಗ್ಯಕರ. ಜೈವಿಕ ಗೊಬ್ಬರ, ಕೀಟನಾಶಕಗಳು ಬಳಸಿ. ಕಂಪೋಸ್ಟ್ ತಯಾರಿಸಿ, ಬೆಳೆ ತಿರುಗು ಪದ್ಧತಿ ಅನುಸರಿಸಿ."
    
    elif any(word in lower_message for word in ['ನೀರು ಉಳಿತಾಯ', 'water saving', 'पानी की बचत', 'நீர் சேமிப்பு', 'నీటి పొదుపు']):
        return "ನೀರು ಉಳಿತಾಯ ಮಾಡಲು: ಟಪ್ಪಾವರಿ ವಿಧಾನ ಬಳಸಿ, ಮಳೆ ನೀರು ಸಂಗ್ರಹಿಸಿ, ಬೆಳೆಗಳಿಗೆ ಅಗತ್ಯವಿರುವಾಗ ಮಾತ್ರ ನೀರು ಹಾಕಿ, ಮಣ್ಣಿನ ತೇವಾಂಶ ನಿಗಾ ಇಡಿ."
    
    else:
        return lang_responses["unknown"]

def analyze_image_simple(image_data):
    """Simple image analysis function - in production, you would use ML models"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Simple analysis based on color distribution
        # This is a very basic simulation - real implementation would use ML
        total_pixels = img_array.shape[0] * img_array.shape[1]
        
        # Calculate average color
        avg_color = np.mean(img_array, axis=(0, 1))
        
        # Simple health detection based on green color dominance
        green_ratio = avg_color[1] / (avg_color[0] + avg_color[1] + avg_color[2] + 0.001)
        
        if green_ratio > 0.4:
            health_status = "ಆರೋಗ್ಯವಂತ ಸಸ್ಯ"
            confidence = 0.85
            recommendations = [
                "ನೀರಾವರಿ ಮತ್ತು ಗೊಬ್ಬರದ ಕ್ರಮಗಳನ್ನು ಮುಂದುವರಿಸಿ",
                "ಸಸ್ಯವನ್ನು ನಿಗಾ ಮಾಡಿ",
                "ಯಾವುದೇ ಬದಲಾವಣೆಗಳಿಗೆ ಸೂಕ್ತ ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳಿ"
            ]
        elif green_ratio > 0.25:
            health_status = "ಮಧ್ಯಮ ಸ್ಥಿತಿಯ ಸಸ್ಯ"
            confidence = 0.65
            recommendations = [
                "ಹೆಚ್ಚಿನ ಗಮನ ಮತ್ತು ಕಾಳಜಿ ಅಗತ್ಯ",
                "ಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ಪರಿಶೀಲಿಸಿ",
                "ರೋಗದ ಚಿಹ್ನೆಗಳಿಗೆ ನಿಗಾ ಇಡಿ"
            ]
        else:
            health_status = "ದುರ್ಬಲ ಸಸ್ಯ"
            confidence = 0.75
            recommendations = [
                "ತಕ್ಷಣದ ಕಾಳಜಿ ಅಗತ್ಯ",
                "ಸೂಕ್ತ ಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ನೀಡಿ",
                "ರೋಗ ನಿಯಂತ್ರಣ ಅಗತ್ಯವಿದ್ದರೆ ಪರಿಶೀಲಿಸಿ"
            ]
        
        return {
            "analysis": f"ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ: {health_status}",
            "confidence": confidence,
            "recommendations": recommendations,
            "details": {
                "image_size": f"{img_array.shape[1]}x{img_array.shape[0]}",
                "color_analysis": f"ಹಸಿರು ಬಣ್ಣದ ಪ್ರಮಾಣ: {green_ratio:.2f}",
                "estimated_health": health_status
            }
        }
    
    except Exception as e:
        return {
            "analysis": "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ ವಿಫಲವಾಗಿದೆ",
            "confidence": 0.0,
            "recommendations": ["ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ"],
            "error": str(e)
        }

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'kn')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get AI response
        response = get_ai_response(message, language)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Analyze image
        analysis_result = analyze_image_simple(image_data)
        
        return jsonify({
            'analysis': analysis_result['analysis'],
            'confidence': analysis_result['confidence'],
            'recommendations': analysis_result['recommendations'],
            'details': analysis_result.get('details', {}),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'KrishiSiri AI Chatbot API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    print("Starting KrishiSiri AI Chatbot Backend...")
    print("API Endpoints:")
    print("  POST /api/chat - Process chat messages")
    print("  POST /api/analyze-image - Analyze plant images")
    print("  GET  /api/health - Health check")
    print("\nServer running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)