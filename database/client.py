# NomadShare - Shared Supabase Client
# One client instance, imported by every database/*.py module.

import logging
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase connected")
except Exception as e:
    logger.error(f"❌ Supabase connection failed: {e}")
    raise
