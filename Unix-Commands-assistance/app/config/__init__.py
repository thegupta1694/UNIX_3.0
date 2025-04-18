"""
Configuration package.
"""

# Import settings
try:
    from app.config.settings_vercel import *
except ImportError:
    from app.config.settings import * 