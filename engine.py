"""
Indian Telecom Forensics Engine
Provides telecom circle analysis, operator prefix identification, STD code resolution,
MCC-MNC identification, CDR processing, and forensic reporting under Indian standards.
"""

import re
import datetime
from typing import Dict, Any, List, Optional
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# 22 Telecom Circles / Licensed Service Areas (LSAs) in India
INDIAN_CIRCLES = {
    "DL": {"name": "Delhi", "category": "Metro", "region": "North", "hq": "New Delhi", "lat": 28.6139, "lon": 77.2090},
    "MUM": {"name": "Mumbai", "category": "Metro", "region": "West", "hq": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "KOL": {"name": "Kolkata", "category": "Metro", "region": "East", "hq": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    "MH": {"name": "Maharashtra & Goa", "category": "A", "region": "West", "hq": "Pune", "lat": 18.5204, "lon": 73.8567},
    "GJ": {"name": "Gujarat", "category": "A", "region": "West", "hq": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    "AP": {"name": "Andhra Pradesh & Telangana", "category": "A", "region": "South", "hq": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "KA": {"name": "Karnataka", "category": "A", "region": "South", "hq": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    "TN": {"name": "Tamil Nadu & Chennai", "category": "A", "region": "South", "hq": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "KL": {"name": "Kerala & Lakshadweep", "category": "B", "region": "South", "hq": "Kochi", "lat": 9.9312, "lon": 76.2673},
    "PB": {"name": "Punjab", "category": "B", "region": "North", "hq": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "HR": {"name": "Haryana", "category": "B", "region": "North", "hq": "Ambala", "lat": 30.3782, "lon": 76.7767},
    "UPE": {"name": "Uttar Pradesh (East)", "category": "B", "region": "North", "hq": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    "UPW": {"name": "Uttar Pradesh (West) & Uttarakhand", "category": "B", "region": "North", "hq": "Meerut", "lat": 28.9845, "lon": 77.7064},
    "RJ": {"name": "Rajasthan", "category": "B", "region": "North", "hq": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    "MP": {"name": "Madhya Pradesh & Chhattisgarh", "category": "B", "region": "Central", "hq": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    "WB": {"name": "West Bengal (excluding Kolkata)", "category": "B", "region": "East", "hq": "Kolkata", "lat": 23.5204, "lon": 87.3119},
    "AS": {"name": "Assam", "category": "C", "region": "North East", "hq": "Guwahati", "lat": 26.1445, "lon": 91.7362},
    "BR": {"name": "Bihar & Jharkhand", "category": "C", "region": "East", "hq": "Patna", "lat": 25.5941, "lon": 85.1376},
    "HP": {"name": "Himachal Pradesh", "category": "C", "region": "North", "hq": "Shimla", "lat": 31.1048, "lon": 77.1734},
    "JK": {"name": "Jammu & Kashmir & Ladakh", "category": "C", "region": "North", "hq": "Jammu / Srinagar", "lat": 32.7266, "lon": 74.8570},
    "NE": {"name": "North East", "category": "C", "region": "North East", "hq": "Shillong", "lat": 25.5788, "lon": 91.8933},
    "OR": {"name": "Odisha", "category": "C", "region": "East", "hq": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245},
}

# Major Indian STD codes for Landline identification
STD_CODES = {
    "11": "Delhi / NCR",
    "22": "Mumbai, Maharashtra",
    "33": "Kolkata, West Bengal",
    "44": "Chennai, Tamil Nadu",
    "80": "Bengaluru, Karnataka",
    "20": "Pune, Maharashtra",
    "40": "Hyderabad, Telangana",
    "79": "Ahmedabad, Gujarat",
    "141": "Jaipur, Rajasthan",
    "522": "Lucknow, Uttar Pradesh",
    "612": "Patna, Bihar",
    "172": "Chandigarh / Mohali / Panchkula",
    "755": "Bhopal, Madhya Pradesh",
    "731": "Indore, Madhya Pradesh",
    "265": "Vadodara, Gujarat",
    "261": "Surat, Gujarat",
    "891": "Visakhapatnam, Andhra Pradesh",
    "484": "Kochi, Kerala",
    "471": "Thiruvananthapuram, Kerala",
    "674": "Bhubaneswar, Odisha",
    "361": "Guwahati, Assam",
    "194": "Srinagar, Jammu & Kashmir",
    "191": "Jammu, Jammu & Kashmir",
    "177": "Shimla, Himachal Pradesh",
    "135": "Dehradun, Uttarakhand",
    "512": "Kanpur, Uttar Pradesh",
    "542": "Varanasi, Uttar Pradesh",
    "651": "Ranchi, Jharkhand",
    "771": "Raipur, Chhattisgarh",
    "832": "Panaji, Goa",
    "422": "Coimbatore, Tamil Nadu",
    "452": "Madurai, Tamil Nadu",
    "821": "Mysuru, Karnataka",
    "824": "Mangaluru, Karnataka",
    "161": "Ludhiana, Punjab",
    "181": "Jalandhar, Punjab",
    "183": "Amritsar, Punjab",
    "294": "Udaipur, Rajasthan",
    "291": "Jodhpur, Rajasthan",
    "124": "Gurugram, Haryana",
    "120": "Noida / Ghaziabad, Uttar Pradesh",
    "129": "Faridabad, Haryana",
}

# Indian Mobile Country Code (MCC) & Network Codes (MNC) reference
INDIAN_MNC_MAPPING = {
    "404-45": "Airtel (Airtel India)",
    "404-10": "Airtel (Delhi)",
    "404-31": "Airtel (Kolkata)",
    "404-70": "Airtel (Rajasthan)",
    "404-49": "Airtel (Maharashtra)",
    "404-92": "Airtel (Mumbai)",
    "405-854": "Reliance Jio (All India)",
    "405-855": "Reliance Jio (All India)",
    "405-856": "Reliance Jio (All India)",
    "405-857": "Reliance Jio (All India)",
    "405-858": "Reliance Jio (All India)",
    "405-859": "Reliance Jio (All India)",
    "405-860": "Reliance Jio (All India)",
    "405-861": "Reliance Jio (All India)",
    "404-20": "Vodafone Idea (Vi - Mumbai)",
    "404-11": "Vodafone Idea (Vi - Delhi)",
    "404-27": "Vodafone Idea (Vi - Maharashtra)",
    "404-46": "Vodafone Idea (Vi - Kerala)",
    "404-38": "BSNL Mobile (CellOne)",
    "404-51": "BSNL Mobile (Himachal)",
    "404-53": "BSNL Mobile (Punjab)",
    "404-55": "BSNL Mobile (UP East)",
    "404-56": "BSNL Mobile (UP West)",
    "404-71": "BSNL Mobile (Karnataka)",
    "404-72": "BSNL Mobile (Kerala)",
    "404-68": "MTNL Dolphin (Delhi)",
    "404-69": "MTNL Dolphin (Mumbai)"
}

# DoT Indian Mobile 4-digit prefix allocations to Telecom Circles (LSAs)
MOBILE_PREFIX_TO_CIRCLE = {
    # Delhi
    "9810": "DL", "9811": "DL", "9818": "DL", "9871": "DL", "9873": "DL", "9891": "DL", "9910": "DL", "9911": "DL", "9999": "DL", "9711": "DL", "9716": "DL", "9717": "DL", "9718": "DL", "9310": "DL", "9311": "DL", "9312": "DL", "9313": "DL", "9315": "DL", "9350": "DL", "9210": "DL", "9211": "DL", "9212": "DL", "9213": "DL", "9250": "DL", "8800": "DL", "8802": "DL", "8826": "DL", "8860": "DL", "8447": "DL", "8527": "DL", "8588": "DL", "8595": "DL", "8744": "DL", "8750": "DL", "7042": "DL", "7290": "DL", "7503": "DL", "7838": "DL",
    # Mumbai
    "9820": "MUM", "9821": "MUM", "9819": "MUM", "9867": "MUM", "9869": "MUM", "9892": "MUM", "9920": "MUM", "9930": "MUM", "9969": "MUM", "9987": "MUM", "9702": "MUM", "9769": "MUM", "9320": "MUM", "9321": "MUM", "9322": "MUM", "9323": "MUM", "9324": "MUM", "9220": "MUM", "9221": "MUM", "9222": "MUM", "9223": "MUM", "8879": "MUM", "8898": "MUM", "8451": "MUM", "8452": "MUM", "8454": "MUM", "8652": "MUM", "8655": "MUM", "7506": "MUM", "7710": "MUM", "7715": "MUM", "7718": "MUM", "7738": "MUM", "7021": "MUM", "7045": "MUM",
    # Kolkata
    "9830": "KOL", "9831": "KOL", "9836": "KOL", "9874": "KOL", "9883": "KOL", "9903": "KOL", "9748": "KOL", "9330": "KOL", "9331": "KOL", "9339": "KOL", "9230": "KOL", "9231": "KOL", "8981": "KOL", "8961": "KOL", "8420": "KOL", "8334": "KOL", "8335": "KOL", "7044": "KOL", "7278": "KOL", "7595": "KOL", "7596": "KOL",
    # Tamil Nadu / Chennai
    "9840": "TN", "9841": "TN", "9884": "TN", "9940": "TN", "9941": "TN", "9952": "TN", "9710": "TN", "9789": "TN", "9790": "TN", "9791": "TN", "9380": "TN", "9381": "TN", "9382": "TN", "9282": "TN", "9283": "TN", "8939": "TN", "8144": "TN", "8148": "TN", "8667": "TN", "7200": "TN", "7299": "TN", "7358": "TN", "7397": "TN",
    # Karnataka
    "9844": "KA", "9845": "KA", "9880": "KA", "9886": "KA", "9900": "KA", "9901": "KA", "9902": "KA", "9916": "KA", "9945": "KA", "9972": "KA", "9980": "KA", "9986": "KA", "9731": "KA", "9739": "KA", "9740": "KA", "9741": "KA", "9742": "KA", "9743": "KA", "9341": "KA", "9342": "KA", "9343": "KA", "9241": "KA", "9242": "KA", "9243": "KA", "8861": "KA", "8867": "KA", "8880": "KA", "8884": "KA", "8722": "KA", "8746": "KA", "8747": "KA", "8748": "KA", "8749": "KA", "8105": "KA", "8123": "KA", "8147": "KA", "8197": "KA", "7022": "KA", "7026": "KA", "7204": "KA", "7259": "KA", "7337": "KA", "7338": "KA", "7348": "KA", "7349": "KA", "7353": "KA", "7406": "KA", "7411": "KA",
    # Andhra Pradesh & Telangana
    "9848": "AP", "9849": "AP", "9866": "AP", "9885": "AP", "9908": "AP", "9912": "AP", "9948": "AP", "9949": "AP", "9951": "AP", "9959": "AP", "9963": "AP", "9966": "AP", "9985": "AP", "9989": "AP", "9700": "AP", "9701": "AP", "9703": "AP", "9704": "AP", "9705": "AP", "9346": "AP", "9347": "AP", "9348": "AP", "9390": "AP", "9391": "AP", "9392": "AP", "9393": "AP", "9246": "AP", "9247": "AP", "9248": "AP", "8885": "AP", "8886": "AP", "8897": "AP", "8978": "AP", "8985": "AP", "8106": "AP", "8121": "AP", "8125": "AP", "8142": "AP", "8143": "AP", "8179": "AP", "8184": "AP", "8185": "AP", "8186": "AP", "8187": "AP", "7032": "AP", "7036": "AP", "7093": "AP", "7095": "AP", "7207": "AP", "7285": "AP", "7306": "AP", "7330": "AP", "7382": "AP", "7386": "AP", "7396": "AP",
    # Maharashtra & Goa
    "9822": "MH", "9823": "MH", "9850": "MH", "9860": "MH", "9881": "MH", "9890": "MH", "9921": "MH", "9922": "MH", "9923": "MH", "9960": "MH", "9970": "MH", "9975": "MH", "9730": "MH", "9762": "MH", "9763": "MH", "9764": "MH", "9765": "MH", "9766": "MH", "9767": "MH", "9325": "MH", "9326": "MH", "9370": "MH", "9371": "MH", "9372": "MH", "9373": "MH", "9225": "MH", "9226": "MH", "9270": "MH", "9271": "MH", "9272": "MH", "9273": "MH", "8805": "MH", "8806": "MH", "8888": "MH", "8975": "MH", "8983": "MH", "8999": "MH", "8308": "MH", "8380": "MH", "8390": "MH", "8408": "MH", "8411": "MH", "8412": "MH", "8421": "MH", "8446": "MH", "8482": "MH", "8483": "MH", "8484": "MH", "8485": "MH", "7020": "MH", "7028": "MH", "7030": "MH", "7038": "MH", "7057": "MH", "7058": "MH", "7066": "MH", "7083": "MH", "7218": "MH", "7219": "MH", "7248": "MH", "7249": "MH", "7276": "MH", "7350": "MH", "7378": "MH", "7385": "MH", "7387": "MH", "7410": "MH", "7420": "MH", "7447": "MH", "7448": "MH", "7498": "MH", "7499": "MH",
    # Gujarat
    "9824": "GJ", "9825": "GJ", "9879": "GJ", "9898": "GJ", "9904": "GJ", "9909": "GJ", "9913": "GJ", "9924": "GJ", "9925": "GJ", "9974": "GJ", "9978": "GJ", "9979": "GJ", "9998": "GJ", "9712": "GJ", "9714": "GJ", "9723": "GJ", "9724": "GJ", "9725": "GJ", "9726": "GJ", "9727": "GJ", "9327": "GJ", "9328": "GJ", "9374": "GJ", "9375": "GJ", "9376": "GJ", "9377": "GJ", "9227": "GJ", "9228": "GJ", "8866": "GJ", "8980": "GJ", "8128": "GJ", "8140": "GJ", "8141": "GJ", "8153": "GJ", "8154": "GJ", "8155": "GJ", "8156": "GJ", "8160": "GJ", "8200": "GJ", "8238": "GJ", "8320": "GJ", "8347": "GJ", "8401": "GJ", "8460": "GJ", "8469": "GJ", "8487": "GJ", "8488": "GJ", "8511": "GJ", "8530": "GJ", "8732": "GJ", "8733": "GJ", "8734": "GJ", "8735": "GJ", "8758": "GJ", "8780": "GJ", "7016": "GJ", "7041": "GJ", "7043": "GJ", "7046": "GJ", "7069": "GJ", "7096": "GJ", "7201": "GJ", "7202": "GJ", "7203": "GJ", "7226": "GJ", "7227": "GJ", "7228": "GJ", "7229": "GJ", "7283": "GJ", "7284": "GJ", "7359": "GJ", "7383": "GJ", "7405": "GJ", "7433": "GJ", "7434": "GJ", "7435": "GJ", "7436": "GJ",
    # Kerala
    "9846": "KL", "9847": "KL", "9895": "KL", "9946": "KL", "9947": "KL", "9961": "KL", "9995": "KL", "9744": "KL", "9745": "KL", "9746": "KL", "9747": "KL", "9349": "KL", "9387": "KL", "9388": "KL", "9249": "KL", "8891": "KL", "8893": "KL", "8943": "KL", "8111": "KL", "8113": "KL", "8129": "KL", "8136": "KL", "8137": "KL", "8138": "KL", "8139": "KL", "8281": "KL", "8289": "KL", "8547": "KL", "8589": "KL", "8590": "KL", "8592": "KL", "8593": "KL", "8594": "KL", "7012": "KL", "7025": "KL", "7034": "KL", "7510": "KL", "7558": "KL", "7559": "KL", "7560": "KL", "7561": "KL", "7591": "KL", "7592": "KL", "7593": "KL", "7594": "KL", "7902": "KL", "7907": "KL", "7994": "KL",
    # Punjab
    "9814": "PB", "9815": "PB", "9855": "PB", "9872": "PB", "9876": "PB", "9878": "PB", "9888": "PB", "9914": "PB", "9915": "PB", "9988": "PB", "9779": "PB", "9780": "PB", "9781": "PB", "9316": "PB", "9317": "PB", "9356": "PB", "9357": "PB", "9216": "PB", "9217": "PB", "8872": "PB", "8968": "PB", "8146": "PB", "8194": "PB", "8195": "PB", "8196": "PB", "8198": "PB", "8283": "PB", "8284": "PB", "8288": "PB", "8427": "PB", "8437": "PB", "8556": "PB", "8557": "PB", "8558": "PB", "8559": "PB", "8566": "PB", "8567": "PB", "8568": "PB", "8569": "PB", "8725": "PB", "8727": "PB", "8728": "PB", "8729": "PB", "7009": "PB", "7087": "PB", "7340": "PB", "7341": "PB", "7347": "PB", "7355": "PB", "7508": "PB", "7526": "PB", "7527": "PB", "7528": "PB", "7529": "PB", "7589": "PB", "7696": "PB", "7814": "PB", "7837": "PB", "7888": "PB", "7889": "PB",
    # Haryana
    "9812": "HR", "9813": "HR", "9896": "HR", "9991": "HR", "9992": "HR", "9996": "HR", "9728": "HR", "9729": "HR", "9354": "HR", "9355": "HR", "9215": "HR", "9253": "HR", "9254": "HR", "9255": "HR", "8813": "HR", "8814": "HR", "8816": "HR", "8818": "HR", "8901": "HR", "8930": "HR", "8950": "HR", "8199": "HR", "8221": "HR", "8222": "HR", "8295": "HR", "8570": "HR", "8571": "HR", "8572": "HR", "8607": "HR", "8683": "HR", "8684": "HR", "8685": "HR", "8689": "HR", "8708": "HR", "7015": "HR", "7027": "HR", "7056": "HR", "7082": "HR", "7206": "HR", "7404": "HR", "7419": "HR", "7494": "HR", "7495": "HR", "7496": "HR", "7497": "HR"
}

# Indian Emergency & Special Service Numbers
SPECIAL_NUMBERS = {
    "112": "National Unified Emergency Response (ERSS)",
    "100": "Police Control Room",
    "101": "Fire Service",
    "102": "Ambulance (State Emergency)",
    "108": "Disaster & Emergency Medical Response",
    "1090": "Women Power Line (Anti-Harassment)",
    "1091": "Women Helpline (General)",
    "1098": "Childline India",
    "1930": "National Cyber Crime Helpline (Citizen Financial Cyber Fraud Reporting)",
    "14449": "National Consumer Helpline",
    "1070": "National Disaster Management Authority (NDMA)",
    "1073": "Road Accident Emergency Service",
    "139": "Indian Railways Unified Customer Helpline"
}


def clean_phone_input(raw: str) -> str:
    """Removes spaces, hyphens, parentheses, and noise from number strings."""
    if not raw:
        return ""
    cleaned = re.sub(r"[\s\-\(\)\.]", "", str(raw).strip())
    # Strip leading zeroes if length is 11 (e.g. 09876543210 -> 9876543210)
    if cleaned.startswith("0") and len(cleaned) == 11 and cleaned[1] in "6789":
        cleaned = cleaned[1:]
    return cleaned


def resolve_std_code(clean_num: str) -> Optional[Dict[str, str]]:
    """Checks if a number begins with an Indian STD landline code."""
    num = clean_num
    if num.startswith("+91"):
        num = num[3:]
    elif num.startswith("91") and len(num) > 10:
        num = num[2:]
    if num.startswith("0"):
        num = num[1:]

    # Check 4-digit, 3-digit, 2-digit STD prefixes
    for length in [4, 3, 2]:
        prefix = num[:length]
        if prefix in STD_CODES:
            return {
                "std_code": prefix,
                "location": STD_CODES[prefix]
            }
    return None


def match_circle_metadata(description: str) -> Dict[str, Any]:
    """Matches a geographic description to official Indian Telecom Circle metadata."""
    desc_lower = description.lower()
    
    for code, info in INDIAN_CIRCLES.items():
        if code.lower() in desc_lower or info["name"].lower() in desc_lower or info["hq"].lower() in desc_lower:
            return {
                "circle_code": code,
                "circle_name": info["name"],
                "circle_category": info["category"],
                "circle_region": info["region"],
                "circle_hq": info["hq"],
                "lat": info.get("lat"),
                "lon": info.get("lon")
            }
            
    # Fuzzy keyword heuristics for Indian states/cities
    keyword_map = {
        "delhi": "DL",
        "mumbai": "MUM",
        "kolkata": "KOL",
        "maharashtra": "MH",
        "goa": "MH",
        "pune": "MH",
        "gujarat": "GJ",
        "ahmedabad": "GJ",
        "andhra": "AP",
        "telangana": "AP",
        "hyderabad": "AP",
        "karnataka": "KA",
        "bangalore": "KA",
        "bengaluru": "KA",
        "tamil": "TN",
        "chennai": "TN",
        "kerala": "KL",
        "punjab": "PB",
        "chandigarh": "PB",
        "haryana": "HR",
        "rajasthan": "RJ",
        "jaipur": "RJ",
        "bhopal": "MP",
        "madhya": "MP",
        "chhattisgarh": "MP",
        "bihar": "BR",
        "jharkhand": "BR",
        "patna": "BR",
        "assam": "AS",
        "odisha": "OR",
        "orissa": "OR",
        "bhubaneswar": "OR",
        "himachal": "HP",
        "shimla": "HP",
        "jammu": "JK",
        "kashmir": "JK"
    }
    
    for kw, code in keyword_map.items():
        if kw in desc_lower:
            info = INDIAN_CIRCLES[code]
            return {
                "circle_code": code,
                "circle_name": info["name"],
                "circle_category": info["category"],
                "circle_region": info["region"],
                "circle_hq": info["hq"],
                "lat": info.get("lat"),
                "lon": info.get("lon")
            }
            
    return {
        "circle_code": "UNKNOWN",
        "circle_name": description or "Pan-India / Unassigned",
        "circle_category": "N/A",
        "circle_region": "India",
        "circle_hq": "N/A",
        "lat": 20.5937,
        "lon": 78.9629
    }


def analyze_single_number(raw_input: str) -> Dict[str, Any]:
    """
    Forensic analysis for an individual Indian telephone/mobile number.
    Extracts metadata, circle, operator series, line type, and legal notes.
    """
    cleaned = clean_phone_input(raw_input)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    
    result = {
        "query_input": raw_input,
        "cleaned_input": cleaned,
        "timestamp": timestamp,
        "is_valid": False,
        "is_possible": False,
        "is_special_service": False,
        "special_service_desc": None,
        "e164": None,
        "national": None,
        "international": None,
        "country_code": 91,
        "national_number": None,
        "line_type": "Unknown",
        "original_circle": "Unknown",
        "circle_details": {},
        "original_carrier": "Unknown",
        "carrier_risk_note": "MNP (Mobile Number Portability) allows users to switch carriers. Original carrier indicates initial prefix allocation only.",
        "std_code_info": None,
        "timezones": ["Asia/Kolkata"],
        "investigative_guidance": []
    }
    
    # Check if this is an Indian Emergency / Special shortcode
    if cleaned in SPECIAL_NUMBERS:
        result["is_valid"] = True
        result["is_special_service"] = True
        result["special_service_desc"] = SPECIAL_NUMBERS[cleaned]
        result["line_type"] = "Government / Emergency Shortcode"
        result["original_circle"] = "Pan-India National Service"
        result["investigative_guidance"].append("Direct institutional line. Calls routed to nearest State/District Public Safety Answering Point (PSAP).")
        return result

    try:
        # Default region to India ('IN')
        parsed = phonenumbers.parse(cleaned, "IN")
    except phonenumbers.NumberParseException as err:
        result["error"] = str(err)
        result["investigative_guidance"].append("Parsing failed. Check for irregular characters or missing digits.")
        return result

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)
    
    result["is_valid"] = is_valid
    result["is_possible"] = is_possible
    result["country_code"] = parsed.country_code
    result["national_number"] = str(parsed.national_number)

    if not is_valid:
        result["investigative_guidance"].append("Number does not comply with DoT National Numbering Plan allocation. May be spoofed or fictitious.")
        return result

    # Formatted representations
    result["e164"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    result["national"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    result["international"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    # Line Type Classification
    num_type = phonenumbers.number_type(parsed)
    type_labels = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile Cellular",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line (PSTN/Landline)",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line / Mobile Hybrid",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free (1800 Series)",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate Services",
        phonenumbers.PhoneNumberType.VOIP: "VoIP (Voice over IP)",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "Universal Access Number (UAN)",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail Access",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unclassified"
    }
    result["line_type"] = type_labels.get(num_type, "Unknown")

    # Geolocation / Telecom Circle
    geo_desc = geocoder.description_for_number(parsed, "en")
    nat_str = str(parsed.national_number)
    
    # If generic "India" or empty, resolve using 4-digit mobile prefix
    resolved_circle = geo_desc
    if (not geo_desc or geo_desc == "India") and len(nat_str) == 10:
        pref4 = nat_str[:4]
        if pref4 in MOBILE_PREFIX_TO_CIRCLE:
            code = MOBILE_PREFIX_TO_CIRCLE[pref4]
            if code in INDIAN_CIRCLES:
                resolved_circle = INDIAN_CIRCLES[code]["name"]
                
    result["original_circle"] = resolved_circle or "India"
    result["circle_details"] = match_circle_metadata(result["original_circle"])

    # Carrier / Operator Series
    carrier_name = carrier.name_for_number(parsed, "en")
    result["original_carrier"] = carrier_name if carrier_name else "Unspecified / Shared Series"

    # STD Code check for Landlines
    if result["line_type"] in ["Fixed Line (PSTN/Landline)", "Fixed Line / Mobile Hybrid"]:
        std_info = resolve_std_code(cleaned)
        if std_info:
            result["std_code_info"] = std_info

    # Timezones
    tz_list = list(timezone.time_zones_for_number(parsed))
    result["timezones"] = tz_list if tz_list else ["Asia/Kolkata"]

    # Forensic & Investigative Guidance Notes
    nat_str = str(parsed.national_number)
    
    # Check leading digit for Indian mobile
    if len(nat_str) == 10:
        first_digit = nat_str[0]
        if first_digit in "6789":
            result["investigative_guidance"].append(
                f"Valid 10-digit mobile series beginning with '{first_digit}'. Allocated under DoT National Numbering Plan."
            )
        else:
            result["investigative_guidance"].append(
                f"Notice: Mobile numbers in India typically begin with 6, 7, 8, or 9. Beginning with '{first_digit}' may indicate landline, UAN, or virtual number."
            )

    result["investigative_guidance"].append(
        "To obtain subscriber name (SDR/CAF) or cell tower locations (CDR), an authorized notice under Section 91 CrPC (or Section 94 BNSS) must be served to the Nodal Officer of the active telecom service provider."
    )
    result["investigative_guidance"].append(
        "To verify if this handset is reported stolen/lost in India, query the Central Equipment Identity Register (CEIR) database via ceir.gov.in."
    )

    return result


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes the great-circle distance between two points in kilometers."""
    import math
    r = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 3)


def parse_timestamp_safe(ts_str: str) -> Optional[datetime.datetime]:
    """Tries multiple common datetime formats in Indian CDR logs."""
    if not ts_str:
        return None
    cleaned = str(ts_str).strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M"
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_cdr_records(records: List[Dict[str, Any]], geofence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Forensically analyzes Call Detail Records (CDRs).
    Calculates velocity between consecutive tower points, detects anomalies (impossible travel),
    checks geofence boundaries, and aggregates frequent callers/towers.
    """
    total_calls = len(records)
    callers = {}
    callees = {}
    towers = {}
    call_types = {"INCOMING": 0, "OUTGOING": 0, "SMS": 0, "DATA": 0, "OTHER": 0}
    total_duration_sec = 0

    processed_rows = []
    anomalies = []
    geofence_breaches = []

    prev_point = None  # (lat, lon, datetime)

    for idx, row in enumerate(records, start=1):
        caller = clean_phone_input(str(row.get("caller", "")))
        callee = clean_phone_input(str(row.get("callee", "")))
        ctype = str(row.get("call_type", "OTHER")).upper()
        ts_str = str(row.get("timestamp", ""))
        ts_dt = parse_timestamp_safe(ts_str)

        duration = 0
        try:
            duration = int(row.get("duration", 0))
        except (ValueError, TypeError):
            duration = 0
            
        total_duration_sec += duration
        
        # Categorize call type
        matched_type = "OTHER"
        for k in call_types:
            if k in ctype:
                matched_type = k
                break
        call_types[matched_type] += 1

        # Track frequency
        if caller:
            callers[caller] = callers.get(caller, 0) + 1
        if callee:
            callees[callee] = callees.get(callee, 0) + 1

        # Track Cell Sites / Towers
        cell_id = str(row.get("cell_id", "") or row.get("cgi", "")).strip()
        lac = str(row.get("lac", "")).strip()
        tower_key = f"LAC:{lac}-Cell:{cell_id}" if lac else cell_id
        if tower_key and tower_key != "LAC:-Cell:":
            towers[tower_key] = towers.get(tower_key, 0) + 1

        # Coordinates parsing
        lat = None
        lon = None
        try:
            if "lat" in row and "lon" in row:
                lat = float(row["lat"])
                lon = float(row["lon"])
        except (ValueError, TypeError):
            lat = None
            lon = None

        # Speed / Velocity Analysis between consecutive tower points
        speed_kmh = None
        distance_km = None
        velocity_status = "STATIONARY"

        if lat is not None and lon is not None and ts_dt is not None:
            if prev_point and prev_point["dt"]:
                dist = haversine_distance(prev_point["lat"], prev_point["lon"], lat, lon)
                time_diff = (ts_dt - prev_point["dt"]).total_seconds()
                distance_km = dist
                
                if time_diff > 0:
                    speed = (dist / (time_diff / 3600.0))
                    speed_kmh = round(speed, 1)

                    if speed_kmh > 250:
                        velocity_status = "IMPOSSIBLE_VELOCITY"
                        anomalies.append({
                            "type": "IMPOSSIBLE_VELOCITY",
                            "severity": "CRITICAL",
                            "record_id": idx,
                            "timestamp": ts_str,
                            "speed_kmh": speed_kmh,
                            "distance_km": dist,
                            "time_sec": round(time_diff),
                            "description": f"Device jumped {dist} km in {round(time_diff)}s ({speed_kmh} km/h). Probable SIM cloning or virtual cell tower injection."
                        })
                    elif speed_kmh > 120:
                        velocity_status = "HIGH_SPEED_TRANSIT"
                    elif speed_kmh > 5:
                        velocity_status = "URBAN_TRANSIT"
                    else:
                        velocity_status = "WALKING / LOCAL"
            prev_point = {"lat": lat, "lon": lon, "dt": ts_dt}

        # Geofence breach check
        inside_geofence = None
        if geofence and lat is not None and lon is not None:
            g_lat = float(geofence.get("lat", 0))
            g_lon = float(geofence.get("lon", 0))
            g_radius = float(geofence.get("radius_km", 5))
            dist_from_center = haversine_distance(g_lat, g_lon, lat, lon)
            inside_geofence = dist_from_center <= g_radius
            if inside_geofence:
                geofence_breaches.append({
                    "record_id": idx,
                    "timestamp": ts_str,
                    "lat": lat,
                    "lon": lon,
                    "dist_from_center_km": dist_from_center,
                    "tower_identifier": tower_key
                })

        # Late-night suspicious activity flag (11 PM - 5 AM)
        if ts_dt and (ts_dt.hour >= 23 or ts_dt.hour < 5):
            anomalies.append({
                "type": "LATE_NIGHT_ACTIVITY",
                "severity": "MEDIUM",
                "record_id": idx,
                "timestamp": ts_str,
                "description": f"Activity recorded during high-suspicion window ({ts_dt.strftime('%H:%M:%S')})."
            })

        processed_rows.append({
            "record_id": idx,
            "timestamp": ts_str,
            "caller": caller,
            "callee": callee,
            "call_type": matched_type,
            "duration_sec": duration,
            "tower_identifier": tower_key,
            "lat": lat,
            "lon": lon,
            "distance_km": distance_km,
            "speed_kmh": speed_kmh,
            "velocity_status": velocity_status,
            "inside_geofence": inside_geofence
        })

    # Sort top entities
    top_callers = sorted(callers.items(), key=lambda x: x[1], reverse=True)[:10]
    top_callees = sorted(callees.items(), key=lambda x: x[1], reverse=True)[:10]
    top_towers = sorted(towers.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_records": total_calls,
        "total_duration_seconds": total_duration_sec,
        "total_duration_minutes": round(total_duration_sec / 60, 2),
        "call_type_breakdown": call_types,
        "top_callers": top_callers,
        "top_callees": top_callees,
        "top_towers": top_towers,
        "anomalies": anomalies,
        "geofence_breaches": geofence_breaches,
        "records": processed_rows
    }
