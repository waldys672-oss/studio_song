import os
import cloudinary
from sqlalchemy.pool import NullPool 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 1. Secret Key Protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sumo-secret-key-change-in-production')

   # 2. Database configuration with Render Postgres fix
    uri = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'instance', 'sumo.db')
    )
    
    # Render sometimes provides postgres://, but SQLAlchemy 1.4+ needs postgresql://
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─── DATABASE PERFORMANCE OPTIMIZATIONS ───
    # Changed to NullPool to prevent exhausting Neon's free tier compute quota
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool  # <-- 2. Replaced the 5 old settings with this
    }

    # 3. File upload limits
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload

    # 4. Cloudinary configuration for storage
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    if CLOUDINARY_URL:
        cloudinary.config(cloudinary_url=CLOUDINARY_URL, secure=True)
    # 5. WhatsApp configuration
    WHATSAPP_NUMBER = '+966558262881'

    # 6. Brand Identity
    BRAND_NAME = 'ضوء الفمر'
    BRAND_YEAR = 2026