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
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

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
# FONCTIONS EMAIL (SIMULÉES POUR L'EXEMPLE)
# ============================================================
def send_reset_email(email, reset_code):
    """
    Envoie un email avec le code de réinitialisation
    À configurer avec un vrai serveur SMTP en production
    """
    try:
        # Configuration SMTP (à remplacer par vos vrais paramètres)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "votre.email@gmail.com"
        smtp_password = "votre_mot_de_passe"
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "EcoCapital - Réinitialisation de votre mot de passe"
        
        # Corps du message HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4a6fa5, #166088); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #4a6fa5; text-align: center; padding: 20px; background: white; border-radius: 10px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 EcoCapital</h1>
                    <p>Réinitialisation de votre mot de passe</p>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Vous avez demandé la réinitialisation de votre mot de passe. Voici votre code de confirmation :</p>
                    <div class="code">{reset_code}</div>
                    <p>Ce code est valable pendant 15 minutes.</p>
                    <p>Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 EcoCapital - Tous droits réservés</p>
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Envoi de l'email (désactivé pour l'exemple)
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(smtp_username, smtp_password)
        # server.send_message(msg)
        # server.quit()
        
        print(f"📧 Email envoyé à {email} avec le code {reset_code}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email: {e}")
        return False

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
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
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
        
        /* Tableaux */
        [data-testid="stDataFrame"] {{
            border-radius: 10px;
            animation: fadeInUp 0.6s ease-out;
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
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

        /* Password reset styles */
        .reset-container {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }}
        
        @media (prefers-color-scheme: dark) {{
            .reset-container {{
                background: #1e2130;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
        }}
        
        .reset-container h2 {{
            text-align: center;
            color: #4a6fa5;
            margin-bottom: 1.5rem;
        }}
        
        .reset-container .step-indicator {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
            position: relative;
        }}
        
        .reset-container .step {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
        }}
        
        .reset-container .step .circle {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #666;
            position: relative;
            z-index: 2;
        }}
        
        .reset-container .step .circle.active {{
            background: #4a6fa5;
            color: white;
        }}
        
        .reset-container .step .circle.completed {{
            background: #48bb78;
            color: white;
        }}
        
        .reset-container .step .label {{
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #666;
        }}
        
        .reset-container .step .label.active {{
            color: #4a6fa5;
            font-weight: bold;
        }}
        
        .reset-container .step .line {{
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            height: 3px;
            background: #e0e0e0;
            z-index: 1;
        }}
        
        .reset-container .step .line.active {{
            background: #4a6fa5;
        }}
        
        .reset-container .step .line.completed {{
            background: #48bb78;
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# CLASSE DATABASE (AVEC FONCTIONS DE RÉINITIALISATION)
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
                
                self.cursor.execute("SET SESSION wait_timeout = 28800")
                self.cursor.execute("SET SESSION interactive_timeout = 28800")
                
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
            'is_active': 'BOOLEAN DEFAULT TRUE',
            'reset_code': 'VARCHAR(10) NULL',
            'reset_code_expiry': 'TIMESTAMP NULL'
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
                        reset_code VARCHAR(10) NULL,
                        reset_code_expiry TIMESTAMP NULL,
                        PRIMARY KEY (id),
                        UNIQUE KEY uk_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            
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

    # ==================== FONCTIONS DE RÉINITIALISATION ====================
    
    def generate_reset_code(self, email):
        """Génère un code de réinitialisation pour un email"""
        try:
            # Vérifier si l'utilisateur existe
            self.cursor.execute("SELECT id, email FROM utilisateurs WHERE email = %s AND is_active = TRUE", (email,))
            user = self.cursor.fetchone()
            
            if not user:
                return False, "Aucun compte trouvé avec cet email"
            
            # Générer un code aléatoire de 6 chiffres
            reset_code = ''.join(random.choices(string.digits, k=6))
            
            # Définir l'expiration à 15 minutes
            expiry = datetime.now() + timedelta(minutes=15)
            
            # Mettre à jour l'utilisateur
            self.cursor.execute("""
                UPDATE utilisateurs 
                SET reset_code = %s, reset_code_expiry = %s 
                WHERE id = %s
            """, (reset_code, expiry, user['id']))
            
            self.connection.commit()
            
            # Envoyer l'email
            email_sent = send_reset_email(email, reset_code)
            
            if email_sent:
                return True, reset_code
            else:
                return False, "Erreur lors de l'envoi de l'email"
                
        except Error as e:
            return False, str(e)
    
    def verify_reset_code(self, email, code):
        """Vérifie si le code de réinitialisation est valide"""
        try:
            self.cursor.execute("""
                SELECT id, reset_code, reset_code_expiry 
                FROM utilisateurs 
                WHERE email = %s AND is_active = TRUE
            """, (email,))
            
            user = self.cursor.fetchone()
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            if not user.get('reset_code'):
                return False, "Aucun code de réinitialisation demandé"
            
            if user['reset_code'] != code:
                return False, "Code incorrect"
            
            # Vérifier si le code a expiré
            if user['reset_code_expiry'] < datetime.now():
                return False, "Le code a expiré. Veuillez en demander un nouveau."
            
            return True, user['id']
            
        except Error as e:
            return False, str(e)
    
    def reset_password(self, email, code, new_password):
        """Réinitialise le mot de passe"""
        try:
            # Vérifier le code
            valid, result = self.verify_reset_code(email, code)
            
            if not valid:
                return False, result
            
            user_id = result
            
            # Hasher le nouveau mot de passe
            hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Mettre à jour le mot de passe et effacer le code
            self.cursor.execute("""
                UPDATE utilisateurs 
                SET password = %s, reset_code = NULL, reset_code_expiry = NULL 
                WHERE id = %s
            """, (hashed_pw, user_id))
            
            self.connection.commit()
            
            return True, "Mot de passe réinitialisé avec succès"
            
        except Error as e:
            return False, str(e)

    # ==================== AUTRES FONCTIONS ====================
    
    def send_message_with_attachment(self, user_id, sender, content, file_bytes, filename, file_type):
        """Envoie un message avec pièce jointe"""
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
        """Récupère les messages d'un utilisateur avec leurs pièces jointes"""
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
            
            print(f"Recherche AVI pour: {user_first} {user_last}")
            
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
            
            print(f"AVI trouvées: {len(results)}")
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
# PAGE MOT DE PASSE OUBLIÉ
# ============================================================
def forgot_password_page():
    set_custom_theme()
    
    # Initialiser les étapes si nécessaire
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1
    if 'reset_email' not in st.session_state:
        st.session_state.reset_email = ""
    if 'reset_code' not in st.session_state:
        st.session_state.reset_code = ""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2rem;">🔐 Mot de passe oublié</h1>
        <p style="color: rgba(255,255,255,0.9);">Réinitialisez votre mot de passe en 3 étapes</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="reset-container">
        <div class="step-indicator">
            <div class="step">
                <div class="circle active">1</div>
                <div class="label active">Email</div>
            </div>
            <div class="step">
                <div class="circle">2</div>
                <div class="label">Code</div>
            </div>
            <div class="step">
                <div class="circle">3</div>
                <div class="label">Nouveau MDP</div>
            </div>
            <div class="line active" style="width: 100%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Étape 1 : Saisie de l'email
    if st.session_state.reset_step == 1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
            <h3 style="text-align: center; color: #4a6fa5;">📧 Saisissez votre email</h3>
            <p style="text-align: center; color: #666;">Nous vous enverrons un code de réinitialisation</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reset_email_form"):
            email = st.text_input("Email", placeholder="exemple@email.com", value=st.session_state.reset_email)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("⬅️ Retour à la connexion", use_container_width=True):
                    st.session_state.reset_step = 1
                    st.session_state.reset_email = ""
                    st.session_state.reset_code = ""
                    st.rerun()
            with col2:
                if st.form_submit_button("📧 Envoyer le code", use_container_width=True):
                    if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        success, result = db.generate_reset_code(email)
                        if success:
                            st.session_state.reset_email = email
                            st.session_state.reset_step = 2
                            st.success(f"✅ Un code a été envoyé à {email}")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
                    else:
                        st.error("Veuillez saisir une adresse email valide")
    
    # Étape 2 : Vérification du code
    elif st.session_state.reset_step == 2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
            <h3 style="text-align: center; color: #4a6fa5;">🔑 Vérification du code</h3>
            <p style="text-align: center; color: #666;">Un code à 6 chiffres a été envoyé à <strong>{st.session_state.reset_email}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reset_code_form"):
            code = st.text_input("Code de confirmation", placeholder="000000", max_chars=6)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("⬅️ Retour", use_container_width=True):
                    st.session_state.reset_step = 1
                    st.rerun()
            with col2:
                if st.form_submit_button("🔄 Renvoyer", use_container_width=True):
                    success, result = db.generate_reset_code(st.session_state.reset_email)
                    if success:
                        st.success("✅ Un nouveau code a été envoyé")
                    else:
                        st.error(f"❌ {result}")
            with col3:
                if st.form_submit_button("✅ Vérifier", use_container_width=True):
                    if code and len(code) == 6 and code.isdigit():
                        valid, result = db.verify_reset_code(st.session_state.reset_email, code)
                        if valid:
                            st.session_state.reset_code = code
                            st.session_state.reset_step = 3
                            st.success("✅ Code vérifié !")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
                    else:
                        st.error("Veuillez saisir un code à 6 chiffres")
    
    # Étape 3 : Nouveau mot de passe
    elif st.session_state.reset_step == 3:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
            <h3 style="text-align: center; color: #4a6fa5;">🔐 Nouveau mot de passe</h3>
            <p style="text-align: center; color: #666;">Créez un nouveau mot de passe pour <strong>{st.session_state.reset_email}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("reset_password_form"):
            new_password = st.text_input("Nouveau mot de passe", type="password", placeholder="••••••••")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("⬅️ Retour", use_container_width=True):
                    st.session_state.reset_step = 2
                    st.rerun()
            with col2:
                if st.form_submit_button("✅ Modifier", use_container_width=True):
                    if new_password and confirm_password:
                        if len(new_password) < 6:
                            st.error("Le mot de passe doit contenir au moins 6 caractères")
                        elif new_password != confirm_password:
                            st.error("Les mots de passe ne correspondent pas")
                        else:
                            success, result = db.reset_password(
                                st.session_state.reset_email,
                                st.session_state.reset_code,
                                new_password
                            )
                            if success:
                                st.success("✅ Mot de passe modifié avec succès !")
                                st.balloons()
                                
                                # Réinitialiser les variables de session
                                st.session_state.reset_step = 1
                                st.session_state.reset_email = ""
                                st.session_state.reset_code = ""
                                
                                # Rediriger vers la page de connexion après 2 secondes
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
                    else:
                        st.error("Veuillez remplir tous les champs")

# ============================================================
# PAGE D'AUTHENTIFICATION (AVEC LIEN MOT DE PASSE OUBLIÉ)
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
                
                # Lien vers Mot de passe oublié
                st.markdown("""
                <div style="text-align: center; margin-top: 1rem;">
                    <a href="#" onclick="window.location.reload();" style="color: white; text-decoration: none;">
                        🔑 Mot de passe oublié ?
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Bouton Mot de passe oublié
                if st.button("🔑 Mot de passe oublié", use_container_width=True):
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

    # Afficher la page de réinitialisation si demandée
    if st.session_state.show_forgot_password:
        forgot_password_page()
        return

    if not st.session_state.logged_in:
        auth_page()
        return

    set_custom_theme()
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #4a6fa5, #166088); border-radius: 15px; color: white;">
            <div style="font-size: 3rem;">👤</div>
            <h4>{st.session_state.user.get('first_name', '')} {st.session_state.user.get('last_name', '')}</h4>
            <small>{st.session_state.user.get('email', '')}</small>
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
