"""One-shot: emoji statice din markup-ul dosar.html -> {{ icon() }} (macro _icon.html).
Separa markup-ul de <script> => string-urile JS (emoji randate dinamic) raman EMOJI (deferred, fara risc).
"""
import re
from pathlib import Path

f = Path("src/evaluare/web/templates/curent/dosar.html")
s = f.read_text(encoding="utf-8")
idx = s.find("<script>")
head, tail = (s[:idx], s[idx:]) if idx > 0 else (s, "")

if "_icon.html" not in head:
    head = '{% from "_icon.html" import icon %}\n' + head

# emoji impachetate in <span aria-hidden> -> {{ icon }}
SPAN = {"📄": "doc", "🛡": "shield", "🔒": "lock", "🧾": "audit", "🔓": "unlock",
        "➕": "add", "↻": "refresh", "↑": "upload", "📝": "edit", "📎": "attach", "⚠": "warn"}
for emo, name in SPAN.items():
    head = head.replace(f'<span aria-hidden="true">{emo}</span>', '{{ icon("' + name + '") }}')

# emoji inline in text de markup (>EMOJI<spatiu>) -> {{ icon }}
INLINE = {"📄": "doc", "🔎": "search", "📥": "import", "🧩": "grid", "📐": "grid",
          "🔄": "refresh", "💾": "save", "🧾": "audit", "⚠️": "warn"}
for emo, name in INLINE.items():
    head = re.sub(r'>' + re.escape(emo) + r'\s', '>{{ icon("' + name + '") }} ', head)

f.write_text(head + tail, encoding="utf-8")

rem = re.findall(r'[\U0001F300-\U0001FAFF☀-➿⬀-⯿]', head)
print("import _icon.html in markup:", "_icon.html" in head)
print("emoji ramase in MARKUP (trebuie ~0, fara glife →←↗):", rem)
print("emoji in JS (tail, deferred, raman):", len(re.findall(r'[\U0001F300-\U0001FAFF☀-➿]', tail)))
