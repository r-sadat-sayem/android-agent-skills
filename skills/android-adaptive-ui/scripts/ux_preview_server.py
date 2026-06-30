#!/usr/bin/env python3
"""
UX Preview Server — android-adaptive-ui skill
Single-selection pattern picker. Opens browser automatically, shuts down on Submit.

Usage:
    python scripts/ux_preview_server.py --src app/src/main/java/ui/ [--port 8080]
    python scripts/ux_preview_server.py --pattern navigation-suite-scaffold-migration [--port 8080]
    python scripts/ux_preview_server.py --playbook references/solutions-playbook.json [--port 8080]
"""
import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
PLAYBOOK_PATH = SKILL_ROOT / "references" / "solutions-playbook.json"
OUTPUT_DIR = Path("ux_preview_output")

FORM_FACTOR_LABELS = {
    "phone": "Phone",
    "large-screen": "Tablet / Large Screen",
    "foldable": "Foldable",
    "wear": "Wear OS",
    "auto": "Android Auto",
}

PROS_CONS = {
    "navigation-suite-scaffold-migration": {
        "pros": ["Automatic phone→rail→drawer", "Single component, no manual breakpoints", "Material 3 spec-compliant"],
        "cons": ["Requires adaptive-navigation-suite dep", "Needs @OptIn annotation"],
    },
    "navigation-rail-migration": {
        "pros": ["Auto adapts Compact→Rail→Drawer", "One source of truth for destinations"],
        "cons": ["Replaces Scaffold entirely — must refactor bottomBar slot"],
    },
    "content-discovery-feed": {
        "pros": ["Matches all major streaming app structures", "Sections are independently replaceable"],
        "cons": ["LazyVerticalGrid nested in LazyColumn needs fixed height"],
    },
    "hero-content-pattern": {
        "pros": ["Clear visual hierarchy", "Single above-fold focus point"],
        "cons": ["Must cap width on tablet with widthIn(max)"],
    },
    "discovery-grid-responsive": {
        "pros": ["Zero breakpoint code", "Scales phone→TV automatically"],
        "cons": ["minSize needs tuning per card design"],
    },
    "list-detail-pane-large-screen": {
        "pros": ["Predictive back gesture built-in", "Handles single/dual pane automatically"],
        "cons": ["AnimatedPane is mandatory — easy to omit", "Needs @OptIn annotation"],
    },
    "column-vertical-scroll": {
        "pros": ["Simple fix, no dep changes", "Works for fixed-length lists"],
        "cons": ["Don't combine with LazyColumn"],
    },
    "text-overflow-ellipsis": {
        "pros": ["Prevents silent clipping on all screen sizes"],
        "cons": ["Must set both maxLines AND overflow together"],
    },
}

_shutdown_event = threading.Event()
_feedback_lock = threading.Lock()


def load_playbook():
    if not PLAYBOOK_PATH.exists():
        return []
    with open(PLAYBOOK_PATH) as f:
        data = json.load(f)
    return data.get("patterns", [])


