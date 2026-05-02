import os
import cloudinary

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
    # These settings prevent connection drops and make queries much faster
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,                # Keep 5 active connections ready to serve users instantly
        "max_overflow": 10,            # Allow up to 10 extra temporary connections during peak traffic
        "pool_timeout": 30,            # Wait up to 30 seconds for a connection before giving up
        "pool_recycle": 1200,          # Automatically recycle connections every 20 minutes
        "pool_pre_ping": True,         # CRITICAL: Tests if the connection is still alive before using it
    }

    # 3. File upload limits
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload

    # 4. Cloudinary configuration for storage
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    if CLOUDINARY_URL:
        cloudinary.config(secure=True)

    # 5. WhatsApp configuration
    WHATSAPP_NUMBER = '+966558262881'

    # 6. Brand Identity
    BRAND_NAME = 'ضوء الفمر'
    BRAND_YEAR = 2026