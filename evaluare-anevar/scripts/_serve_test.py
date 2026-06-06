"""Server local efemer pentru testarea Playwright (fără AI, DB temporar)."""
import os
import shutil
import tempfile

import uvicorn

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

# Izolează datele e2e într-un folder temporar — NU atinge `date/` (contul/dosarele reale).
out = os.path.join(tempfile.gettempdir(), "anevar_pw_date")
shutil.rmtree(out, ignore_errors=True)
os.environ["OUTPUT_DIR"] = out

db = os.path.join(tempfile.gettempdir(), "anevar_pw.db")
if os.path.exists(db):
    os.remove(db)
s = Storage(db)
s.init()
app = create_app(storage=s, client=None)
uvicorn.run(app, host="127.0.0.1", port=8765, log_level="error")
