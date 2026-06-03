"""Server local pentru QA vizual (preview). Nu deschide browserul; port fix."""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import uvicorn  # noqa: E402

from evaluare.db.storage import Storage  # noqa: E402
from evaluare.web.app import create_app  # noqa: E402

s = Storage(pathlib.Path(tempfile.gettempdir()) / "qa_design.db")
s.init()
app = create_app(storage=s, client=None)
uvicorn.run(app, host="127.0.0.1", port=5119, log_level="warning")
