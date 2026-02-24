from typing import Dict, Any
from datetime import datetime
import logging
from database import save_session_to_db, get_session_from_db

logger = logging.getLogger(__name__)

# Cache for loaded sessions (still useful for speed, but backed by DB)
_session_cache: Dict[str, 'PersistentSession'] = {}

class PersistentSession(dict):
    """
    A dictionary-like object that automatically saves to SQLite when modified.
    This ensures session state (including uploaded files) survives server restarts.
    """
    def __init__(self, session_id: str, *args, **kwargs):
        self.session_id = session_id
        super().__init__(*args, **kwargs)
        
    def __setitem__(self, key: str, value: Any):
        super().__setitem__(key, value)
        self._save()
        
    def __delitem__(self, key: str):
        super().__delitem__(key)
        self._save()
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save()
        
    def pop(self, key, default=None):
        value = super().pop(key, default)
        self._save()
        return value
        
    def setdefault(self, key, default=None):
        value = super().setdefault(key, default)
        self._save()
        return value

    def _save(self):
        """Trigger save to database"""
        # Extract user_id from session data
        user_id = self.get('user_id')
        if not user_id:
            logger.warning(f"Session {self.session_id} has no user_id, skipping DB save")
            return
        
        try:
            save_session_to_db(self.session_id, dict(self), user_id)
        except Exception as e:
            logger.error(f"Failed to persist session {self.session_id}: {e}")

def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get or create a persistent session.
    1. Check in-memory cache
    2. Check database
    3. Create new if missing
    """
    # 1. Check cache
    if session_id in _session_cache:
        return _session_cache[session_id]
        
    # 2. Check Database
    db_data = get_session_from_db(session_id)
    if db_data:
        logger.info(f"✅ Restored session {session_id[:8]}... from database")
        session = PersistentSession(session_id, db_data)
        _session_cache[session_id] = session
        return session
        
    # 3. Create New
    logger.info(f"🆕 Creating new session {session_id[:8]}...")
    initial_data = {
        "current_step": "category",
        "user_idea": "",
        "selected_category": None,
        "selected_llm": "Claude", # Default
        "answers_json": {},
        "messages": [],
        "conversation_step": 0,
        "selected_chips": [],
        "api_key_entered": True,
        "created_at": datetime.now().isoformat(),
        # Ensure these lists exist
        "uploaded_files": [],
        "reference_settings": {} 
    }
    
    session = PersistentSession(session_id, initial_data)
    _session_cache[session_id] = session
    session._save() # Save initial state
    return session
