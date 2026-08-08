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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# ============================================================
# CONFIGURATION EMAIL (MAILTRAP - ENVIRONNEMENT DE TEST)
# ============================================================
# Inscrivez-vous sur https://mailtrap.io/ et créez un compte
# Récupérez vos identifiants dans la section "SMTP Settings"
#EMAIL_CONFIG = {
#    'smtp_server': 'live.smtp.mailtrap.io',  # Serveur Mailtrap
#    'smtp_port': 587,  # Port Mailtrap (ou 587 selon votre plan)
#    'smtp_username': 'api',  # À remplacer
#    'smtp_password': 'dba914abfb2e8ee4d29c63c84e62ce16',  # À remplacer
#    'from_email': 'noreply@demomailtrap.com',
#    'from_name': 'EcoCapital - Support'
#}

# ============================================================
# FONCTIONS D'ENVOI D'EMAIL AVEC MAILTRAP
# ============================================================
#def send_email(to_email, subject, html_content, text_content=""):
#    """Envoie un email via Mailtrap (environnement de test)"""
#    try:
        # Créer le message
#        msg = MIMEMultipart('alternative')
#        msg['Subject'] = subject
#        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
#        msg['To'] = to_email
        
        # Ajouter les versions texte et HTML
#        if text_content:
#            part_text = MIMEText(text_content, 'plain')
#            msg.attach(part_text)
#        
#        part_html = MIMEText(html_content, 'html')
#        msg.attach(part_html)
        
        # Connexion au serveur Mailtrap
#        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
#            server.starttls()
#            server.login(EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'])
#            server.send_message(msg)
        
#        print(f"✅ Email envoyé à {to_email} via Mailtrap")
#        return True, "Email envoyé avec succès (via Mailtrap)"
        
#    except Exception as e:
#        print(f"❌ Erreur d'envoi d'email via Mailtrap: {e}")
#        return False, str(e)
import requests

# ============================================================
# CONFIGURATION API MAILTRAP
# ============================================================
MAILTRAP_API_KEY = "dba914abfb2e8ee4d29c63c84e62ce16"  # Récupérez dans Email Sending -> API
MAILTRAP_INBOX_ID = "2807750"  # Récupérez dans l'URL de votre inbox

