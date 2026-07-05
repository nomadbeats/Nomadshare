# NomadShare - Bot Mode
# PRIVATE (default): only admins can save files / generate links.
#                     Everyone can still open a link an admin already shared.
# PUBLIC: anyone can save files and generate links.

import logging
from core.permissions import is_admin
from database.settings import get_setting, set_setting

logger = logging.getLogger(__name__)

SETTING_KEY = "bot_mode"
DEFAULT_MODE = "private"

_current_mode = DEFAULT_MODE
_loaded = False


async def _ensure_loaded():
    global _current_mode, _loaded
    if _loaded:
        return
    stored = await get_setting(SETTING_KEY, DEFAULT_MODE)
    _current_mode = stored if stored in ("public", "private") else DEFAULT_MODE
    _loaded = True


async def get_mode() -> str:
    await _ensure_loaded()
    return _current_mode


async def set_mode(mode: str) -> bool:
    global _current_mode
    if mode not in ("public", "private"):
        return False
    ok = await set_setting(SETTING_KEY, mode)
    if ok:
        _current_mode = mode
        logger.info(f"✅ Bot mode set to {mode}")
    return ok


async def can_use_upload_features(user_id: int) -> bool:
    """Whether this user may save files / generate links."""
    if is_admin(user_id):
        return True
    return await get_mode() == "public"


PRIVATE_MODE_TEXT = (
    "This bot is in private mode right now — only the admin can save files "
    "and generate links. You can still open any link the admin shares with you."
)
