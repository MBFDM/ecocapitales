import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import uuid
import json
from datetime import datetime, timedelta
import time
import os
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
from fpdf import FPDF
from num2words import num2words
import qrcode
from io import BytesIO
from PIL import Image
import random
import re

# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Eco Capital - Espace Client",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LISTE DES PAYS AVEC INDICATIFS ET DRAPEAUX
# ============================================================
PAYS_INDICATIFS = [
    {"pays": "Afghanistan", "indicatif": "+93", "drapeau": "🇦🇫", "code": "AF"},
    {"pays": "Afrique du Sud", "indicatif": "+27", "drapeau": "🇿🇦", "code": "ZA"},
    {"pays": "Albanie", "indicatif": "+355", "drapeau": "🇦🇱", "code": "AL"},
    {"pays": "Algérie", "indicatif": "+213", "drapeau": "🇩🇿", "code": "DZ"},
    {"pays": "Allemagne", "indicatif": "+49", "drapeau": "🇩🇪", "code": "DE"},
    {"pays": "Andorre", "indicatif": "+376", "drapeau": "🇦🇩", "code": "AD"},
    {"pays": "Angola", "indicatif": "+244", "drapeau": "🇦🇴", "code": "AO"},
    {"pays": "Antigua-et-Barbuda", "indicatif": "+1268", "drapeau": "🇦🇬", "code": "AG"},
    {"pays": "Arabie saoudite", "indicatif": "+966", "drapeau": "🇸🇦", "code": "SA"},
    {"pays": "Argentine", "indicatif": "+54", "drapeau": "🇦🇷", "code": "AR"},
    {"pays": "Arménie", "indicatif": "+374", "drapeau": "🇦🇲", "code": "AM"},
    {"pays": "Australie", "indicatif": "+61", "drapeau": "🇦🇺", "code": "AU"},
    {"pays": "Autriche", "indicatif": "+43", "drapeau": "🇦🇹", "code": "AT"},
    {"pays": "Azerbaïdjan", "indicatif": "+994", "drapeau": "🇦🇿", "code": "AZ"},
    {"pays": "Bahamas", "indicatif": "+1242", "drapeau": "🇧🇸", "code": "BS"},
    {"pays": "Bahreïn", "indicatif": "+973", "drapeau": "🇧🇭", "code": "BH"},
    {"pays": "Bangladesh", "indicatif": "+880", "drapeau": "🇧🇩", "code": "BD"},
    {"pays": "Barbade", "indicatif": "+1246", "drapeau": "🇧🇧", "code": "BB"},
    {"pays": "Belgique", "indicatif": "+32", "drapeau": "🇧🇪", "code": "BE"},
    {"pays": "Belize", "indicatif": "+501", "drapeau": "🇧🇿", "code": "BZ"},
    {"pays": "Bénin", "indicatif": "+229", "drapeau": "🇧🇯", "code": "BJ"},
    {"pays": "Bhoutan", "indicatif": "+975", "drapeau": "🇧🇹", "code": "BT"},
    {"pays": "Biélorussie", "indicatif": "+375", "drapeau": "🇧🇾", "code": "BY"},
    {"pays": "Birmanie", "indicatif": "+95", "drapeau": "🇲🇲", "code": "MM"},
    {"pays": "Bolivie", "indicatif": "+591", "drapeau": "🇧🇴", "code": "BO"},
    {"pays": "Bosnie-Herzégovine", "indicatif": "+387", "drapeau": "🇧🇦", "code": "BA"},
    {"pays": "Botswana", "indicatif": "+267", "drapeau": "🇧🇼", "code": "BW"},
    {"pays": "Brésil", "indicatif": "+55", "drapeau": "🇧🇷", "code": "BR"},
    {"pays": "Brunei", "indicatif": "+673", "drapeau": "🇧🇳", "code": "BN"},
    {"pays": "Bulgarie", "indicatif": "+359", "drapeau": "🇧🇬", "code": "BG"},
    {"pays": "Burkina Faso", "indicatif": "+226", "drapeau": "🇧🇫", "code": "BF"},
    {"pays": "Burundi", "indicatif": "+257", "drapeau": "🇧🇮", "code": "BI"},
    {"pays": "Cambodge", "indicatif": "+855", "drapeau": "🇰🇭", "code": "KH"},
    {"pays": "Cameroun", "indicatif": "+237", "drapeau": "🇨🇲", "code": "CM"},
    {"pays": "Canada", "indicatif": "+1", "drapeau": "🇨🇦", "code": "CA"},
    {"pays": "Cap-Vert", "indicatif": "+238", "drapeau": "🇨🇻", "code": "CV"},
    {"pays": "Centrafrique", "indicatif": "+236", "drapeau": "🇨🇫", "code": "CF"},
    {"pays": "Chili", "indicatif": "+56", "drapeau": "🇨🇱", "code": "CL"},
    {"pays": "Chine", "indicatif": "+86", "drapeau": "🇨🇳", "code": "CN"},
    {"pays": "Chypre", "indicatif": "+357", "drapeau": "🇨🇾", "code": "CY"},
    {"pays": "Colombie", "indicatif": "+57", "drapeau": "🇨🇴", "code": "CO"},
    {"pays": "Comores", "indicatif": "+269", "drapeau": "🇰🇲", "code": "KM"},
    {"pays": "Congo (Brazzaville)", "indicatif": "+242", "drapeau": "🇨🇬", "code": "CG"},
    {"pays": "Congo (Kinshasa)", "indicatif": "+243", "drapeau": "🇨🇩", "code": "CD"},
    {"pays": "Corée du Nord", "indicatif": "+850", "drapeau": "🇰🇵", "code": "KP"},
    {"pays": "Corée du Sud", "indicatif": "+82", "drapeau": "🇰🇷", "code": "KR"},
    {"pays": "Costa Rica", "indicatif": "+506", "drapeau": "🇨🇷", "code": "CR"},
    {"pays": "Côte d'Ivoire", "indicatif": "+225", "drapeau": "🇨🇮", "code": "CI"},
    {"pays": "Croatie", "indicatif": "+385", "drapeau": "🇭🇷", "code": "HR"},
    {"pays": "Cuba", "indicatif": "+53", "drapeau": "🇨🇺", "code": "CU"},
    {"pays": "Danemark", "indicatif": "+45", "drapeau": "🇩🇰", "code": "DK"},
    {"pays": "Djibouti", "indicatif": "+253", "drapeau": "🇩🇯", "code": "DJ"},
    {"pays": "Égypte", "indicatif": "+20", "drapeau": "🇪🇬", "code": "EG"},
    {"pays": "Émirats arabes unis", "indicatif": "+971", "drapeau": "🇦🇪", "code": "AE"},
    {"pays": "Équateur", "indicatif": "+593", "drapeau": "🇪🇨", "code": "EC"},
    {"pays": "Érythrée", "indicatif": "+291", "drapeau": "🇪🇷", "code": "ER"},
    {"pays": "Espagne", "indicatif": "+34", "drapeau": "🇪🇸", "code": "ES"},
    {"pays": "Estonie", "indicatif": "+372", "drapeau": "🇪🇪", "code": "EE"},
    {"pays": "Eswatini", "indicatif": "+268", "drapeau": "🇸🇿", "code": "SZ"},
    {"pays": "États-Unis", "indicatif": "+1", "drapeau": "🇺🇸", "code": "US"},
    {"pays": "Éthiopie", "indicatif": "+251", "drapeau": "🇪🇹", "code": "ET"},
    {"pays": "Fidji", "indicatif": "+679", "drapeau": "🇫🇯", "code": "FJ"},
    {"pays": "Finlande", "indicatif": "+358", "drapeau": "🇫🇮", "code": "FI"},
    {"pays": "France", "indicatif": "+33", "drapeau": "🇫🇷", "code": "FR"},
    {"pays": "Gabon", "indicatif": "+241", "drapeau": "🇬🇦", "code": "GA"},
    {"pays": "Gambie", "indicatif": "+220", "drapeau": "🇬🇲", "code": "GM"},
    {"pays": "Géorgie", "indicatif": "+995", "drapeau": "🇬🇪", "code": "GE"},
    {"pays": "Ghana", "indicatif": "+233", "drapeau": "🇬🇭", "code": "GH"},
    {"pays": "Grèce", "indicatif": "+30", "drapeau": "🇬🇷", "code": "GR"},
    {"pays": "Guatemala", "indicatif": "+502", "drapeau": "🇬🇹", "code": "GT"},
    {"pays": "Guinée", "indicatif": "+224", "drapeau": "🇬🇳", "code": "GN"},
    {"pays": "Guinée équatoriale", "indicatif": "+240", "drapeau": "🇬🇶", "code": "GQ"},
    {"pays": "Guinée-Bissau", "indicatif": "+245", "drapeau": "🇬🇼", "code": "GW"},
    {"pays": "Guyana", "indicatif": "+592", "drapeau": "🇬🇾", "code": "GY"},
    {"pays": "Haïti", "indicatif": "+509", "drapeau": "🇭🇹", "code": "HT"},
    {"pays": "Honduras", "indicatif": "+504", "drapeau": "🇭🇳", "code": "HN"},
    {"pays": "Hongrie", "indicatif": "+36", "drapeau": "🇭🇺", "code": "HU"},
    {"pays": "Îles Salomon", "indicatif": "+677", "drapeau": "🇸🇧", "code": "SB"},
    {"pays": "Inde", "indicatif": "+91", "drapeau": "🇮🇳", "code": "IN"},
    {"pays": "Indonésie", "indicatif": "+62", "drapeau": "🇮🇩", "code": "ID"},
    {"pays": "Iran", "indicatif": "+98", "drapeau": "🇮🇷", "code": "IR"},
    {"pays": "Irak", "indicatif": "+964", "drapeau": "🇮🇶", "code": "IQ"},
    {"pays": "Irlande", "indicatif": "+353", "drapeau": "🇮🇪", "code": "IE"},
    {"pays": "Islande", "indicatif": "+354", "drapeau": "🇮🇸", "code": "IS"},
    {"pays": "Israël", "indicatif": "+972", "drapeau": "🇮🇱", "code": "IL"},
    {"pays": "Italie", "indicatif": "+39", "drapeau": "🇮🇹", "code": "IT"},
    {"pays": "Jamaïque", "indicatif": "+1876", "drapeau": "🇯🇲", "code": "JM"},
    {"pays": "Japon", "indicatif": "+81", "drapeau": "🇯🇵", "code": "JP"},
    {"pays": "Jordanie", "indicatif": "+962", "drapeau": "🇯🇴", "code": "JO"},
    {"pays": "Kazakhstan", "indicatif": "+7", "drapeau": "🇰🇿", "code": "KZ"},
    {"pays": "Kenya", "indicatif": "+254", "drapeau": "🇰🇪", "code": "KE"},
    {"pays": "Kirghizistan", "indicatif": "+996", "drapeau": "🇰🇬", "code": "KG"},
    {"pays": "Koweït", "indicatif": "+965", "drapeau": "🇰🇼", "code": "KW"},
    {"pays": "Laos", "indicatif": "+856", "drapeau": "🇱🇦", "code": "LA"},
    {"pays": "Lesotho", "indicatif": "+266", "drapeau": "🇱🇸", "code": "LS"},
    {"pays": "Lettonie", "indicatif": "+371", "drapeau": "🇱🇻", "code": "LV"},
    {"pays": "Liban", "indicatif": "+961", "drapeau": "🇱🇧", "code": "LB"},
    {"pays": "Libéria", "indicatif": "+231", "drapeau": "🇱🇷", "code": "LR"},
    {"pays": "Libye", "indicatif": "+218", "drapeau": "🇱🇾", "code": "LY"},
    {"pays": "Liechtenstein", "indicatif": "+423", "drapeau": "🇱🇮", "code": "LI"},
    {"pays": "Lituanie", "indicatif": "+370", "drapeau": "🇱🇹", "code": "LT"},
    {"pays": "Luxembourg", "indicatif": "+352", "drapeau": "🇱🇺", "code": "LU"},
    {"pays": "Macédoine du Nord", "indicatif": "+389", "drapeau": "🇲🇰", "code": "MK"},
    {"pays": "Madagascar", "indicatif": "+261", "drapeau": "🇲🇬", "code": "MG"},
    {"pays": "Malaisie", "indicatif": "+60", "drapeau": "🇲🇾", "code": "MY"},
    {"pays": "Malawi", "indicatif": "+265", "drapeau": "🇲🇼", "code": "MW"},
    {"pays": "Maldives", "indicatif": "+960", "drapeau": "🇲🇻", "code": "MV"},
    {"pays": "Mali", "indicatif": "+223", "drapeau": "🇲🇱", "code": "ML"},
    {"pays": "Malte", "indicatif": "+356", "drapeau": "🇲🇹", "code": "MT"},
    {"pays": "Maroc", "indicatif": "+212", "drapeau": "🇲🇦", "code": "MA"},
    {"pays": "Maurice", "indicatif": "+230", "drapeau": "🇲🇺", "code": "MU"},
    {"pays": "Mauritanie", "indicatif": "+222", "drapeau": "🇲🇷", "code": "MR"},
    {"pays": "Mexique", "indicatif": "+52", "drapeau": "🇲🇽", "code": "MX"},
    {"pays": "Moldavie", "indicatif": "+373", "drapeau": "🇲🇩", "code": "MD"},
    {"pays": "Monaco", "indicatif": "+377", "drapeau": "🇲🇨", "code": "MC"},
    {"pays": "Mongolie", "indicatif": "+976", "drapeau": "🇲🇳", "code": "MN"},
    {"pays": "Monténégro", "indicatif": "+382", "drapeau": "🇲🇪", "code": "ME"},
    {"pays": "Mozambique", "indicatif": "+258", "drapeau": "🇲🇿", "code": "MZ"},
    {"pays": "Namibie", "indicatif": "+264", "drapeau": "🇳🇦", "code": "NA"},
    {"pays": "Népal", "indicatif": "+977", "drapeau": "🇳🇵", "code": "NP"},
    {"pays": "Nicaragua", "indicatif": "+505", "drapeau": "🇳🇮", "code": "NI"},
    {"pays": "Niger", "indicatif": "+227", "drapeau": "🇳🇪", "code": "NE"},
    {"pays": "Nigéria", "indicatif": "+234", "drapeau": "🇳🇬", "code": "NG"},
    {"pays": "Norvège", "indicatif": "+47", "drapeau": "🇳🇴", "code": "NO"},
    {"pays": "Nouvelle-Zélande", "indicatif": "+64", "drapeau": "🇳🇿", "code": "NZ"},
    {"pays": "Oman", "indicatif": "+968", "drapeau": "🇴🇲", "code": "OM"},
    {"pays": "Ouganda", "indicatif": "+256", "drapeau": "🇺🇬", "code": "UG"},
    {"pays": "Ouzbékistan", "indicatif": "+998", "drapeau": "🇺🇿", "code": "UZ"},
    {"pays": "Pakistan", "indicatif": "+92", "drapeau": "🇵🇰", "code": "PK"},
    {"pays": "Panama", "indicatif": "+507", "drapeau": "🇵🇦", "code": "PA"},
    {"pays": "Papouasie-Nouvelle-Guinée", "indicatif": "+675", "drapeau": "🇵🇬", "code": "PG"},
    {"pays": "Paraguay", "indicatif": "+595", "drapeau": "🇵🇾", "code": "PY"},
    {"pays": "Pays-Bas", "indicatif": "+31", "drapeau": "🇳🇱", "code": "NL"},
    {"pays": "Pérou", "indicatif": "+51", "drapeau": "🇵🇪", "code": "PE"},
    {"pays": "Philippines", "indicatif": "+63", "drapeau": "🇵🇭", "code": "PH"},
    {"pays": "Pologne", "indicatif": "+48", "drapeau": "🇵🇱", "code": "PL"},
    {"pays": "Portugal", "indicatif": "+351", "drapeau": "🇵🇹", "code": "PT"},
    {"pays": "Qatar", "indicatif": "+974", "drapeau": "🇶🇦", "code": "QA"},
    {"pays": "République dominicaine", "indicatif": "+1849", "drapeau": "🇩🇴", "code": "DO"},
    {"pays": "République tchèque", "indicatif": "+420", "drapeau": "🇨🇿", "code": "CZ"},
    {"pays": "Roumanie", "indicatif": "+40", "drapeau": "🇷🇴", "code": "RO"},
    {"pays": "Royaume-Uni", "indicatif": "+44", "drapeau": "🇬🇧", "code": "GB"},
    {"pays": "Russie", "indicatif": "+7", "drapeau": "🇷🇺", "code": "RU"},
    {"pays": "Rwanda", "indicatif": "+250", "drapeau": "🇷🇼", "code": "RW"},
    {"pays": "Saint-Kitts-et-Nevis", "indicatif": "+1869", "drapeau": "🇰🇳", "code": "KN"},
    {"pays": "Saint-Marin", "indicatif": "+378", "drapeau": "🇸🇲", "code": "SM"},
    {"pays": "Sénégal", "indicatif": "+221", "drapeau": "🇸🇳", "code": "SN"},
    {"pays": "Serbie", "indicatif": "+381", "drapeau": "🇷🇸", "code": "RS"},
    {"pays": "Seychelles", "indicatif": "+248", "drapeau": "🇸🇨", "code": "SC"},
    {"pays": "Sierra Leone", "indicatif": "+232", "drapeau": "🇸🇱", "code": "SL"},
    {"pays": "Singapour", "indicatif": "+65", "drapeau": "🇸🇬", "code": "SG"},
    {"pays": "Slovaquie", "indicatif": "+421", "drapeau": "🇸🇰", "code": "SK"},
    {"pays": "Slovénie", "indicatif": "+386", "drapeau": "🇸🇮", "code": "SI"},
    {"pays": "Somalie", "indicatif": "+252", "drapeau": "🇸🇴", "code": "SO"},
    {"pays": "Soudan", "indicatif": "+249", "drapeau": "🇸🇩", "code": "SD"},
    {"pays": "Sri Lanka", "indicatif": "+94", "drapeau": "🇱🇰", "code": "LK"},
    {"pays": "Suède", "indicatif": "+46", "drapeau": "🇸🇪", "code": "SE"},
    {"pays": "Suisse", "indicatif": "+41", "drapeau": "🇨🇭", "code": "CH"},
    {"pays": "Suriname", "indicatif": "+597", "drapeau": "🇸🇷", "code": "SR"},
    {"pays": "Syrie", "indicatif": "+963", "drapeau": "🇸🇾", "code": "SY"},
    {"pays": "Tadjikistan", "indicatif": "+992", "drapeau": "🇹🇯", "code": "TJ"},
    {"pays": "Tanzanie", "indicatif": "+255", "drapeau": "🇹🇿", "code": "TZ"},
    {"pays": "Tchad", "indicatif": "+235", "drapeau": "🇹🇩", "code": "TD"},
    {"pays": "Thaïlande", "indicatif": "+66", "drapeau": "🇹🇭", "code": "TH"},
    {"pays": "Timor oriental", "indicatif": "+670", "drapeau": "🇹🇱", "code": "TL"},
    {"pays": "Togo", "indicatif": "+228", "drapeau": "🇹🇬", "code": "TG"},
    {"pays": "Tonga", "indicatif": "+676", "drapeau": "🇹🇴", "code": "TO"},
    {"pays": "Trinité-et-Tobago", "indicatif": "+1868", "drapeau": "🇹🇹", "code": "TT"},
    {"pays": "Tunisie", "indicatif": "+216", "drapeau": "🇹🇳", "code": "TN"},
    {"pays": "Turkménistan", "indicatif": "+993", "drapeau": "🇹🇲", "code": "TM"},
    {"pays": "Turquie", "indicatif": "+90", "drapeau": "🇹🇷", "code": "TR"},
    {"pays": "Ukraine", "indicatif": "+380", "drapeau": "🇺🇦", "code": "UA"},
    {"pays": "Uruguay", "indicatif": "+598", "drapeau": "🇺🇾", "code": "UY"},
    {"pays": "Vatican", "indicatif": "+379", "drapeau": "🇻🇦", "code": "VA"},
    {"pays": "Venezuela", "indicatif": "+58", "drapeau": "🇻🇪", "code": "VE"},
    {"pays": "Viêt Nam", "indicatif": "+84", "drapeau": "🇻🇳", "code": "VN"},
    {"pays": "Yémen", "indicatif": "+967", "drapeau": "🇾🇪", "code": "YE"},
    {"pays": "Zambie", "indicatif": "+260", "drapeau": "🇿🇲", "code": "ZM"},
    {"pays": "Zimbabwe", "indicatif": "+263", "drapeau": "🇿🇼", "code": "ZW"}
]

