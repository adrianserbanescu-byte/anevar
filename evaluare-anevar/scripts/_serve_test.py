"""Server local efemer pentru testarea Playwright (fără AI, DB temporar)."""
import os
import tempfile

import uvicorn

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

db = os.path.join(tempfile.gettempdir(), "anevar_pw.db")
if os.path.exists(db):
    os.remove(db)
s = Storage(db)
s.init()
app = create_app(storage=s, client=None)
uvicorn.run(app, host="127.0.0.1", port=8765, log_level="error")