def filter_patterns(patterns, pattern_id=None, form_factor=None):
    if pattern_id:
        return [p for p in patterns if p["id"] == pattern_id]
    if form_factor:
        return [p for p in patterns if form_factor in p.get("form_factors", [])]
    ux_categories = {"Navigation", "LargeScreen", "Scrollability", "TextOverflow"}
    return [p for p in patterns if p.get("category") in ux_categories]


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_card(pattern, idx):
    pid = pattern["id"]
    category = pattern.get("category", "")
    form_factors = pattern.get("form_factors", [])
    code = escape_html(pattern.get("code_sketch", ""))
    problem = escape_html(pattern.get("problem", ""))
    pc = PROS_CONS.get(pid, {"pros": [], "cons": []})
    pros_html = "".join(f"<li>{escape_html(p)}</li>" for p in pc["pros"])
    cons_html = "".join(f"<li>{escape_html(c)}</li>" for c in pc["cons"])
    approach = pattern.get("approach", [])
    approach_html = "".join(f"<li>{escape_html(s)}</li>" for s in approach)
    template_ref = pattern.get("template_ref") or ""
    atomic_fix = pattern.get("atomic_fix") or ""
    ff_tags = "".join(
        f'<span class="ff-tag ff-{ff}">{FORM_FACTOR_LABELS.get(ff, ff)}</span>'
        for ff in form_factors
    )

    return f"""
<div class="card" id="card-{idx}" data-pattern="{pid}"
     data-ff="{','.join(form_factors)}" onclick="selectCard('{pid}', this)">
  <div class="card-radio"><span class="radio-dot"></span></div>
  <div class="card-inner">
    <div class="card-head">
      <div class="card-title-row">
        <h2 class="card-title">{escape_html(pid.replace('-', ' ').title())}</h2>
        <span class="card-cat">{escape_html(category)}</span>
      </div>
      <div class="ff-tags">{ff_tags}</div>
      <p class="card-problem">{problem}</p>
    </div>
    <div class="card-body">
      <div class="card-left">
        <p class="section-label">Implementation</p>
        <pre class="code-block"><code>{code}</code></pre>
        {f'<p class="meta-ref">Template: <code>{escape_html(template_ref)}</code></p>' if template_ref else ''}
        {f'<p class="meta-ref">Atomic fix: <code>{escape_html(atomic_fix)}</code></p>' if atomic_fix else ''}
      </div>
      <div class="card-right">
        <div class="pros-cons">
          <div class="pros">
            <p class="section-label pros-label">Pros</p>
            <ul>{pros_html or "<li>See approach steps</li>"}</ul>
          </div>
          <div class="cons">
            <p class="section-label cons-label">Watch-outs</p>
            <ul>{cons_html or "<li>See constraints</li>"}</ul>
          </div>
        </div>
        {f'<details><summary>Approach steps</summary><ol>{approach_html}</ol></details>' if approach_html else ''}
      </div>
    </div>
  </div>
</div>"""