# ============================================================
# FONCTIONS DE GESTION DES NUMÉROS DE TÉLÉPHONE
# ============================================================
def get_pays_from_phone(phone):
    """Détermine le pays à partir du numéro de téléphone"""
    if not phone:
        return None
    
    # Nettoyer le numéro
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Trier les indicatifs par longueur décroissante pour éviter les conflits
    pays_tries = sorted(PAYS_INDICATIFS, key=lambda x: len(x['indicatif']), reverse=True)
    
    for pays in pays_tries:
        indicatif = pays['indicatif'].replace('+', '')
        if phone_clean.startswith(indicatif):
            return pays
    
    return None

def format_phone_with_country(phone):
    """Formate un numéro de téléphone avec le pays détecté"""
    pays = get_pays_from_phone(phone)
    if pays:
        return f"{pays['drapeau']} {phone} ({pays['pays']})"
    return phone

def get_country_code_from_phone(phone):
    """Récupère le code pays à partir du numéro"""
    pays = get_pays_from_phone(phone)
    if pays:
        return pays['code']
    return None

# ============================================================
# CSS STYLE
# ============================================================
def set_custom_theme():
    """Définit les thèmes light et dark avec animations"""
    st.markdown(f"""
    <style>
        /* ===== THÈME LIGHT ===== */
        [data-testid="stAppViewContainer"] > .main {{
            background-color: #f8f9fa;
            background-image: linear-gradient(135deg, rgba(174, 176, 202, 0.05) 0%, #f8f9fa 100%);
        }}
        
        /* ===== THÈME DARK ===== */
        @media (prefers-color-scheme: dark) {{
            [data-testid="stAppViewContainer"] > .main {{
                background-color: #0e1117;
                background-image: linear-gradient(135deg, rgba(19, 23, 34, 0.8) 0%, #0e1117 100%);
                color: #f0f2f6;
            }}
        }}
        
        /* ===== ANIMATIONS COMMUNES ===== */
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes fadeInSlide {{
            from {{ 
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{ 
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Header animé */
        [data-testid="stHeader"] {{
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
        }}
        
        @media (prefers-color-scheme: dark) {{
            [data-testid="stHeader"] {{
                background-color: rgba(14, 17, 23, 0.9);
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
            }}
        }}
        
        /* Titres animés */
        h1, h2, h3, h4, h5, h6 {{
            animation: fadeIn 0.8s ease-out;
        }}
        
        /* Boutons avec effets */
        .stButton>button {{
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            transform: translateY(0);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .stButton>button {{
            background-color: #4a6fa5;
            color: white;
        }}
        
        .stButton>button:hover {{
            background-color: #3a5a8f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }}
        
        @media (prefers-color-scheme: dark) {{
            .stButton>button {{
                background-color: #166088;
                color: white;
            }}
            
            .stButton>button:hover {{
                background-color: #0d4b6e;
            }}
        }}
        
        /* Cartes métriques */
        [data-testid="metric-container"] {{
            border-radius: 10px;
            padding: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        [data-testid="metric-container"] {{
            background-color: white;
            border-left: 4px solid #4a6fa5;
        }}
        
        @media (prefers-color-scheme: dark) {{
            [data-testid="metric-container"] {{
                background-color: #1e2130;
                border-left: 4px solid #166088;
            }}
        }}
        
        [data-testid="metric-container"]:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}
        
        /* Conteneur principal */
        .main-container {{
            background: linear-gradient(135deg, #f8faff 0%, #e6ecff 100%);
            border-radius: 18px;
            padding: 2rem;
            box-shadow: 0 12px 24px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
            transition: all 0.5s ease;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .main-container {{
                background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
                box-shadow: 0 12px 28px rgba(16, 20, 58, 0.3);
            }}
        }}
        
        .main-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .animated-entry {{
            animation: fadeInSlide 0.8s ease-out;
        }}
        
        /* Login container */
        .login-container {{
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            padding: 2em;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            color: white;
        }}
        
        /* Password strength indicator */
        .password-strength {{
            margin: 0.5rem 0;
            padding: 0.5rem;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .password-strength {{
                background: #1e2130;
            }}
        }}
        
        /* Country display */
        .country-display {{
            padding: 0.5rem;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .country-flag-large {{
            font-size: 2rem;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #4a6fa5;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #3a5a8f;
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# CLASSE DATABASE
# ============================================================
class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connect()
        self._fix_and_create_tables()

    def _connect(self):
        """Connexion à MySQL avec timeout configurable"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.connection = mysql.connector.connect(
                    host='ecocapital-mbfdm.c.aivencloud.com',
                    user='avnadmin',
                    password='AVNS_3a2plzaevzttmJ4Tcs9',
                    database='ecocapital',
                    port=14431,
                    connect_timeout=30,
                    buffered=True,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    autocommit=False,
                    pool_reset_session=True
                )
                self.cursor = self.connection.cursor(dictionary=True)
                
                # Configurer le timeout de session
                self.cursor.execute("SET SESSION wait_timeout = 28800")
                self.cursor.execute("SET SESSION interactive_timeout = 28800")
                
                # Tester la connexion
                self.cursor.execute("SELECT 1")
                print("✅ Connexion MySQL réussie")
                return
                
            except Error as e:
                print(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    st.error(f"❌ Erreur de connexion MySQL : {e}")
                    st.stop()

    def _ensure_connection(self):
        """Vérifie et rétablit la connexion si nécessaire"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("Reconnexion à MySQL...")
                self._connect()
            else:
                # Tester la connexion
                self.cursor.execute("SELECT 1")
        except (Error, mysql.connector.OperationalError) as e:
            print(f"Connexion perdue, tentative de reconnexion: {e}")
            try:
                self._connect()
            except Exception as reconnect_error:
                print(f"Échec de reconnexion: {reconnect_error}")
                raise

    def keep_alive(self):
        """Maintient la connexion active"""
        try:
            if self.connection and self.connection.is_connected():
                self.cursor.execute("SELECT 1")
                self.cursor.fetchone()
        except:
            self._connect()

    def _get_existing_columns(self, table_name):
        try:
            self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = self.cursor.fetchall()
            return [col['Field'] for col in columns]
        except Error:
            return []

    def _fix_utilisateurs_table(self):
        existing_columns = self._get_existing_columns('utilisateurs')
        
        if not existing_columns:
            print("Création de la table utilisateurs...")
            return False
        
        required_columns = {
            'id': 'VARCHAR(36) NOT NULL PRIMARY KEY',
            'first_name': 'VARCHAR(100) NOT NULL',
            'last_name': 'VARCHAR(100) NOT NULL',
            'email': 'VARCHAR(255) NOT NULL UNIQUE',
            'phone': 'VARCHAR(50)',
            'country_code': 'VARCHAR(10)',
            'country_name': 'VARCHAR(100)',
            'password': 'VARCHAR(255) NOT NULL',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'last_login': 'TIMESTAMP NULL',
            'is_active': 'BOOLEAN DEFAULT TRUE'
        }
        
        for col_name, col_def in required_columns.items():
            if col_name not in existing_columns:
                try:
                    if col_name == 'id':
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} FIRST")
                    elif col_name == 'first_name':
                        if 'name' in existing_columns:
                            self.cursor.execute("ALTER TABLE utilisateurs CHANGE name first_name VARCHAR(100) NOT NULL")
                            continue
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER id")
                    elif col_name == 'last_name':
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER first_name")
                    elif col_name == 'email':
                        if 'email' in existing_columns:
                            try:
                                self.cursor.execute("ALTER TABLE utilisateurs MODIFY COLUMN email VARCHAR(255) NOT NULL UNIQUE")
                            except Error:
                                pass
                            continue
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER last_name")
                    elif col_name == 'phone':
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER email")
                    elif col_name in ['country_code', 'country_name']:
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER phone")
                    elif col_name == 'password':
                        if 'password' in existing_columns:
                            continue
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER country_name")
                    else:
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def}")
                except Error as e:
                    print(f"⚠️ Impossible d'ajouter {col_name}: {e}")
        
        try:
            self.cursor.execute("SHOW KEYS FROM utilisateurs WHERE Key_name = 'PRIMARY'")
            pk = self.cursor.fetchall()
            if not pk or pk[0]['Column_name'] != 'id':
                try:
                    self.cursor.execute("ALTER TABLE utilisateurs DROP PRIMARY KEY")
                except Error:
                    pass
                self.cursor.execute("ALTER TABLE utilisateurs ADD PRIMARY KEY (id)")
        except Error as e:
            print(f"⚠️ Erreur clé primaire: {e}")
        
        self.connection.commit()
        return True

    def _fix_and_create_tables(self):
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Vérifier si la table utilisateurs existe
            self.cursor.execute("""
                SELECT COUNT(*) as cnt FROM information_schema.tables 
                WHERE table_schema = 'ecocapital' AND table_name = 'utilisateurs'
            """)
            table_exists = self.cursor.fetchone()['cnt'] > 0
            
            if table_exists:
                self._fix_utilisateurs_table()
            else:
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS utilisateurs (
                        id VARCHAR(36) NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        phone VARCHAR(50),
                        country_code VARCHAR(10),
                        country_name VARCHAR(100),
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        PRIMARY KEY (id),
                        UNIQUE KEY uk_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            
            # Vérifier si la table password_reset_tokens existe
            self.cursor.execute("""
                SELECT COUNT(*) as cnt FROM information_schema.tables 
                WHERE table_schema = 'ecocapital' AND table_name = 'password_reset_tokens'
            """)
            token_table_exists = self.cursor.fetchone()['cnt'] > 0
            
            if token_table_exists:
                # Vérifier les colonnes existantes
                existing_token_cols = self._get_existing_columns('password_reset_tokens')
                
                # Ajouter les colonnes manquantes si nécessaire
                required_token_cols = {
                    'country_code': 'VARCHAR(10)',
                    'country_name': 'VARCHAR(100)'
                }
                
                for col_name, col_def in required_token_cols.items():
                    if col_name not in existing_token_cols:
                        try:
                            self.cursor.execute(f"ALTER TABLE password_reset_tokens ADD COLUMN {col_name} {col_def}")
                            print(f"✅ Colonne {col_name} ajoutée à password_reset_tokens")
                        except Error as e:
                            print(f"⚠️ Impossible d'ajouter {col_name}: {e}")
            else:
                # Créer la table des tokens
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id VARCHAR(36) NOT NULL PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        token VARCHAR(10) NOT NULL,
                        phone VARCHAR(50) NOT NULL,
                        country_code VARCHAR(10),
                        country_name VARCHAR(100),
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        KEY idx_reset_user (user_id),
                        KEY idx_reset_token (token),
                        KEY idx_reset_phone (phone),
                        FOREIGN KEY (user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            
            # Les autres tables
            tables_sql = [
                """CREATE TABLE IF NOT EXISTS avi_requests (
                    id VARCHAR(50) NOT NULL PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    user_email VARCHAR(255),
                    request_data JSON,
                    status VARCHAR(50) DEFAULT 'En attente',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    KEY idx_avi_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
                
                """CREATE TABLE IF NOT EXISTS messages (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    sender VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    attachment LONGBLOB,
                    attachment_filename VARCHAR(255),
                    attachment_type VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE,
                    KEY idx_msg_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
                
                """CREATE TABLE IF NOT EXISTS conversations (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    last_message TEXT,
                    unread_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    KEY idx_conv_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
                
                """CREATE TABLE IF NOT EXISTS documents (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    request_id VARCHAR(50),
                    filename VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50),
                    file_size INT,
                    file_data LONGBLOB,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    KEY idx_doc_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
            ]
            
            for sql in tables_sql:
                self.cursor.execute(sql)
            
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            
        except Error as e:
            print(f"❌ Erreur: {e}")
            st.error(f"Erreur MySQL: {e}")

    # ==================== GESTION DES TOKENS ====================
    def create_password_reset_token(self, user_id, token, phone):
        """Crée un token de réinitialisation de mot de passe avec les infos du pays"""
        try:
            # Déterminer le pays à partir du numéro
            pays_info = get_pays_from_phone(phone)
            
            # Supprimer les anciens tokens pour cet utilisateur
            self.cursor.execute(
                "DELETE FROM password_reset_tokens WHERE user_id = %s",
                (user_id,)
            )
            
            # Insérer le nouveau token
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # Vérifier d'abord les colonnes existantes
            existing_cols = self._get_existing_columns('password_reset_tokens')
            
            if 'country_code' in existing_cols and 'country_name' in existing_cols:
                if pays_info:
                    self.cursor.execute(
                        """INSERT INTO password_reset_tokens 
                           (id, user_id, token, phone, country_code, country_name, expires_at, created_at) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                        (str(uuid.uuid4()), user_id, token, phone, 
                         pays_info['code'], pays_info['pays'], expires_at)
                    )
                else:
                    self.cursor.execute(
                        """INSERT INTO password_reset_tokens 
                           (id, user_id, token, phone, expires_at, created_at) 
                           VALUES (%s, %s, %s, %s, %s, NOW())""",
                        (str(uuid.uuid4()), user_id, token, phone, expires_at)
                    )
            else:
                # Version simplifiée sans les colonnes pays
                self.cursor.execute(
                    """INSERT INTO password_reset_tokens 
                       (id, user_id, token, phone, expires_at, created_at) 
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    (str(uuid.uuid4()), user_id, token, phone, expires_at)
                )
            
            self.connection.commit()
            return True, pays_info
        except Error as e:
            print(f"Erreur création token: {e}")
            return False, None
    
    def verify_reset_token(self, token, phone):
        """Vérifie la validité d'un token de réinitialisation"""
        try:
            self.cursor.execute(
                """SELECT * FROM password_reset_tokens 
                   WHERE token = %s AND phone = %s 
                   AND expires_at > NOW() 
                   AND used = FALSE
                   ORDER BY created_at DESC LIMIT 1""",
                (token, phone)
            )
            result = self.cursor.fetchone()
            return result
        except Error as e:
            print(f"Erreur vérification token: {e}")
            return None
    
    def mark_token_as_used(self, token):
        """Marque un token comme utilisé"""
        try:
            self.cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (token,)
            )
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erreur marquage token: {e}")
            return False
    
    def update_user_password(self, user_id, new_password):
        """Met à jour le mot de passe d'un utilisateur"""
        try:
            hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
            self.cursor.execute(
                "UPDATE utilisateurs SET password = %s WHERE id = %s",
                (hashed_pw, user_id)
            )
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erreur mise à jour mot de passe: {e}")
            return False
    
    def get_user_by_phone(self, phone):
        """Récupère un utilisateur par son numéro de téléphone"""
        try:
            # Nettoyer le numéro pour la recherche
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
            self.cursor.execute(
                "SELECT * FROM utilisateurs WHERE REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', '') = %s AND is_active = TRUE",
                (phone_clean,)
            )
            return self.cursor.fetchone()
        except Error as e:
            print(f"Erreur recherche par téléphone: {e}")
            return None

    def create_user_with_country(self, first_name, last_name, email, phone, password):
        """Crée un utilisateur avec les informations du pays"""
        try:
            user_id = str(uuid.uuid4())
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            
            existing = self.get_user_by_email(email)
            if existing:
                return False, "Cet email est déjà utilisé"
            
            # Déterminer le pays
            pays_info = get_pays_from_phone(phone)
            
            # Vérifier les colonnes existantes dans utilisateurs
            existing_cols = self._get_existing_columns('utilisateurs')
            
            if 'country_code' in existing_cols and 'country_name' in existing_cols:
                if pays_info:
                    self.cursor.execute(
                        """INSERT INTO utilisateurs 
                           (id, first_name, last_name, email, phone, country_code, country_name, password) 
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (user_id, first_name, last_name, email, phone, 
                         pays_info['code'], pays_info['pays'], hashed_pw)
                    )
                else:
                    self.cursor.execute(
                        "INSERT INTO utilisateurs (id, first_name, last_name, email, phone, password) VALUES (%s,%s,%s,%s,%s,%s)",
                        (user_id, first_name, last_name, email, phone, hashed_pw)
                    )
            else:
                self.cursor.execute(
                    "INSERT INTO utilisateurs (id, first_name, last_name, email, phone, password) VALUES (%s,%s,%s,%s,%s,%s)",
                    (user_id, first_name, last_name, email, phone, hashed_pw)
                )
            
            self.connection.commit()
            return True, user_id
        except Error as e:
            return False, str(e)

    def create_user(self, first_name, last_name, email, phone, password):
        """Méthode existante modifiée pour utiliser create_user_with_country"""
        return self.create_user_with_country(first_name, last_name, email, phone, password)

    # ==================== AUTRES MÉTHODES ====================
    def send_message_with_attachment(self, user_id, sender, content, file_bytes, filename, file_type):
        try:
            msg_id = str(uuid.uuid4())
            
            self.cursor.execute("""
                SHOW COLUMNS FROM messages 
                WHERE Field IN ('attachment', 'attachment_filename', 'attachment_type')
            """)
            existing_cols = [col['Field'] for col in self.cursor.fetchall()]
            
            if 'attachment' not in existing_cols:
                self.cursor.execute("ALTER TABLE messages ADD COLUMN attachment LONGBLOB")
            if 'attachment_filename' not in existing_cols:
                self.cursor.execute("ALTER TABLE messages ADD COLUMN attachment_filename VARCHAR(255)")
            if 'attachment_type' not in existing_cols:
                self.cursor.execute("ALTER TABLE messages ADD COLUMN attachment_type VARCHAR(50)")
            
            self.connection.commit()
            
            self.cursor.execute("""
                INSERT INTO messages (id, user_id, sender, content, attachment, attachment_filename, attachment_type, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (msg_id, user_id, sender, content, file_bytes, filename, file_type))
            
            self.connection.commit()
            return True, msg_id
        except Error as e:
            return False, str(e)

    def get_user_messages_with_attachments(self, user_id, limit=50):
        try:
            self._ensure_connection()
            self.cursor.execute("""
                SELECT * FROM messages 
                WHERE user_id=%s 
                ORDER BY timestamp DESC LIMIT %s
            """, (user_id, limit))
            msgs = self.cursor.fetchall()
            
            self.cursor.execute("""
                UPDATE messages SET is_read=TRUE 
                WHERE user_id=%s AND sender='support' AND is_read=FALSE
            """, (user_id,))
            self.connection.commit()
            
            return msgs[::-1]
        except Error:
            return []

    def authenticate_user(self, email, password):
        try:
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute(
                "SELECT * FROM utilisateurs WHERE email=%s AND password=%s AND is_active=TRUE",
                (email, hashed_pw)
            )
            user = self.cursor.fetchone()
            if user:
                self.cursor.execute("UPDATE utilisateurs SET last_login=NOW() WHERE id=%s", (user['id'],))
                self.connection.commit()
            return user
        except Error as e:
            return None

    def get_user_by_email(self, email):
        try:
            self.cursor.execute("SELECT * FROM utilisateurs WHERE email=%s", (email,))
            return self.cursor.fetchone()
        except Error:
            return None

    def create_avi_request(self, user_id, user_email, request_data):
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            self.cursor.execute("SELECT COUNT(*) as c FROM avi_requests WHERE id LIKE %s", (f"AVI-{date_str}-%",))
            count = self.cursor.fetchone()['c'] + 1
            request_id = f"AVI-{date_str}-{count:03d}"
            self.cursor.execute(
                "INSERT INTO avi_requests (id, user_id, user_email, request_data) VALUES (%s,%s,%s,%s)",
                (request_id, user_id, user_email, json.dumps(request_data))
            )
            self.connection.commit()
            return True, request_id
        except Error as e:
            return False, str(e)

    def get_user_avi_requests(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM avi_requests WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            requests = self.cursor.fetchall()
            for r in requests:
                if isinstance(r.get('request_data'), str):
                    r['request_data'] = json.loads(r['request_data'])
            return requests
        except Error:
            return []

    def get_avi_stats(self, user_id):
        stats = {}
        queries = {
            'total': "SELECT COUNT(*) as c FROM avi_requests WHERE user_id=%s",
            'validated': "SELECT COUNT(*) as c FROM avi_requests WHERE user_id=%s AND status='Validée'",
            'pending': "SELECT COUNT(*) as c FROM avi_requests WHERE user_id=%s AND status='En attente'",
            'rejected': "SELECT COUNT(*) as c FROM avi_requests WHERE user_id=%s AND status='Rejetée'"
        }
        for key, query in queries.items():
            try:
                self.cursor.execute(query, (user_id,))
                stats[key] = self.cursor.fetchone()['c']
            except Error:
                stats[key] = 0
        return stats

    def create_conversation(self, user_id, name):
        try:
            conv_id = str(uuid.uuid4())
            self.cursor.execute("INSERT INTO conversations (id, user_id, name) VALUES (%s,%s,%s)", (conv_id, user_id, name))
            self.connection.commit()
            return conv_id
        except Error:
            return None

    def get_user_conversations(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM conversations WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            return self.cursor.fetchall()
        except Error:
            return []

    def send_message(self, user_id, sender, content):
        try:
            msg_id = str(uuid.uuid4())
            self.cursor.execute(
                "INSERT INTO messages (id, user_id, sender, content) VALUES (%s,%s,%s,%s)",
                (msg_id, user_id, sender, content)
            )
            self.connection.commit()
            return True, msg_id
        except Error as e:
            return False, str(e)

    def get_user_messages(self, user_id, limit=50):
        try:
            self.cursor.execute("SELECT * FROM messages WHERE user_id=%s ORDER BY timestamp DESC LIMIT %s", (user_id, limit))
            msgs = self.cursor.fetchall()
            self.cursor.execute("UPDATE messages SET is_read=TRUE WHERE user_id=%s AND sender='support' AND is_read=FALSE", (user_id,))
            self.connection.commit()
            return msgs[::-1]
        except Error:
            return []

    def get_unread_messages_count(self, user_id):
        try:
            self.cursor.execute("SELECT COUNT(*) as c FROM messages WHERE user_id=%s AND sender='support' AND is_read=FALSE", (user_id,))
            return self.cursor.fetchone()['c']
        except Error:
            return 0

    def save_document(self, user_id, filename, file_data, file_type):
        try:
            doc_id = str(uuid.uuid4())
            self.cursor.execute(
                "INSERT INTO documents (id, user_id, filename, file_type, file_size, file_data) VALUES (%s,%s,%s,%s,%s,%s)",
                (doc_id, user_id, filename, file_type, len(file_data), file_data)
            )
            self.connection.commit()
            return True, doc_id
        except Error as e:
            return False, str(e)

    def get_user_avis(self, user_id):
        try:
            self._ensure_connection()
            
            self.cursor.execute('''
            SELECT id, first_name, last_name, email FROM utilisateurs WHERE id = %s
            ''', (user_id,))
            user = self.cursor.fetchone()
            
            if not user:
                return []
            
            user_first = user.get('first_name', '')
            user_last = user.get('last_name', '')
            
            query = '''
            SELECT 
                reference,
                nom_complet,
                code_banque,
                numero_compte,
                devise,
                iban,
                bic,
                montant,
                date_creation,
                date_expiration,
                statut,
                commentaires,
                created_at
            FROM avis
            WHERE LOWER(nom_complet) LIKE LOWER(%s)
               OR LOWER(nom_complet) LIKE LOWER(%s)
            ORDER BY date_creation DESC
            '''
            
            search_pattern1 = f'%{user_first}%'
            search_pattern2 = f'%{user_last}%'
            
            self.cursor.execute(query, (search_pattern1, search_pattern2))
            results = self.cursor.fetchall()
            
            return results
            
        except Error as e:
            print(f"Erreur get_user_avis: {e}")
            try:
                self._ensure_connection()
                self.cursor.execute(query, (search_pattern1, search_pattern2))
                return self.cursor.fetchall()
            except:
                return []
        except Exception as e:
            print(f"Erreur générale get_user_avis: {e}")
            return []

# ============================================================
# INIT DB
# ============================================================
@st.cache_resource
def get_db():
    return Database()

db = get_db()

# ============================================================
# ANIMATION LOTTIE
# ============================================================
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ============================================================
# SIMULATION D'ENVOI DE SMS
# ============================================================
def send_sms_simulation(phone, token, pays_info=None):
    """Simule l'envoi d'un SMS avec le token"""
    country_display = ""
    if pays_info:
        country_display = f" ({pays_info['drapeau']} {pays_info['pays']})"
    
    # Dans un environnement de production, remplacer par un vrai service SMS
    st.info(f"📱 SMS envoyé à {phone}{country_display}")
    st.caption(f"🔑 Code de vérification: **{token}** (valable 10 minutes)")
    
    # Log pour le débogage
    print(f"[SMS] Envoi du code {token} à {phone} {country_display}")
    
    return True

# ============================================================
# PAGE MOT DE PASSE OUBLIÉ
# ============================================================
def forgot_password_page():
    """Page de réinitialisation du mot de passe avec détection du pays"""
    set_custom_theme()
    
    # Cache pour stocker l'état du processus
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1
    if 'reset_phone' not in st.session_state:
        st.session_state.reset_phone = ""
    if 'reset_user_id' not in st.session_state:
        st.session_state.reset_user_id = ""
    if 'reset_token' not in st.session_state:
        st.session_state.reset_token = ""
    if 'reset_pays_info' not in st.session_state:
        st.session_state.reset_pays_info = None
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🔐 Mot de passe oublié</h1>
        <p style="color: rgba(255,255,255,0.9);">Retrouvez l'accès à votre compte</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.reset_step == 1:
        # Étape 1: Saisie du numéro de téléphone
        with st.container():
            st.markdown("""
            <div class="login-container" style="max-width: 600px; margin: 0 auto;">
                <h3 style="text-align: center; color: white;">📱 Réinitialisation</h3>
                <p style="text-align: center; color: rgba(255,255,255,0.9); font-size: 0.9rem;">
                    Entrez votre numéro de téléphone avec l'indicatif du pays
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sélecteur de pays avec drapeau
            st.markdown("### 🌍 Sélectionnez votre pays")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                # Liste des pays pour le selectbox
                pays_options = [f"{p['drapeau']} {p['pays']} ({p['indicatif']})" for p in PAYS_INDICATIFS]
                selected_index = 0  # Congo Brazzaville par défaut
                
                # Trouver l'index du Congo Brazzaville
                for i, p in enumerate(PAYS_INDICATIFS):
                    if p['code'] == 'CG':
                        selected_index = i
                        break
                
                selected_pays = st.selectbox(
                    "Pays",
                    pays_options,
                    index=selected_index,
                    key="pays_select"
                )
                
                # Extraire l'indicatif du pays sélectionné
                selected_indicatif = ""
                for p in PAYS_INDICATIFS:
                    if f"{p['drapeau']} {p['pays']} ({p['indicatif']})" == selected_pays:
                        selected_indicatif = p['indicatif']
                        break
            
            with col2:
                st.markdown("### 📞 Votre numéro")
                
                with st.form("phone_form", clear_on_submit=False):
                    phone_without_code = st.text_input(
                        "Numéro de téléphone *",
                        placeholder="Ex: 6 123 45 67",
                        key="reset_phone_input",
                        help="Entrez votre numéro sans l'indicatif"
                    )
                    
                    # Afficher le numéro complet avec l'indicatif
                    if phone_without_code and selected_indicatif:
                        full_phone = selected_indicatif + phone_without_code.replace(' ', '')
                        pays_info = get_pays_from_phone(full_phone)
                        
                        if pays_info:
                            st.markdown(f"""
                            <div class="country-display">
                                <span class="country-flag-large">{pays_info['drapeau']}</span>
                                <div>
                                    <strong>{pays_info['pays']}</strong>
                                    <br>
                                    <span style="font-size: 0.9rem; opacity: 0.8;">Numéro complet: {pays_info['indicatif']} {phone_without_code}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Indicatif non reconnu pour ce numéro")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        back = st.form_submit_button("⬅️ Retour", use_container_width=True)
                    with col2:
                        send_code = st.form_submit_button("📤 Envoyer le code", use_container_width=True)
                    
                    if back:
                        for key in ['reset_step', 'reset_phone', 'reset_user_id', 'reset_token', 'reset_pays_info']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.session_state.show_forgot_password = False
                        st.rerun()
                    
                    if send_code:
                        if not phone_without_code or len(phone_without_code) < 6:
                            st.error("⚠️ Veuillez entrer un numéro de téléphone valide")
                        else:
                            # Construire le numéro complet
                            full_phone = selected_indicatif + phone_without_code.replace(' ', '')
                            pays_info = get_pays_from_phone(full_phone)
                            
                            if not pays_info:
                                st.error("⚠️ Indicatif non reconnu. Veuillez sélectionner le bon pays.")
                            else:
                                # Vérifier si l'utilisateur existe
                                user = db.get_user_by_phone(full_phone)
                                if user:
                                    # Générer un token de 6 chiffres
                                    token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                                    
                                    # Sauvegarder le token
                                    success, pays_info_result = db.create_password_reset_token(
                                        user['id'], token, full_phone
                                    )
                                    
                                    if success:
                                        st.session_state.reset_phone = full_phone
                                        st.session_state.reset_user_id = user['id']
                                        st.session_state.reset_token = token
                                        st.session_state.reset_pays_info = pays_info
                                        st.session_state.reset_step = 2
                                        
                                        # Envoyer le SMS
                                        send_sms_simulation(full_phone, token, pays_info)
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ Erreur lors de l'envoi du code. Réessayez.")
                                else:
                                    st.error(f"❌ Aucun compte trouvé avec le numéro {full_phone}")
    
    elif st.session_state.reset_step == 2:
        # Étape 2: Vérification du code SMS
        with st.container():
            pays_info = st.session_state.reset_pays_info
            country_display = f"{pays_info['drapeau']} {pays_info['pays']}" if pays_info else ""
            
            st.markdown(f"""
            <div class="login-container" style="max-width: 500px; margin: 0 auto;">
                <h3 style="text-align: center; color: white;">✅ Vérification</h3>
                <p style="text-align: center; color: rgba(255,255,255,0.9); font-size: 0.9rem;">
                    Entrez le code reçu par SMS
                </p>
                <p style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.8rem;">
                    Envoyé au {country_display} {st.session_state.reset_phone}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("token_form", clear_on_submit=False):
                token = st.text_input(
                    "Code de vérification *",
                    placeholder="Ex: 123456",
                    max_chars=6,
                    key="reset_token_input",
                    help="Entrez le code à 6 chiffres reçu par SMS"
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    back = st.form_submit_button("⬅️ Précédent", use_container_width=True)
                with col2:
                    resend = st.form_submit_button("🔄 Renvoyer", use_container_width=True)
                with col3:
                    verify = st.form_submit_button("✅ Vérifier", use_container_width=True)
                
                if back:
                    st.session_state.reset_step = 1
                    st.rerun()
                
                if resend:
                    new_token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    
                    success, pays_info_result = db.create_password_reset_token(
                        st.session_state.reset_user_id, 
                        new_token, 
                        st.session_state.reset_phone
                    )
                    
                    if success:
                        st.session_state.reset_token = new_token
                        st.success("✅ Nouveau code envoyé par SMS")
                        send_sms_simulation(st.session_state.reset_phone, new_token, st.session_state.reset_pays_info)
                    else:
                        st.error("❌ Erreur lors du renvoi du code")
                
                if verify:
                    if not token or len(token) != 6:
                        st.error("⚠️ Veuillez entrer un code valide à 6 chiffres")
                    else:
                        token_data = db.verify_reset_token(token, st.session_state.reset_phone)
                        
                        if token_data:
                            st.session_state.reset_step = 3
                            st.success("✅ Code vérifié avec succès")
                            st.rerun()
                        else:
                            st.error("❌ Code invalide ou expiré. Veuillez en demander un nouveau.")
    
    elif st.session_state.reset_step == 3:
        # Étape 3: Modification du mot de passe
        with st.container():
            pays_info = st.session_state.reset_pays_info
            country_display = f"{pays_info['drapeau']} {pays_info['pays']}" if pays_info else ""
            
            st.markdown(f"""
            <div class="login-container" style="max-width: 500px; margin: 0 auto;">
                <h3 style="text-align: center; color: white;">🔑 Nouveau mot de passe</h3>
                <p style="text-align: center; color: rgba(255,255,255,0.9); font-size: 0.9rem;">
                    Créez un nouveau mot de passe sécurisé
                </p>
                <p style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.8rem;">
                    {country_display}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("new_password_form", clear_on_submit=False):
                new_password = st.text_input(
                    "Nouveau mot de passe *",
                    type="password",
                    placeholder="••••••••••",
                    key="new_password"
                )
                
                confirm_password = st.text_input(
                    "Confirmer le mot de passe *",
                    type="password",
                    placeholder="••••••••••",
                    key="confirm_password"
                )
                
                # Indicateur de force du mot de passe
                if new_password:
                    strength = 0
                    if len(new_password) >= 8:
                        strength += 1
                    if any(c.isupper() for c in new_password):
                        strength += 1
                    if any(c.islower() for c in new_password):
                        strength += 1
                    if any(c.isdigit() for c in new_password):
                        strength += 1
                    if any(c in "!@#$%^&*()_+-=,.;:?/" for c in new_password):
                        strength += 1
                    
                    strength_text = ["Très faible", "Faible", "Moyen", "Fort", "Très fort", "Excellent"]
                    strength_color = ["#ef4444", "#f59e0b", "#f59e0b", "#22c55e", "#22c55e", "#16a34a"]
                    
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 8px;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 0.8rem; color: #666;">Force:</span>
                            <div style="flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                                <div style="width: {strength/5*100}%; height: 100%; background: {strength_color[strength]}; border-radius: 3px; transition: width 0.3s;"></div>
                            </div>
                            <span style="font-size: 0.8rem; font-weight: 600; color: {strength_color[strength]};">{strength_text[strength]}</span>
                        </div>
                        <div style="font-size: 0.7rem; color: #999; margin-top: 0.3rem;">
                            {">= 8 caractères" if len(new_password) >= 8 else "❌ 8 caractères minimum"} • 
                            {"✅ Majuscule" if any(c.isupper() for c in new_password) else "❌ Majuscule"} • 
                            {"✅ Minuscule" if any(c.islower() for c in new_password) else "❌ Minuscule"} • 
                            {"✅ Chiffre" if any(c.isdigit() for c in new_password) else "❌ Chiffre"} • 
                            {"✅ Caractère spécial" if any(c in "!@#$%^&*()_+-=,.;:?/" for c in new_password) else "❌ Caractère spécial"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    back = st.form_submit_button("⬅️ Précédent", use_container_width=True)
                with col2:
                    update = st.form_submit_button("🔑 Mettre à jour", use_container_width=True)
                
                if back:
                    st.session_state.reset_step = 2
                    st.rerun()
                
                if update:
                    if not new_password or not confirm_password:
                        st.error("⚠️ Veuillez remplir tous les champs")
                    elif new_password != confirm_password:
                        st.error("⚠️ Les mots de passe ne correspondent pas")
                    elif len(new_password) < 8:
                        st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères")
                    else:
                        success = db.update_user_password(st.session_state.reset_user_id, new_password)
                        
                        if success:
                            token_data = db.verify_reset_token(
                                st.session_state.reset_token, 
                                st.session_state.reset_phone
                            )
                            if token_data:
                                db.mark_token_as_used(st.session_state.reset_token)
                            
                            st.success("✅ Mot de passe mis à jour avec succès !")
                            st.balloons()
                            
                            st.markdown("""
                            <div style="text-align: center; padding: 1rem; background: #d1fae5; border-radius: 10px; margin: 1rem 0;">
                                <h4 style="color: #065f46;">🔐 Votre mot de passe a été réinitialisé</h4>
                                <p style="color: #065f46;">Vous pouvez maintenant vous connecter avec votre nouveau mot de passe</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("🔐 Aller à la page de connexion", use_container_width=True):
                                for key in ['reset_step', 'reset_phone', 'reset_user_id', 'reset_token', 
                                           'reset_pays_info', 'reset_phone_input', 'reset_token_input', 
                                           'new_password', 'confirm_password']:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                
                                st.session_state.show_forgot_password = False
                                st.session_state.logged_in = False
                                st.session_state.user = None
                                st.rerun()
                        else:
                            st.error("❌ Erreur lors de la mise à jour du mot de passe")

# ============================================================
# PAGE D'AUTHENTIFICATION
# ============================================================
def auth_page():
    set_custom_theme()
    
    lottie_banking = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json")
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem;">EcoCapital</h1>
        <p style="color: rgba(255,255,255,0.9);">Votre Partenaire Financier de Confiance</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if lottie_banking:
            st_lottie(lottie_banking, height=350, key="banking")
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Connexion", "Inscription"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="exemple@email.com")
                password = st.text_input("Mot de passe", type="password", placeholder="..........")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_clicked = st.form_submit_button("Se connecter", use_container_width=True)
                with col2:
                    forgot_clicked = st.form_submit_button("🔑 Mot de passe oublié", use_container_width=True)
                
                if login_clicked:
                    if email and password:
                        user = db.authenticate_user(email, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success("Connexion réussie !")
                            st.rerun()
                        else:
                            st.error("Email ou mot de passe incorrect")
                
                if forgot_clicked:
                    st.session_state.reset_step = 1
                    st.session_state.show_forgot_password = True
                    st.rerun()

                st.page_link("https://ecocapitale-bm.streamlit.app/", label="EcoCapital")                     
        
        with tab2:
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("Prénom")
                with col2:
                    last_name = st.text_input("Nom")
                
                email = st.text_input("Email")
                
                # Sélecteur de pays pour l'inscription
                st.markdown("**📍 Pays et numéro de téléphone**")
                col1, col2 = st.columns([1, 2])
                with col1:
                    pays_options = [f"{p['drapeau']} {p['pays']} ({p['indicatif']})" for p in PAYS_INDICATIFS]
                    selected_idx = 0
                    for i, p in enumerate(PAYS_INDICATIFS):
                        if p['code'] == 'CG':
                            selected_idx = i
                            break
                    selected_pays = st.selectbox("Pays", pays_options, index=selected_idx, key="register_pays")
                    
                    # Extraire l'indicatif
                    selected_indicatif = ""
                    for p in PAYS_INDICATIFS:
                        if f"{p['drapeau']} {p['pays']} ({p['indicatif']})" == selected_pays:
                            selected_indicatif = p['indicatif']
                            break
                
                with col2:
                    phone_local = st.text_input("Numéro de téléphone", placeholder="6 123 45 67", key="register_phone")
                    if phone_local and selected_indicatif:
                        full_phone = selected_indicatif + phone_local.replace(' ', '')
                        pays_info = get_pays_from_phone(full_phone)
                        if pays_info:
                            st.caption(f"📱 {pays_info['drapeau']} {full_phone}")
                
                password = st.text_input("Mot de passe", type="password")
                confirm = st.text_input("Confirmer", type="password")
                terms = st.checkbox("J'accepte les conditions générales")
                
                if st.form_submit_button("Créer mon compte", use_container_width=True):
                    if password == confirm and terms:
                        full_phone = selected_indicatif + phone_local.replace(' ', '') if phone_local else ""
                        ok, res = db.create_user(first_name, last_name, email, full_phone, password)
                        if ok:
                            st.success("Compte créé avec succès !")
                            st.balloons()
                        else:
                            st.error(f"Erreur : {res}")
                    else:
                        st.error("Vérifiez les informations")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DASHBOARD
# ============================================================
def dashboard_page():
    set_custom_theme()
    
    # Récupérer le pays de l'utilisateur
    user_country = ""
    if st.session_state.user.get('country_code'):
        for p in PAYS_INDICATIFS:
            if p['code'] == st.session_state.user['country_code']:
                user_country = f"{p['drapeau']} {p['pays']}"
                break
    
    st.markdown(f"""
    <div class="main-container animated-entry">
        <h1>👋 Bienvenue, {st.session_state.user.get('first_name', 'Utilisateur')} !</h1>
        <p>Voici votre tableau de bord personnalisé {user_country}</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = db.get_avi_stats(st.session_state.user['id'])
    unread = db.get_unread_messages_count(st.session_state.user['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Demandes AVI", stats['total'])
    with col2:
        st.metric("✅ Validées", stats['validated'])
    with col3:
        st.metric("⏳ En attente", stats['pending'])
    with col4:
        st.metric("💬 Messages", unread)
    
    st.markdown("## 📊 Activités Récentes")
    
    user_requests = db.get_user_avi_requests(st.session_state.user['id'])
    
    if user_requests:
        for req in user_requests[:5]:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <strong>{req['id']}</strong><br>
                    📅 {req['created_at'].strftime('%d/%m/%Y %H:%M')}<br>
                    💰 {req['request_data'].get('avi_amount', 'N/A')}<br>
                    <span style="color: {'orange' if req['status'] == 'En attente' else 'green' if req['status'] == 'Validée' else 'red'}">
                        {req['status']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucune activité récente")

# ============================================================
# PAGE DEMANDE AVI
# ============================================================
def avi_request_page():
    set_custom_theme()
    
    st.markdown("""
    <div class="main-container animated-entry">
        <h2>📋 Nouvelle Demande d'AVI</h2>
        <p>Attestation de Vérification d'Identité - Traitement sous 48h</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'avi_step' not in st.session_state:
        st.session_state.avi_step = 1
    
    steps = ["📝 Informations", "📎 Documents", "✅ Validation"]
    step = st.session_state.avi_step
    
    st.progress(step / 3)
    
    if step == 1:
        st.markdown('<div class="card-premium animate-fadeInLeft">', unsafe_allow_html=True)
        st.markdown("### 📝 Informations Personnelles")
        
        with st.form(key="avi_form_step1"):
            col1, col2 = st.columns(2)
            with col1:
                last_name = st.text_input("Nom *", placeholder="Votre nom de famille", key="avi_last_name")
                birth_date = st.date_input("Date de naissance *", 
                                          value=datetime.now() - timedelta(days=365*70), 
                                          max_value=datetime.now(), 
                                          key="avi_birth_date")
                nationality = st.text_input("Nationalité *", placeholder="Ex: Congolaise", key="avi_nationality")
            with col2:
                first_name = st.text_input("Prénom(s) *", placeholder="Votre prénom", key="avi_first_name")
                birth_place = st.text_input("Lieu de naissance *", placeholder="Ville de naissance", key="avi_birth_place")
            
            st.markdown("### 🏠 Adresse")
            col1, col2 = st.columns(2)
            with col1:
                address = st.text_input("Adresse *", placeholder="Votre adresse complète", key="avi_address")
                postal_code = st.text_input("Code postal *", placeholder="Code postal", key="avi_postal_code")
            with col2:
                city = st.text_input("Ville *", placeholder="Votre ville", key="avi_city")
                country = st.selectbox("Pays *", 
                                      ["Congo Brazzaville", "Chine", "Maroc", "Gabon", "Turquie", "Autre"], 
                                      index=0,
                                      key="avi_country")
            
            submitted = st.form_submit_button("Suivant ➡️", use_container_width=True)
            
            if submitted:
                last_name_val = st.session_state.get("avi_last_name", "")
                first_name_val = st.session_state.get("avi_first_name", "")
                birth_place_val = st.session_state.get("avi_birth_place", "")
                nationality_val = st.session_state.get("avi_nationality", "")
                address_val = st.session_state.get("avi_address", "")
                postal_code_val = st.session_state.get("avi_postal_code", "")
                city_val = st.session_state.get("avi_city", "")
                country_val = st.session_state.get("avi_country", "Congo Brazzaville")
                birth_date_val = st.session_state.get("avi_birth_date", datetime.now())
                
                missing_fields = []
                if not last_name_val or last_name_val.strip() == "":
                    missing_fields.append("Nom")
                if not first_name_val or first_name_val.strip() == "":
                    missing_fields.append("Prénom")
                if not birth_place_val or birth_place_val.strip() == "":
                    missing_fields.append("Lieu de naissance")
                if not nationality_val or nationality_val.strip() == "":
                    missing_fields.append("Nationalité")
                if not address_val or address_val.strip() == "":
                    missing_fields.append("Adresse")
                if not postal_code_val or postal_code_val.strip() == "":
                    missing_fields.append("Code postal")
                if not city_val or city_val.strip() == "":
                    missing_fields.append("Ville")
                
                if missing_fields:
                    st.error(f"⚠️ Champs manquants : {', '.join(missing_fields)}")
                else:
                    st.session_state.avi_data = {
                        'last_name': last_name_val.strip(),
                        'first_name': first_name_val.strip(),
                        'birth_date': birth_date_val.strftime('%Y-%m-%d'),
                        'birth_place': birth_place_val.strip(),
                        'nationality': nationality_val.strip(),
                        'address': address_val.strip(),
                        'postal_code': postal_code_val.strip(),
                        'city': city_val.strip(),
                        'country': country_val
                    }
                    st.session_state.avi_step = 2
                    st.rerun()
    
    elif step == 2:
        with st.container():
            st.markdown("### 📎 Pièces Justificatives")
            
            with st.form(key="avi_form_step2"):
                identity_doc = st.file_uploader("Pièce d'identité *", type=['jpg','jpeg','png','pdf'], key="avi_identity_doc")
                avi_amount = st.text_input("Montant AVI *", placeholder="500000 XAF", key="avi_amount")
                consent = st.checkbox("Je certifie l'exactitude des informations *", key="avi_consent")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    prev_clicked = st.form_submit_button("⬅️ Précédent")
                with col3:
                    next_clicked = st.form_submit_button("Suivant ➡️")
                
                if prev_clicked:
                    st.session_state.avi_step = 1
                    st.rerun()
                
                if next_clicked:
                    avi_amount_val = st.session_state.get("avi_amount", "")
                    identity_doc_val = st.session_state.get("avi_identity_doc", None)
                    consent_val = st.session_state.get("avi_consent", False)
                    
                    if identity_doc_val and avi_amount_val and consent_val:
                        file_data = identity_doc_val.read()
                        db.save_document(st.session_state.user['id'], identity_doc_val.name, file_data, identity_doc_val.type)
                        st.session_state.avi_data['avi_amount'] = avi_amount_val
                        st.session_state.avi_step = 3
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")
    
    elif step == 3:
        with st.container():
            st.markdown("### ✅ Validation Finale")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nom:** {st.session_state.avi_data.get('first_name', '')} {st.session_state.avi_data.get('last_name', '')}")
                st.write(f"**Date naissance:** {st.session_state.avi_data.get('birth_date', '')}")
                st.write(f"**Lieu naissance:** {st.session_state.avi_data.get('birth_place', '')}")
                st.write(f"**Nationalité:** {st.session_state.avi_data.get('nationality', '')}")
            with col2:
                st.write(f"**Adresse:** {st.session_state.avi_data.get('address', '')}")
                st.write(f"**Code postal:** {st.session_state.avi_data.get('postal_code', '')}")
                st.write(f"**Ville:** {st.session_state.avi_data.get('city', '')}")
                st.write(f"**Pays:** {st.session_state.avi_data.get('country', '')}")
                st.write(f"**Montant:** {st.session_state.avi_data.get('avi_amount', '')}")
            
            with st.form(key="avi_form_step3"):
                final_consent = st.checkbox("Je confirme les informations", key="avi_final_consent")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    prev_clicked = st.form_submit_button("⬅️ Précédent")
                with col3:
                    submit_clicked = st.form_submit_button("📤 Soumettre")
                
                if prev_clicked:
                    st.session_state.avi_step = 2
                    st.rerun()
                
                if submit_clicked:
                    if final_consent:
                        ok, ref = db.create_avi_request(st.session_state.user['id'], st.session_state.user['email'], st.session_state.avi_data)
                        if ok:
                            st.success(f"✅ Demande {ref} soumise avec succès !")
                            st.balloons()
                            st.session_state.avi_step = 1
                            st.session_state.avi_data = {}
                            keys_to_clear = ["avi_last_name", "avi_first_name", "avi_birth_place", "avi_nationality", 
                                            "avi_address", "avi_postal_code", "avi_city", "avi_birth_date", "avi_country",
                                            "avi_amount", "avi_identity_doc", "avi_consent", "avi_final_consent"]
                            for key in keys_to_clear:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error(f"❌ Erreur: {ref}")
                    else:
                        st.error("⚠️ Veuillez confirmer les informations")

# ============================================================
# PAGE MES AVI
# ============================================================
def my_avi_page():
    set_custom_theme()
    
    st.markdown("""
    <div class="animate-fadeInDown" style="margin-bottom: 2rem;">
        <h2 style="font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            📋 Mes Demandes d'AVI
        </h2>
        <p style="color: #718096; font-weight: 300;">
            Historique complet de vos attestations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📝 Demandes soumises")
    user_requests = db.get_user_avi_requests(st.session_state.user['id'])
    
    if not user_requests:
        st.info("📭 Aucune demande trouvée. Créez votre première demande !")
        if st.button("➕ Nouvelle Demande", use_container_width=True):
            st.session_state.avi_step = 1
            st.session_state.menu = "Demande AVI"
            st.rerun()
    else:
        for i, req in enumerate(user_requests):
            status_color = {'En attente': '#ed8936', 'Validée': '#48bb78', 'Rejetée': '#f56565'}.get(req['status'], '#a0aec0')
            status_emoji = {'En attente': '⏳', 'Validée': '✅', 'Rejetée': '❌'}.get(req['status'], '📋')
            
            with st.expander(f"{status_emoji} {req['id']} - {req['created_at'].strftime('%d/%m/%Y')}"):
                st.markdown(f"""
                **Statut:** {req['status']}
                **Date:** {req['created_at'].strftime('%d/%m/%Y %H:%M')}
                **Montant:** {req['request_data'].get('avi_amount', 'N/A')}
                """)
                
                if req['status'] == 'Validée' and req.get('request_data', {}).get('avi_amount'):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.info("✅ Votre demande a été validée. Vous recevrez votre attestation sous 48h.")
    
    st.markdown("---")
    st.markdown("### 📄 Attestations AVI Générées")

    user_avis = db.get_user_avis(st.session_state.user['id'])

    if not user_avis:
        st.info("📭 Aucune attestation AVI n'a encore été générée pour vous")
    else:
        def montant_en_lettres(montant):
            try:
                partie_entiere = int(montant)
                partie_decimale = int(round((montant - partie_entiere) * 100))
                texte = num2words(partie_entiere, lang='fr')
                if partie_entiere > 1:
                    texte += " francs CFA"
                else:
                    texte += " franc CFA"
                if partie_decimale > 0:
                    texte += " et " + num2words(partie_decimale, lang='fr') + " centimes"
                return texte.capitalize()
            except:
                return f"{montant:,.2f} francs CFA"
        
        def generate_avi_pdf(avi_data):
            try:
                pdf = FPDF()
                pdf.add_page()
                
                try:
                    logo_path = "assets/logo.png"
                    if os.path.exists(logo_path):
                        img = Image.open(logo_path)
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        data = img.getdata()
                        new_data = []
                        for item in data:
                            new_data.append((item[0], item[1], item[2], int(item[3] * 0.2)))
                        img.putdata(new_data)
                        temp_logo = BytesIO()
                        img.save(temp_logo, format='PNG')
                        temp_logo.seek(0)
                        for position in [(30, 30), (120, 200), (50, 300), (100, 100)]:
                            pdf.image(temp_logo, x=position[0], y=position[1], w=100)
                except:
                    pass
                
                pdf.set_font('Arial', 'B', 16)
                pdf.cell(0, 30, 'ATTESTATION DE VIREMENT IRREVOCABLE', 0, 1, 'C')
                
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 0, f"DGF/EC-{avi_data.get('reference', 'N/A')}", 0, 1, 'C')
                pdf.ln(10)
                
                try:
                    if os.path.exists("assets/logo.png"):
                        pdf.image("assets/logo.png", x=10, y=10, w=30)
                except:
                    pass
                
                pdf.set_font('Arial', '', 12)
                intro = [
                    "Nous soussignés, Eco Capital (E.C), établissement de microfinance agréé pour exercer des",
                    "activités bancaires en République du Congo conformément au décret n°7236/MEFB-CAB du",
                    "15 novembre 2007, après avis conforme de la COBAC D-2007/2018, déclarons avoir notre",
                    "siège au n°1636 Boulevard Denis Sassou Nguesso, Batignol Brazzaville.",
                    "",
                    "Représenté par son Directeur Général, Monsieur ILOKO Charmant.",
                    "",
                    f"Nous certifions par la présente que Monsieur/Madame {avi_data.get('nom_complet', 'N/A')}",
                    "détient un compte courant enregistré dans nos livres avec les caractéristiques suivantes :",
                    ""
                ]
                
                for line in intro:
                    pdf.cell(0, 5, line, 0, 1)
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(40, 5, "CODE BANQUE :", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 5, avi_data.get('code_banque', 'N/A'), 0, 1)
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(45, 5, "NUMERO COMPTE : ", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 5, avi_data.get('numero_compte', 'N/A'), 0, 1)
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(20, 5, "Devise :", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 5, avi_data.get('devise', 'XAF'), 0, 1)
                pdf.ln(5)
                
                montant = avi_data.get('montant', 0)
                try:
                    montant_float = float(montant) if montant else 0
                except:
                    montant_float = 0
                
                details = [
                    f"Il est l'ordonnateur d'un virement irrévocable et permanent d'un montant total de {montant_float:,.2f} FCFA",
                    f"({montant_en_lettres(montant_float)}), équivalant actuellement à {montant_float/650:,.2f} euros,",
                    "destiné à couvrir les frais liés à ses études en France.",
                    "",
                    "Il est précisé que ce compte demeurera bloqué jusqu'à la présentation, par le donneur",
                    "d'ordre, de ses nouvelles coordonnées bancaires ouvertes en France.",
                    "",
                    "À défaut, les fonds ne pourront être remis à sa disposition qu'après présentation de son",
                    "passeport attestant d'un refus de visa. Toutefois, nous autorisons le donneur d'ordre, à",
                    "toutes fins utiles, à utiliser notre compte ouvert auprès de United Bank for Africa (UBA).",
                    ""
                ]
                
                for line in details:
                    pdf.cell(0, 5, line, 0, 1)
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(16, 5, "IBAN :", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 5, avi_data.get('iban', 'N/A'), 0, 1)
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(16, 5, "BIC :", 0, 0)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 5, avi_data.get('bic', 'N/A'), 0, 1)
                pdf.ln(10)
                
                pdf.cell(0, 5, "En foi de quoi, cette attestation lui est délivrée pour servir et valoir ce que de droit.", 0, 1)
                pdf.ln(10)
                
                date_val = avi_data.get('date_creation')
                if date_val:
                    if hasattr(date_val, 'strftime'):
                        date_str = date_val.strftime('%d %B %Y')
                    else:
                        date_str = str(date_val)
                else:
                    date_str = datetime.now().strftime('%d %B %Y')
                
                pdf.cell(0, 5, f"Fait à Brazzaville, le {date_str}", 0, 1, 'R')
                pdf.ln(5)
                
                pdf.cell(0, 5, "Rubain MOUNGALA", 0, 1)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 5, "Directeur de la Gestion Financière", 0, 1)
                pdf.ln(15)
                
                footer = [
                    "Eco capital Sarl",
                    "Société a responsabilité limité au capital de 60.000.000 XAF",
                    "Siège social : 1636 Boulevard Denis Sassou Nguesso Brazzaville",
                    "Contact: 00242 06 931 31 06 /04 001 79 40",
                    "Web : www.ecocapitale.com mail : contacts@ecocapitale.com",
                    "RCCM N°CG/BZV/B12-00320NIU N°M24000000665934H",
                    "Brazzaville République du Congo"
                ]
                
                pdf.set_font('Arial', 'I', 10)
                for line in footer:
                    pdf.cell(1, 4.5, line, 0, 1, 'L')
                
                try:
                    qr_data = {
                        "Référence": avi_data.get('reference', 'N/A'),
                        "Nom": avi_data.get('nom_complet', 'N/A'),
                        "Code Banque": avi_data.get('code_banque', 'N/A'),
                        "Numéro Compte": avi_data.get('numero_compte', 'N/A'),
                        "BIC": avi_data.get('bic', 'N/A'),
                        "Montant": f"{montant_float:,.2f} FCFA",
                        "Date Création": date_str
                    }
                    
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=2)
                    qr.add_data(str(qr_data))
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    pdf.image(img_bytes, x=150, y=pdf.get_y() - 40, w=40)
                except:
                    pass
                
                try:
                    output = pdf.output()
                    if isinstance(output, str):
                        output = output.encode('latin1')
                except TypeError:
                    output = pdf.output(dest='S')
                    if isinstance(output, str):
                        output = output.encode('latin1')
                
                return output
                    
            except Exception as e:
                print(f"Erreur generate_avi_pdf: {e}")
                return None
        
        for i, avi in enumerate(user_avis):
            reference = avi.get('reference', 'N/A') if avi.get('reference') else f'AVI_{i+1}'
            nom_complet = avi.get('nom_complet', 'Bénéficiaire non spécifié')
            
            try:
                montant_val = float(avi.get('montant', 0)) if avi.get('montant') else 0
                montant_display = f"{montant_val:,.2f} FCFA"
            except (ValueError, TypeError):
                montant_display = f"{avi.get('montant', 0)} FCFA"
            
            with st.expander(f"📄 {reference} - {nom_complet} - {montant_display}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **👤 Informations du bénéficiaire:**
                    - Nom complet: **{avi.get('nom_complet', 'N/A')}**
                    - Code Banque: **{avi.get('code_banque', 'N/A')}**
                    - Numéro de compte: **{avi.get('numero_compte', 'N/A')}**
                    - Devise: **{avi.get('devise', 'XAF')}**
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📄 Détails de l'attestation:**
                    - Référence: **{reference}**
                    - IBAN: **{avi.get('iban', 'N/A')}**
                    - BIC: **{avi.get('bic', 'N/A')}**
                    - Montant: **{montant_display}**
                    - Statut: **{avi.get('statut', 'N/A')}**
                    - Date d'émission: **{avi.get('date_creation').strftime('%d/%m/%Y') if avi.get('date_creation') else 'Date inconnue'}**
                    """)
                
                if avi.get('commentaires'):
                    st.markdown(f"**📝 Commentaires:** {avi.get('commentaires')}")
                
                st.markdown("---")
                
                try:
                    pdf_bytes = generate_avi_pdf(avi)
                    if pdf_bytes:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label=f"📥 Télécharger l'attestation {reference}",
                                data=pdf_bytes,
                                file_name=f"AVI_{reference}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"download_{reference}_{i}"
                            )
                    else:
                        st.error(f"Impossible de générer le PDF pour {reference}")
                except Exception as e:
                    st.error(f"Erreur lors de la génération du PDF: {str(e)}")

# ============================================================
# PAGE MESSAGES
# ============================================================
def messages_page():
    set_custom_theme()
    
    st.markdown("""
    <style>
    .message-sent-premium {
        background: linear-gradient(135deg, #4a6fa5, #166088);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .message-received-premium {
        background: #f0f0f0;
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .attachment-preview {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(0,0,0,0.05);
        border-radius: 8px;
        display: inline-block;
    }
    
    @media (prefers-color-scheme: dark) {
        .message-received-premium {
            background: #2d2d44;
            color: #f0f2f6;
        }
        .attachment-preview {
            background: rgba(255,255,255,0.1);
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="animate-fadeInDown" style="margin-bottom: 2rem;">
        <h2 style="font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            💬 Centre de Messages
        </h2>
        <p style="color: #718096; font-weight: 300;">
            Communiquez directement avec notre équipe support et partagez des documents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📋 Conversations")
        
        conversations = db.get_user_conversations(st.session_state.user['id'])
        
        if not conversations or all(conv is None for conv in conversations):
            default_conversations = ["Support Technique", "Service AVI", "Comptabilité"]
            for name in default_conversations:
                db.create_conversation(st.session_state.user['id'], name)
            conversations = db.get_user_conversations(st.session_state.user['id'])
        
        valid_conversations = []
        for conv in conversations:
            if conv is not None and isinstance(conv, dict):
                if 'name' in conv:
                    valid_conversations.append(conv)
                else:
                    conv['name'] = f"Conversation {conv.get('id', '')[:8]}"
                    conv['last_message'] = conv.get('last_message', 'Nouvelle conversation')
                    conv['unread_count'] = conv.get('unread_count', 0)
                    valid_conversations.append(conv)
        
        if valid_conversations:
            for conv in valid_conversations:
                conv_name = conv.get('name', 'Conversation')
                conv_last_message = conv.get('last_message', 'Nouvelle conversation')
                conv_unread_count = conv.get('unread_count', 0)
                
                if conv_last_message is None:
                    conv_last_message = 'Nouvelle conversation'
                elif not isinstance(conv_last_message, str):
                    conv_last_message = str(conv_last_message)
                
                last_message_preview = conv_last_message[:50] if len(conv_last_message) > 50 else conv_last_message
                badge = f'<span style="background: #ef4444; color: white; border-radius: 50%; padding: 0.2rem 0.5rem; font-size: 0.7rem;">{conv_unread_count}</span>' if conv_unread_count > 0 else ""
                
                st.markdown(f"""
                <div style="padding: 1rem; margin-bottom: 0.5rem; border-radius: 12px; background: white;">
                    <strong>{conv_name}</strong> {badge}
                    <br>
                    <small style="color: #718096;">{last_message_preview}...</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💬 Aucune conversation disponible")
    
    with col2:
        st.markdown("### 💭 Support Technique")
        
        user_messages = db.get_user_messages_with_attachments(st.session_state.user['id'])
        
        if user_messages:
            for msg in user_messages:
                if msg and isinstance(msg, dict):
                    sender = msg.get('sender', 'user')
                    content = msg.get('content', 'Message vide')
                    timestamp = msg.get('timestamp', datetime.now())
                    timestamp_str = timestamp.strftime('%d/%m %H:%M') if hasattr(timestamp, 'strftime') else str(timestamp)
                    attachment = msg.get('attachment')
                    attachment_filename = msg.get('attachment_filename', '')
                    
                    if sender == 'user':
                        st.markdown(f"""
                        <div class="message-sent-premium">
                            <strong>👤 Vous</strong>
                            <p style="margin: 0.5rem 0;">{content}</p>
                        """, unsafe_allow_html=True)
                        
                        if attachment and attachment_filename:
                            file_ext = attachment_filename.split('.')[-1].lower() if '.' in attachment_filename else ''
                            
                            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                try:
                                    import base64
                                    img_data = base64.b64encode(attachment).decode('utf-8')
                                    st.markdown(f"""
                                    <div class="attachment-preview">
                                        <img src="data:image/{file_ext};base64,{img_data}" style="max-width: 200px; max-height: 150px; border-radius: 8px;">
                                        <br>
                                        <small>📎 {attachment_filename}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                except:
                                    st.markdown(f'<div class="attachment-preview">📎 {attachment_filename}</div>', unsafe_allow_html=True)
                            else:
                                st.download_button(
                                    label=f"📎 Télécharger {attachment_filename}",
                                    data=attachment,
                                    file_name=attachment_filename,
                                    mime="application/octet-stream",
                                    key=f"download_{msg.get('id', '')}"
                                )
                        
                        st.markdown(f"""
                            <small style="opacity: 0.8;">📅 {timestamp_str}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="message-received-premium">
                            <strong>🏦 Support</strong>
                            <p style="margin: 0.5rem 0;">{content}</p>
                        """, unsafe_allow_html=True)
                        
                        if attachment and attachment_filename:
                            file_ext = attachment_filename.split('.')[-1].lower() if '.' in attachment_filename else ''
                            
                            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                try:
                                    import base64
                                    img_data = base64.b64encode(attachment).decode('utf-8')
                                    st.markdown(f"""
                                    <div class="attachment-preview">
                                        <img src="data:image/{file_ext};base64,{img_data}" style="max-width: 200px; max-height: 150px; border-radius: 8px;">
                                        <br>
                                        <small>📎 {attachment_filename}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                except:
                                    st.markdown(f'<div class="attachment-preview">📎 {attachment_filename}</div>', unsafe_allow_html=True)
                            else:
                                st.download_button(
                                    label=f"📎 Télécharger {attachment_filename}",
                                    data=attachment,
                                    file_name=attachment_filename,
                                    mime="application/octet-stream",
                                    key=f"download_support_{msg.get('id', '')}"
                                )
                        
                        st.markdown(f"""
                            <small style="opacity: 0.8;">📅 {timestamp_str}</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("💬 Aucun message pour le moment. Commencez une conversation !")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("send_msg", clear_on_submit=True):
            msg_text = st.text_area("Message", placeholder="Écrivez votre message ici...", height=80)
            
            uploaded_file = st.file_uploader(
                "📎 Joindre un fichier (optionnel)",
                type=['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'],
                help="Vous pouvez joindre des documents, images, PDF, etc."
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("📤 Envoyer", use_container_width=True)
            
            if submitted:
                if not msg_text.strip() and not uploaded_file:
                    st.warning("Veuillez écrire un message ou joindre un fichier.")
                else:
                    if uploaded_file:
                        file_bytes = uploaded_file.read()
                        filename = uploaded_file.name
                        file_type = uploaded_file.type
                        
                        success, result = db.send_message_with_attachment(
                            st.session_state.user['id'], 
                            'user', 
                            msg_text if msg_text.strip() else "[Message avec pièce jointe]", 
                            file_bytes, 
                            filename, 
                            file_type
                        )
                    else:
                        success, result = db.send_message(st.session_state.user['id'], 'user', msg_text)
                    
                    if success:
                        st.success("Message envoyé avec succès !")
                        st.rerun()
                    else:
                        st.error(f"Erreur lors de l'envoi : {result}")

# ============================================================
# MAIN
# ============================================================
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'menu' not in st.session_state:
        st.session_state.menu = "Dashboard"
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 0

    # Si l'utilisateur demande la page de réinitialisation
    if st.session_state.get('show_forgot_password', False) or st.session_state.reset_step > 0:
        forgot_password_page()
        return

    if not st.session_state.logged_in:
        auth_page()
        return

    set_custom_theme()
    
    with st.sidebar:
        # Afficher le pays de l'utilisateur dans la sidebar
        user_country_display = ""
        if st.session_state.user.get('country_code'):
            for p in PAYS_INDICATIFS:
                if p['code'] == st.session_state.user['country_code']:
                    user_country_display = f"{p['drapeau']} {p['pays']}"
                    break
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 15px; color: white;">
            <div style="font-size: 3rem;">👤</div>
            <h4>{st.session_state.user.get('first_name', '')} {st.session_state.user.get('last_name', '')}</h4>
            <small>{st.session_state.user.get('email', '')}</small>
            <br>
            <small>{user_country_display}</small>
        </div>
        """, unsafe_allow_html=True)
        
        menu = option_menu(
            None,
            ["Dashboard", "Demande AVI", "Mes AVI", "Messages", "Déconnexion"],
            icons=["speedometer2", "file-text", "folder-check", "chat-dots", "box-arrow-right"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "#4a6fa5", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "margin": "5px 0", "border-radius": "10px"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #4a6fa5, #166088)"},
            }
        )
        
        if menu == "Déconnexion":
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        
        st.session_state.menu = menu

    pages = {
        "Dashboard": dashboard_page,
        "Demande AVI": avi_request_page,
        "Mes AVI": my_avi_page,
        "Messages": messages_page,
    }
    
    pages.get(st.session_state.menu, dashboard_page)()

if __name__ == "__main__":
    main()