def send_email_api(to_email, subject, html_content, text_content=""):
    """Envoie un email via l'API Mailtrap (recommandé)"""
    try:
        url = f"https://send.api.mailtrap.io/api/send"
        
        headers = {
            "Authorization": f"Bearer {MAILTRAP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": {
                "email": "noreply@demomailtrap.com",
                "name": "EcoCapital - Support"
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "html": html_content,
            "text": text_content or html_content.replace('<br>', '\n').replace('</p>', '\n').replace('<p>', '').replace('</div>', '')
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Email envoyé à {to_email} via API Mailtrap")
            return True, "Email envoyé avec succès"
        else:
            error_msg = response.json().get('error', {}).get('message', 'Erreur inconnue')
            print(f"❌ Erreur API Mailtrap: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email: {e}")
        return False, str(e)
        
def send_reset_password_email(email, token, user_name=""):
    """Envoie l'email de réinitialisation du mot de passe via Mailtrap"""
    # Construction du lien de réinitialisation
    base_url = "https://ecocapitales-client.streamlit.app"  # À adapter selon votre URL
    reset_link = f"{base_url}?reset_token={token}"
    
    # Contenu HTML de l'email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
            }}
            .header {{
                background: linear-gradient(135deg, #4a6fa5, #166088);
                color: white;
                padding: 30px 20px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .header p {{
                margin: 10px 0 0;
                opacity: 0.9;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 10px 10px;
                border: 1px solid #e0e0e0;
                border-top: none;
            }}
            .button {{
                display: inline-block;
                padding: 14px 35px;
                background: linear-gradient(135deg, #4a6fa5, #166088);
                color: white !important;
                text-decoration: none;
                border-radius: 8px;
                margin: 20px 0;
                font-weight: bold;
                text-align: center;
            }}
            .button:hover {{
                background: linear-gradient(135deg, #3a5a8f, #0d4b6e);
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
                font-size: 14px;
            }}
            .info-box {{
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
                font-size: 14px;
            }}
            .link-box {{
                background: #f0f0f0;
                padding: 12px;
                border-radius: 4px;
                word-break: break-all;
                font-size: 13px;
                font-family: monospace;
                margin: 10px 0;
            }}
            .logo-text {{
                font-size: 28px;
                font-weight: bold;
                color: #4a6fa5;
            }}
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #1a1a2e;
                }}
                .content {{
                    background: #1e2130;
                    color: #f0f2f6;
                    border-color: #2d2d44;
                }}
                .link-box {{
                    background: #2d2d44;
                }}
                .info-box {{
                    background: #1a2a3a;
                    border-left-color: #4a6fa5;
                }}
                .warning {{
                    background: #2a2a1a;
                    border-left-color: #ffc107;
                }}
                .footer {{
                    border-top-color: #2d2d44;
                    color: #999;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔑 Réinitialisation de mot de passe</h1>
            <p>EcoCapital - Votre Partenaire Financier de Confiance</p>
        </div>
        <div class="content">
            <p><strong>Bonjour {user_name},</strong></p>
            
            <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte EcoCapital.</p>
            
            <p>Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
            
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">🔐 Réinitialiser mon mot de passe</a>
            </div>
            
            <div class="warning">
                ⚠️ <strong>Ce lien expirera dans 24 heures.</strong><br>
                Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
            </div>
            
            <div class="info-box">
                💡 <strong>Conseil de sécurité :</strong><br>
                Utilisez un mot de passe d'au moins 8 caractères avec une majuscule, une minuscule et un chiffre.
            </div>
            
            <p>Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :</p>
            <div class="link-box">
                {reset_link}
            </div>
            
            <p>Pour toute question, n'hésitez pas à contacter notre équipe support à l'adresse : <strong>support@ecocapital.com</strong></p>
            
            <p style="margin-top: 20px;">
                Cordialement,<br>
                <strong>L'équipe EcoCapital</strong>
            </p>
            
            <div style="text-align: center; margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    🌍 <strong>EcoCapital</strong> - Votre Partenaire Financier de Confiance
                </p>
            </div>
        </div>
        <div class="footer">
            <p>Cet email a été envoyé automatiquement, veuillez ne pas y répondre.</p>
            <p>© 2024 EcoCapital. Tous droits réservés.</p>
            <p style="margin-top: 10px; font-size: 11px; color: #999;">
                Ce message est confidentiel et destiné uniquement à la personne ou à l'entité à laquelle il est adressé.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Version texte pour les clients qui ne supportent pas HTML
    text_content = f"""
    Réinitialisation de mot de passe - EcoCapital
    
    Bonjour {user_name},
    
    Vous avez demandé la réinitialisation de votre mot de passe pour votre compte EcoCapital.
    
    Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :
    {reset_link}
    
    ⚠️ Ce lien expirera dans 24 heures.
    Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
    
    Conseils de sécurité :
    - Utilisez un mot de passe d'au moins 8 caractères
    - Incluez une majuscule, une minuscule et un chiffre
    
    Pour toute question, contactez-nous à support@ecocapital.com
    
    Cordialement,
    L'équipe EcoCapital
    """
    
    return send_email(email, "🔑 Réinitialisation de votre mot de passe EcoCapital", html_content, text_content)

def send_password_changed_notification(email, user_name=""):
    """Envoie une notification de changement de mot de passe via Mailtrap"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
            }}
            .header {{
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                padding: 30px 20px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 10px 10px;
                border: 1px solid #e0e0e0;
                border-top: none;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }}
            .success-box {{
                background: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }}
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #1a1a2e;
                }}
                .content {{
                    background: #1e2130;
                    color: #f0f2f6;
                    border-color: #2d2d44;
                }}
                .warning {{
                    background: #2a2a1a;
                    border-left-color: #ffc107;
                }}
                .success-box {{
                    background: #1a3a2a;
                    border-left-color: #28a745;
                }}
                .footer {{
                    border-top-color: #2d2d44;
                    color: #999;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✅ Mot de passe modifié</h1>
            <p>EcoCapital - Votre Partenaire Financier de Confiance</p>
        </div>
        <div class="content">
            <p><strong>Bonjour {user_name},</strong></p>
            
            <div class="success-box">
                ✅ Votre mot de passe a été modifié avec succès.
            </div>
            
            <div class="warning">
                ⚠️ <strong>Important :</strong> Si vous n'êtes pas à l'origine de cette modification, <strong>contactez immédiatement</strong> notre support client à support@ecocapital.com ou par téléphone au +242 06 931 31 06.
            </div>
            
            <p>Pour toute question, n'hésitez pas à contacter notre équipe support.</p>
            
            <p style="margin-top: 20px;">
                Cordialement,<br>
                <strong>L'équipe EcoCapital</strong>
            </p>
        </div>
        <div class="footer">
            <p>Cet email a été envoyé automatiquement, veuillez ne pas y répondre.</p>
            <p>© 2024 EcoCapital. Tous droits réservés.</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Mot de passe modifié - EcoCapital
    
    Bonjour {user_name},
    
    ✅ Votre mot de passe a été modifié avec succès.
    
    ⚠️ Important : Si vous n'êtes pas à l'origine de cette modification, contactez immédiatement notre support client.
    
    Pour toute question, n'hésitez pas à contacter notre équipe support.
    
    Cordialement,
    L'équipe EcoCapital
    """
    
    return send_email(email, "✅ Votre mot de passe a été modifié", html_content, text_content)

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
        
        /* ===== ANIMATIONS ===== */
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
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
        
        h1, h2, h3, h4, h5, h6 {{
            animation: fadeIn 0.8s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stButton>button {{
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            transform: translateY(0);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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
        
        [data-testid="metric-container"] {{
            border-radius: 10px;
            padding: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
        
        @keyframes fadeInSlide {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .login-container {{
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            padding: 2em;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            color: white;
        }}
        
        .custom-card {{
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            border-left: 4px solid #4a6fa5;
            background-color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        @media (prefers-color-scheme: dark) {{
            .custom-card {{
                background-color: #1e2130;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                border-left: 4px solid #166088;
            }}
        }}
        
        .custom-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }}
        
        .forgot-password-link {{
            color: #ffffff !important;
            text-decoration: none !important;
            cursor: pointer;
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .forgot-password-link:hover {{
            text-decoration: underline !important;
            opacity: 1;
        }}
        
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
        
        .message-sent-premium {{
            background: linear-gradient(135deg, #4a6fa5, #166088);
            color: white;
            padding: 1rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            max-width: 80%;
            margin-left: auto;
        }}
        
        .message-received-premium {{
            background: #f0f0f0;
            color: #333;
            padding: 1rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            max-width: 80%;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .message-received-premium {{
                background: #2d2d44;
                color: #f0f2f6;
            }}
        }}
        
        .attachment-preview {{
            margin-top: 0.5rem;
            padding: 0.5rem;
            background: rgba(0,0,0,0.05);
            border-radius: 8px;
            display: inline-block;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .attachment-preview {{
                background: rgba(255,255,255,0.1);
            }}
        }}
        
        .reset-success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .reset-error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .reset-success {{
                background: #1e3a2f;
                border-color: #2d6a4f;
                color: #95d5b2;
            }}
            .reset-error {{
                background: #3a1e1e;
                border-color: #6a2d2d;
                color: #f5a3a3;
            }}
        }}
        
        .password-requirements {{
            font-size: 0.9rem;
            color: #666;
            margin: 5px 0;
            padding-left: 20px;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .password-requirements {{
                color: #aaa;
            }}
        }}
        
        .password-requirements li {{
            list-style: none;
        }}
        
        .password-requirements li:before {{
            content: "• ";
            color: #4a6fa5;
        }}
        
        .mailtrap-info {{
            background: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
            font-size: 14px;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .mailtrap-info {{
                background: #1a2a3a;
                border-color: #4a6fa5;
                color: #e3f2fd;
            }}
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
                    elif col_name == 'password':
                        if 'password' in existing_columns:
                            continue
                        self.cursor.execute(f"ALTER TABLE utilisateurs ADD COLUMN {col_name} {col_def} AFTER phone")
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
            
            # Table utilisateurs
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
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        PRIMARY KEY (id),
                        UNIQUE KEY uk_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            
            # Table password_resets
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    token VARCHAR(36) NOT NULL UNIQUE,
                    expiry_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used BOOLEAN DEFAULT FALSE,
                    INDEX idx_token (token),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Autres tables
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

    # ==================== GESTION DES MOTS DE PASSE ====================
    def create_password_reset_token(self, email):
        """Crée un token de réinitialisation de mot de passe"""
        try:
            # Vérifier si l'utilisateur existe
            user = self.get_user_by_email(email)
            if not user:
                return False, "Aucun compte trouvé avec cet email"
            
            # Générer un token unique
            token = str(uuid.uuid4())
            expiry = datetime.now() + timedelta(hours=24)
            
            # Supprimer les anciens tokens pour cet email
            self.cursor.execute(
                "DELETE FROM password_resets WHERE email = %s",
                (email,)
            )
            
            # Créer le nouveau token
            self.cursor.execute(
                """INSERT INTO password_resets 
                   (email, token, expiry_date, created_at) 
                   VALUES (%s, %s, %s, NOW())""",
                (email, token, expiry)
            )
            self.connection.commit()
            return True, token
        except Error as e:
            return False, str(e)

    def verify_reset_token(self, token):
        """Vérifie si un token de réinitialisation est valide"""
        try:
            self.cursor.execute(
                """SELECT email, expiry_date, used 
                   FROM password_resets 
                   WHERE token = %s AND used = FALSE 
                   AND expiry_date > NOW()""",
                (token,)
            )
            result = self.cursor.fetchone()
            if result:
                return True, result['email']
            return False, "Token invalide ou expiré"
        except Error as e:
            return False, str(e)

    def reset_password(self, token, new_password):
        """Réinitialise le mot de passe avec un token"""
        try:
            # Vérifier le token
            valid, email = self.verify_reset_token(token)
            if not valid:
                return False, email
            
            # Hasher le nouveau mot de passe
            hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Mettre à jour le mot de passe
            self.cursor.execute(
                "UPDATE utilisateurs SET password = %s WHERE email = %s",
                (hashed_pw, email)
            )
            
            # Marquer le token comme utilisé
            self.cursor.execute(
                "UPDATE password_resets SET used = TRUE WHERE token = %s",
                (token,)
            )
            
            self.connection.commit()
            return True, email
        except Error as e:
            return False, str(e)

    def update_password(self, user_id, current_password, new_password):
        """Met à jour le mot de passe d'un utilisateur connecté"""
        try:
            # Vérifier le mot de passe actuel
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Utilisateur non trouvé"
            
            current_hashed = hashlib.sha256(current_password.encode()).hexdigest()
            if user['password'] != current_hashed:
                return False, "Mot de passe actuel incorrect"
            
            # Hasher le nouveau mot de passe
            new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Mettre à jour
            self.cursor.execute(
                "UPDATE utilisateurs SET password = %s WHERE id = %s",
                (new_hashed, user_id)
            )
            self.connection.commit()
            return True, user['email']
        except Error as e:
            return False, str(e)

    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        try:
            self.cursor.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            return self.cursor.fetchone()
        except Error:
            return None

    # ==================== MÉTHODES EXISTANTES ====================
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

    def create_user(self, first_name, last_name, email, phone, password):
        try:
            user_id = str(uuid.uuid4())
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            
            existing = self.get_user_by_email(email)
            if existing:
                return False, "Cet email est déjà utilisé"
            
            self.cursor.execute(
                "INSERT INTO utilisateurs (id, first_name, last_name, email, phone, password) VALUES (%s,%s,%s,%s,%s,%s)",
                (user_id, first_name, last_name, email, phone, hashed_pw)
            )
            self.connection.commit()
            return True, user_id
        except Error as e:
            return False, str(e)

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
# PAGE MOT DE PASSE OUBLIÉ (VERSION COMPLÈTE ET CORRIGÉE)
# ============================================================
# ============================================================
# PAGE MOT DE PASSE OUBLIÉ (VERSION CORRIGÉE - SANS BOUTONS CONDITIONNELS)
# ============================================================
def forgot_password_page():
    """Page pour demander la réinitialisation du mot de passe"""
    set_custom_theme()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🔑 Mot de passe oublié</h1>
        <p style="color: rgba(255,255,255,0.9);">Recevez un lien de réinitialisation par email</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher les informations Mailtrap
    st.markdown("""
    <div class="mailtrap-info">
        <strong>📧 Envoi d'email via Mailtrap (Environnement de test)</strong><br>
        Les emails seront envoyés à votre boîte Mailtrap. 
        <a href="https://mailtrap.io/inboxes" target="_blank" style="color: #4a6fa5;">
            Cliquez ici pour voir vos emails
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Utiliser st.session_state pour stocker l'état du formulaire
        if 'reset_email_sent' not in st.session_state:
            st.session_state.reset_email_sent = False
        if 'reset_email' not in st.session_state:
            st.session_state.reset_email = ""
        if 'reset_token' not in st.session_state:
            st.session_state.reset_token = ""
        
        with st.form("forgot_password_form"):
            email = st.text_input("Email", placeholder="exemple@email.com", key="forgot_email_input")
            
            st.markdown("""
            <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 10px;">
                📧 Nous vous enverrons un lien pour réinitialiser votre mot de passe via Mailtrap.
            </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📧 Envoyer le lien de réinitialisation", use_container_width=True)
            
            if submitted:
                if email:
                    # Valider le format de l'email
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, email):
                        st.error("⚠️ Format d'email invalide.")
                        st.session_state.reset_email_sent = False
                    else:
                        # Créer le token
                        success, result = db.create_password_reset_token(email)
                        if success:
                            # Récupérer le nom de l'utilisateur
                            user = db.get_user_by_email(email)
                            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Utilisateur"
                            
                            # Envoyer l'email via Mailtrap
                            email_sent, message = send_reset_password_email(email, result, user_name)
                            
                            if email_sent:
                                st.session_state.reset_email_sent = True
                                st.session_state.reset_email = email
                                st.session_state.reset_token = result
                                st.success("✅ Un lien de réinitialisation a été envoyé à votre adresse email via Mailtrap.")
                                st.info("📧 Consultez votre boîte Mailtrap pour voir l'email : https://mailtrap.io/inboxes")
                                
                                # Afficher les détails de l'email pour le débogage
                                with st.expander("🔍 Détails de l'email (débogage)"):
                                    st.code(f"""
                                    À: {email}
                                    Sujet: 🔑 Réinitialisation de votre mot de passe EcoCapital
                                    Token: {result}
                                    Lien: https://ecocapitales-client.streamlit.app?reset_token={result}
                                    """)
                            else:
                                st.session_state.reset_email_sent = False
                                st.error(f"❌ Erreur lors de l'envoi de l'email via Mailtrap: {message}")
                                st.warning("Vérifiez vos identifiants Mailtrap dans la configuration.")
                        else:
                            st.session_state.reset_email_sent = False
                            st.error(f"❌ {result}")
                else:
                    st.session_state.reset_email_sent = False
                    st.warning("Veuillez saisir votre adresse email.")
        
        # Bouton de retour - TOUJOURS PRÉSENT, en dehors de toute condition
        if st.button("⬅️ Retour à la page de connexion", key="back_to_login_bottom"):
            # Réinitialiser les variables de session
            st.session_state.reset_email_sent = False
            st.session_state.reset_email = ""
            st.session_state.reset_token = ""
            st.session_state.page = "login"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE RÉINITIALISATION DU MOT DE PASSE
# ============================================================
def reset_password_page():
    """Page pour définir un nouveau mot de passe via token"""
    set_custom_theme()
    
    # Récupérer le token de l'URL
    query_params = st.query_params
    token = query_params.get("reset_token", [None])[0]
    
    if not token:
        st.error("❌ Token de réinitialisation manquant.")
        if st.button("⬅️ Retour à la connexion"):
            st.session_state.page = "login"
            st.rerun()
        return
    
    # Vérifier la validité du token
    valid, email = db.verify_reset_token(token)
    
    if not valid:
        st.error(f"❌ {email}")
        st.info("💡 Le lien a peut-être expiré. Faites une nouvelle demande de réinitialisation.")
        if st.button("⬅️ Retour à la connexion"):
            st.session_state.page = "login"
            st.rerun()
        return
    
    # Récupérer les infos de l'utilisateur
    user = db.get_user_by_email(email)
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else "Utilisateur"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🔐 Nouveau mot de passe</h1>
        <p style="color: rgba(255,255,255,0.9);">Bonjour {user_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("reset_password_form"):
            new_password = st.text_input("Nouveau mot de passe", type="password", placeholder="Min 8 caractères")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password", placeholder="Répétez le mot de passe")
            
            st.markdown("""
            <div class="password-requirements">
                <strong>Exigences :</strong>
                <ul>
                    <li>Minimum 8 caractères</li>
                    <li>Au moins une majuscule</li>
                    <li>Au moins un chiffre</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔑 Réinitialiser le mot de passe", use_container_width=True)
            
            if submitted:
                # Validation du mot de passe
                if not new_password:
                    st.error("⚠️ Veuillez saisir un mot de passe.")
                elif len(new_password) < 8:
                    st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères.")
                elif not re.search(r'[A-Z]', new_password):
                    st.error("⚠️ Le mot de passe doit contenir au moins une majuscule.")
                elif not re.search(r'[0-9]', new_password):
                    st.error("⚠️ Le mot de passe doit contenir au moins un chiffre.")
                elif new_password != confirm_password:
                    st.error("⚠️ Les mots de passe ne correspondent pas.")
                else:
                    success, result = db.reset_password(token, new_password)
                    if success:
                        # Envoyer une notification de changement de mot de passe via Mailtrap
                        send_password_changed_notification(email, user_name)
                        
                        st.success("✅ Mot de passe réinitialisé avec succès !")
                        st.balloons()
                        st.info("🔑 Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.")
                        if st.button("🔑 Aller à la connexion"):
                            st.session_state.page = "login"
                            st.rerun()
                    else:
                        st.error(f"❌ {result}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE MODIFICATION DU MOT DE PASSE (UTILISATEUR CONNECTÉ)
# ============================================================
def change_password_page():
    """Page pour modifier le mot de passe d'un utilisateur connecté"""
    set_custom_theme()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🔒 Changer mon mot de passe</h1>
        <p style="color: rgba(255,255,255,0.9);">Mettez à jour votre mot de passe en toute sécurité</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        with st.form("change_password_form"):
            current_password = st.text_input("Mot de passe actuel", type="password", placeholder="Votre mot de passe actuel")
            new_password = st.text_input("Nouveau mot de passe", type="password", placeholder="Min 8 caractères")
            confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password", placeholder="Répétez le nouveau mot de passe")
            
            st.markdown("""
            <div class="password-requirements">
                <strong>Exigences :</strong>
                <ul>
                    <li>Minimum 8 caractères</li>
                    <li>Au moins une majuscule</li>
                    <li>Au moins un chiffre</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔑 Changer le mot de passe", use_container_width=True)
            
            if submitted:
                # Validation
                if not current_password:
                    st.warning("Veuillez saisir votre mot de passe actuel.")
                elif not new_password:
                    st.warning("Veuillez saisir un nouveau mot de passe.")
                elif len(new_password) < 8:
                    st.warning("⚠️ Le nouveau mot de passe doit contenir au moins 8 caractères.")
                elif not re.search(r'[A-Z]', new_password):
                    st.warning("⚠️ Le nouveau mot de passe doit contenir au moins une majuscule.")
                elif not re.search(r'[0-9]', new_password):
                    st.warning("⚠️ Le nouveau mot de passe doit contenir au moins un chiffre.")
                elif new_password != confirm_password:
                    st.warning("⚠️ Les nouveaux mots de passe ne correspondent pas.")
                else:
                    # Mettre à jour le mot de passe
                    success, result = db.update_password(
                        st.session_state.user['id'],
                        current_password,
                        new_password
                    )
                    
                    if success:
                        # Envoyer une notification via Mailtrap
                        user_name = f"{st.session_state.user.get('first_name', '')} {st.session_state.user.get('last_name', '')}".strip() or "Utilisateur"
                        send_password_changed_notification(st.session_state.user['email'], user_name)
                        
                        st.success("✅ Mot de passe changé avec succès !")
                        st.balloons()
                        st.info("🔑 Votre mot de passe a été mis à jour.")
                    else:
                        st.error(f"❌ {result}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PAGE PARAMÈTRES DU COMPTE
# ============================================================
def account_settings_page():
    """Page des paramètres du compte avec option de changement de mot de passe"""
    set_custom_theme()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">⚙️ Paramètres du compte</h1>
        <p style="color: rgba(255,255,255,0.9);">Gérez vos informations personnelles et votre sécurité</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informations du compte
    st.markdown("### 👤 Informations personnelles")
    
    user = st.session_state.user
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Prénom:** {user.get('first_name', 'N/A')}")
        st.info(f"**Nom:** {user.get('last_name', 'N/A')}")
    
    with col2:
        st.info(f"**Email:** {user.get('email', 'N/A')}")
        st.info(f"**Téléphone:** {user.get('phone', 'Non renseigné')}")
    
    st.markdown("---")
    
    # Section sécurité
    st.markdown("### 🔒 Sécurité")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔑 Changer mon mot de passe", use_container_width=True):
            st.session_state.page = "change_password"
            st.rerun()
    
    with col2:
        st.info("💡 Nous vous recommandons de changer régulièrement votre mot de passe.")
    
    st.markdown("---")
    st.markdown("### 🗑️ Gestion du compte")
    
    if st.button("⚠️ Supprimer mon compte", use_container_width=True):
        st.warning("🚧 Cette fonctionnalité sera disponible prochainement.")

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
                
                # Lien "Mot de passe oublié"
                st.markdown("""
                <div style="text-align: right; margin: 5px 0;">
                    <a href="#" onclick="alert('Redirection vers la page de réinitialisation')" 
                       style="color: #ffffff; text-decoration: none; font-size: 0.9rem; opacity: 0.9;">
                        Mot de passe oublié ?
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                if st.form_submit_button("Se connecter", use_container_width=True):
                    if email and password:
                        user = db.authenticate_user(email, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success("Connexion réussie !")
                            st.rerun()
                        else:
                            st.error("Email ou mot de passe incorrect")
            
            # Bouton "Mot de passe oublié"
            if st.button("🔑 Mot de passe oublié ?", use_container_width=True):
                st.session_state.page = "forgot_password"
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
                phone = st.text_input("Téléphone")
                password = st.text_input("Mot de passe", type="password")
                confirm = st.text_input("Confirmer", type="password")
                terms = st.checkbox("J'accepte les conditions générales")
                
                if st.form_submit_button("Créer mon compte", use_container_width=True):
                    if password == confirm and terms:
                        ok, res = db.create_user(first_name, last_name, email, phone, password)
                        if ok:
                            st.success("Compte créé avec succès !")
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
    
    st.markdown(f"""
    <div class="main-container animated-entry">
        <h1>👋 Bienvenue, {st.session_state.user.get('first_name', 'Utilisateur')} !</h1>
        <p>Voici votre tableau de bord personnalisé</p>
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
    
    # Étape 1
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
    
    # Étape 2
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
    
    # Étape 3
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
                    output = pdf.output(dest='S')
                    if isinstance(output, str):
                        output = output.encode('latin1')
                    elif isinstance(output, bytearray):
                        output = bytes(output)
                    return output
                except Exception as e:
                    print(f"Erreur lors de la génération du PDF: {e}")
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        pdf.output(tmp.name)
                        with open(tmp.name, 'rb') as f:
                            pdf_data = f.read()
                        os.unlink(tmp.name)
                        return pdf_data
                    
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
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    # Gestion des pages d'authentification
    if not st.session_state.logged_in:
        query_params = st.query_params
        token = query_params.get("reset_token", [None])[0]
        
        if token:
            reset_password_page()
            return
        elif st.session_state.page == "forgot_password":
            forgot_password_page()
            return
        elif st.session_state.page == "change_password":
            st.session_state.page = "login"
            st.rerun()
        else:
            auth_page()
            return

    # Pages pour utilisateur connecté
    set_custom_theme()
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 15px; color: white;">
            <div style="font-size: 3rem;">👤</div>
            <h4>{st.session_state.user.get('first_name', '')} {st.session_state.user.get('last_name', '')}</h4>
            <small>{st.session_state.user.get('email', '')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu principal
        menu_options = ["Dashboard", "Demande AVI", "Mes AVI", "Messages", "Paramètres", "Déconnexion"]
        menu_icons = ["speedometer2", "file-text", "folder-check", "chat-dots", "gear", "box-arrow-right"]
        
        menu = option_menu(
            None,
            menu_options,
            icons=menu_icons,
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
            st.session_state.page = "login"
            st.rerun()
        
        st.session_state.menu = menu

    # Gestion des pages
    if st.session_state.page == "change_password":
        change_password_page()
        return
    
    pages = {
        "Dashboard": dashboard_page,
        "Demande AVI": avi_request_page,
        "Mes AVI": my_avi_page,
        "Messages": messages_page,
        "Paramètres": account_settings_page,
    }
    
    pages.get(st.session_state.menu, dashboard_page)()

if __name__ == "__main__":
    main()