def build_html(patterns, src_label=""):
    all_ffs = sorted({ff for p in patterns for ff in p.get("form_factors", [])})
    cards_html = "".join(build_card(p, i) for i, p in enumerate(patterns))
    ff_btns = "".join(
        f'<button class="ff-btn" data-ff="{ff}" onclick="filterFF(\'{ff}\')">'
        f'{FORM_FACTOR_LABELS.get(ff, ff)}</button>'
        for ff in all_ffs
    )
    count = len(patterns)
    src_note = f" &mdash; {escape_html(src_label)}" if src_label else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Android Adaptive UI — Pick a Pattern</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0d0d0d;
      color: #e0e0e0;
      min-height: 100vh;
      padding-bottom: 88px;
    }}

    /* ── top bar ── */
    .top-bar {{
      background: #111827;
      border-bottom: 1px solid #1f2937;
      padding: 14px 24px;
      position: sticky; top: 0; z-index: 200;
      display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    }}
    .top-bar h1 {{ font-size: 16px; font-weight: 600; color: #93c5fd; flex: 1; }}
    .top-bar .hint {{ font-size: 12px; color: #6b7280; }}

    /* ── filter bar ── */
    .filter-bar {{
      padding: 10px 24px;
      background: #111111;
      border-bottom: 1px solid #1f1f1f;
      display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
    }}
    .filter-label {{ font-size: 11px; color: #6b7280; margin-right: 4px; }}
    .ff-btn {{
      padding: 3px 12px; border-radius: 12px; border: 1px solid #374151;
      background: #1f2937; color: #9ca3af; font-size: 11px; cursor: pointer;
      transition: all 0.15s;
    }}
    .ff-btn:hover {{ border-color: #4b5563; color: #d1d5db; }}
    .ff-btn.active {{ background: #1d4ed8; border-color: #2563eb; color: #fff; }}
    .ff-btn.all {{ border-color: #4b5563; }}

    /* ── cards ── */
    .cards {{ padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; max-width: 1300px; margin: 0 auto; }}

    .card {{
      display: flex; gap: 0;
      background: #161616;
      border: 2px solid #262626;
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      transition: border-color 0.15s, box-shadow 0.15s;
      user-select: none;
    }}
    .card:hover {{ border-color: #374151; box-shadow: 0 0 0 1px #374151; }}
    .card.selected {{
      border-color: #16a34a;
      box-shadow: 0 0 0 1px #16a34a, 0 4px 20px rgba(22,163,74,0.15);
    }}
    .card.hidden {{ display: none; }}

    /* radio column */
    .card-radio {{
      width: 48px; flex-shrink: 0;
      display: flex; align-items: flex-start; justify-content: center;
      padding-top: 20px;
      background: #111;
      border-right: 1px solid #222;
      transition: background 0.15s;
    }}
    .card.selected .card-radio {{ background: #052e16; border-right-color: #14532d; }}
    .radio-dot {{
      width: 18px; height: 18px;
      border-radius: 50%;
      border: 2px solid #374151;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.15s;
      flex-shrink: 0;
    }}
    .card:hover .radio-dot {{ border-color: #6b7280; }}
    .card.selected .radio-dot {{
      border-color: #16a34a;
      background: #16a34a;
    }}
    .card.selected .radio-dot::after {{
      content: '';
      width: 6px; height: 6px;
      border-radius: 50%;
      background: #fff;
    }}

    .card-inner {{ flex: 1; min-width: 0; }}

    /* card head */
    .card-head {{
      padding: 16px 20px 12px;
      background: #1a1a2a;
      border-bottom: 1px solid #262626;
    }}
    .card.selected .card-head {{ background: #0a1f0a; border-bottom-color: #14532d; }}
    .card-title-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
    .card-title {{ font-size: 15px; font-weight: 600; color: #f3f4f6; flex: 1; }}
    .card-cat {{
      font-size: 10px; padding: 2px 8px; border-radius: 10px;
      background: #1e3a5f; color: #60a5fa; border: 1px solid #1d4ed8;
    }}
    .ff-tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }}
    .ff-tag {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 500; }}
    .ff-phone        {{ background: #14291a; color: #86efac; border: 1px solid #166534; }}
    .ff-large-screen {{ background: #0c2040; color: #93c5fd; border: 1px solid #1d4ed8; }}
    .ff-foldable     {{ background: #291a00; color: #fcd34d; border: 1px solid #b45309; }}
    .ff-wear         {{ background: #200029; color: #d8b4fe; border: 1px solid #7e22ce; }}
    .ff-auto         {{ background: #1a0000; color: #fca5a5; border: 1px solid #991b1b; }}
    .card-problem {{ font-size: 12px; color: #9ca3af; line-height: 1.5; }}

    /* card body */
    .card-body {{
      display: grid; grid-template-columns: 1fr 1fr;
    }}
    @media (max-width: 780px) {{ .card-body {{ grid-template-columns: 1fr; }} }}
    .card-left {{ padding: 14px 18px; border-right: 1px solid #1f1f1f; }}
    .card-right {{ padding: 14px 18px; }}

    .section-label {{
      font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px;
      color: #4b5563; margin-bottom: 8px;
    }}
    .pros-label {{ color: #166534 !important; }}
    .cons-label {{ color: #991b1b !important; }}

    .code-block {{
      background: #0a0e14; border: 1px solid #1f2937; border-radius: 8px;
      padding: 12px; font-size: 11px; line-height: 1.6; overflow-x: auto;
      color: #e2e8f0; font-family: "SF Mono","Fira Code","Consolas",monospace;
      white-space: pre;
    }}
    .meta-ref {{ font-size: 10px; color: #4b5563; margin-top: 6px; }}
    .meta-ref code {{ background: #1f2937; padding: 1px 4px; border-radius: 3px; color: #93c5fd; }}

    .pros-cons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px; }}
    .pros ul, .cons ul {{ padding-left: 14px; }}
    .pros li, .cons li {{ font-size: 11px; line-height: 1.7; color: #d1d5db; }}
    .pros li {{ color: #bbf7d0; }}
    .cons li {{ color: #fecaca; }}

    details {{ margin-top: 8px; }}
    summary {{ font-size: 11px; color: #6b7280; cursor: pointer; padding: 2px 0; }}
    summary:hover {{ color: #9ca3af; }}
    details ol {{ padding-left: 16px; margin-top: 6px; }}
    details li {{ font-size: 11px; line-height: 1.7; color: #9ca3af; }}

    /* ── submit bar ── */
    .submit-bar {{
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 300;
      background: #111827;
      border-top: 1px solid #1f2937;
      padding: 14px 24px;
      display: flex; align-items: center; gap: 16px;
    }}
    .submit-hint {{ font-size: 13px; color: #6b7280; flex: 1; }}
    .submit-hint .sel-name {{ color: #86efac; font-weight: 500; }}
    .submit-btn {{
      padding: 10px 28px; border-radius: 8px; border: none;
      background: #15803d; color: #fff; font-size: 14px; font-weight: 600;
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }}
    .submit-btn:disabled {{
      background: #1f2937; color: #4b5563; cursor: not-allowed;
    }}
    .submit-btn:not(:disabled):hover {{ background: #166534; }}
    .submit-btn.done {{ background: #064e3b; color: #6ee7b7; cursor: default; }}

    .empty-state {{ text-align: center; padding: 60px 24px; color: #4b5563; }}
    .empty-state h2 {{ font-size: 18px; margin-bottom: 8px; }}
  </style>
</head>
<body>

<div class="top-bar">
  <h1>Android Adaptive UI &mdash; Pick a Pattern</h1>
  <span class="hint">{count} option{'' if count == 1 else 's'}{src_note}</span>
</div>

<div class="filter-bar">
  <span class="filter-label">Form factor:</span>
  <button class="ff-btn all active" onclick="filterFF('all')">All</button>
  {ff_btns}
</div>

<div class="cards" id="cards">
  {cards_html if cards_html else '<div class="empty-state"><h2>No patterns found</h2><p>Try passing --pattern &lt;id&gt; or run analyze_ui first.</p></div>'}
</div>

<div class="submit-bar">
  <span class="submit-hint" id="submit-hint">Select a pattern above, then click Submit.</span>
  <button class="submit-btn" id="submit-btn" disabled onclick="submitSelection()">Submit</button>
</div>

<script>
  let selected = null;

  function selectCard(patternId, el) {{
    // deselect previous
    document.querySelectorAll('.card.selected').forEach(c => c.classList.remove('selected'));
    // select new
    el.classList.add('selected');
    selected = patternId;
    // update submit bar
    const name = patternId.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
    document.getElementById('submit-hint').innerHTML =
      'Selected: <span class="sel-name">' + name + '</span>';
    const btn = document.getElementById('submit-btn');
    btn.disabled = false;
    btn.textContent = 'Submit';
    btn.classList.remove('done');
  }}

  function filterFF(ff) {{
    document.querySelectorAll('.ff-btn').forEach(b => b.classList.remove('active'));
    const target = document.querySelector(ff === 'all' ? '.ff-btn.all' : `.ff-btn[data-ff="${{ff}}"]`);
    if (target) target.classList.add('active');
    document.querySelectorAll('.card').forEach(card => {{
      const ffs = card.dataset.ff.split(',');
      card.classList.toggle('hidden', ff !== 'all' && !ffs.includes(ff));
    }});
  }}

  function submitSelection() {{
    if (!selected) return;
    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.textContent = 'Submitting…';

    fetch('/submit', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{ selected: selected, ts: new Date().toISOString() }})
    }})
    .then(r => r.json())
    .then(() => {{
      btn.textContent = '✓ Submitted';
      btn.classList.add('done');
      document.getElementById('submit-hint').innerHTML =
        'Done! You can close this tab.';
    }})
    .catch(() => {{
      btn.disabled = false;
      btn.textContent = 'Submit';
      document.getElementById('submit-hint').textContent = 'Submit failed — try again.';
    }});
  }}
</script>
</body>
</html>"""


DONE_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Done</title>
  <style>
    body { font-family: -apple-system, sans-serif; background: #0d0d0d; color: #e0e0e0;
           display: flex; align-items: center; justify-content: center; min-height: 100vh; }
    .box { text-align: center; }
    h1 { font-size: 28px; color: #86efac; margin-bottom: 12px; }
    p  { font-size: 14px; color: #6b7280; }
  </style>
</head>
<body>
  <div class="box">
    <h1>&#10003; Selection recorded</h1>
    <p>You can close this tab.</p>
  </div>
</body>
</html>"""


class PreviewHandler(BaseHTTPRequestHandler):
    html_content = b""
    feedback_path = OUTPUT_DIR / "feedback.json"

    def log_message(self, fmt, *args):
        pass  # suppress request logs

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._respond(200, "text/html; charset=utf-8", self.html_content)
        else:
            self._respond(404, "text/plain", b"Not found")

    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                entry = json.loads(body)
            except json.JSONDecodeError:
                self._respond(400, "text/plain", b"Bad request")
                return

            with _feedback_lock:
                existing = []
                if self.feedback_path.exists():
                    try:
                        existing = json.loads(self.feedback_path.read_text())
                    except (json.JSONDecodeError, OSError):
                        existing = []
                existing.append(entry)
                self.feedback_path.write_text(json.dumps(existing, indent=2))

            self._respond(200, "application/json", b'{"ok":true}')
            _shutdown_event.set()
        else:
            self._respond(404, "text/plain", b"Not found")

    def _respond(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Android Adaptive UI Preview Server")
    parser.add_argument("--src",         help="Source path label (informational)")
    parser.add_argument("--pattern",     help="Show a single pattern by ID")
    parser.add_argument("--form-factor", dest="form_factor",
                        help="Filter by form factor (phone|large-screen|foldable|wear|auto)")
    parser.add_argument("--playbook",    help="Path to solutions-playbook.json")
    parser.add_argument("--port",        type=int, default=8080)
    args = parser.parse_args()

    playbook_path = Path(args.playbook) if args.playbook else PLAYBOOK_PATH
    if not playbook_path.exists():
        print(f"ERROR: playbook not found at {playbook_path}", file=sys.stderr)
        sys.exit(1)

    patterns = load_playbook()
    if not patterns:
        print("ERROR: no patterns loaded from playbook", file=sys.stderr)
        sys.exit(1)

    filtered = filter_patterns(patterns, pattern_id=args.pattern, form_factor=args.form_factor)
    if not filtered:
        print(f"No patterns matched (pattern={args.pattern!r}, form_factor={args.form_factor!r})")
        print("Available IDs:", ", ".join(p["id"] for p in patterns))
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    html_bytes = build_html(filtered, src_label=args.src or "").encode("utf-8")
    (OUTPUT_DIR / "index.html").write_bytes(html_bytes)

    PreviewHandler.html_content = html_bytes
    PreviewHandler.feedback_path = OUTPUT_DIR / "feedback.json"

    httpd = HTTPServer(("", args.port), PreviewHandler)
    url = f"http://localhost:{args.port}"

    print(f"\nUX Preview  →  {url}")
    print(f"Patterns    :  {len(filtered)}")
    print(f"Feedback    :  {OUTPUT_DIR / 'feedback.json'}")
    print(f"Waiting for selection… (Ctrl-C to cancel)\n")

    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    # Open browser after a short delay so the server is ready
    threading.Timer(0.4, webbrowser.open, args=[url]).start()

    try:
        _shutdown_event.wait(timeout=600)  # auto-close after 10 min
    except KeyboardInterrupt:
        pass

    httpd.shutdown()

    feedback_path = OUTPUT_DIR / "feedback.json"
    if feedback_path.exists():
        try:
            votes = json.loads(feedback_path.read_text())
            if votes:
                last = votes[-1]
                selected_id = last.get("selected", "—")
                print(f"Selected: {selected_id}")
        except (json.JSONDecodeError, OSError):
            pass


if __name__ == "__main__":
    main()
