#!/usr/bin/env python3
"""
UX Preview Server — android-adaptive-ui skill
Generates a localhost webpage showing adaptive UX options and collects feedback.

Usage:
    python scripts/ux_preview_server.py --src app/src/main/java/ui/ [--port 8080]
    python scripts/ux_preview_server.py --pattern navigation-suite-scaffold-migration [--port 8080]
    python scripts/ux_preview_server.py --playbook references/solutions-playbook.json [--port 8080]
"""
import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
PLAYBOOK_PATH = SKILL_ROOT / "references" / "solutions-playbook.json"
OUTPUT_DIR = Path("ux_preview_output")

DEVICE_FORM_FACTORS = ["phone", "large-screen", "foldable", "wear", "auto"]

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
        "cons": ["Requires material3-adaptive-navigation-suite dep", "Needs @OptIn annotation"],
    },
    "navigation-rail-migration": {
        "pros": ["Auto adapts Compact→Rail→Drawer", "One source of truth for destinations"],
        "cons": ["Replaces Scaffold entirely — must refactor bottomBar slot"],
    },
    "content-discovery-feed": {
        "pros": ["Structure matches all major streaming apps", "Sections are independently replaceable"],
        "cons": ["LazyVerticalGrid nested in LazyColumn needs fixed height"],
    },
    "hero-content-pattern": {
        "pros": ["Clear visual hierarchy", "Single above-fold focus point"],
        "cons": ["Must cap width on tablet manually (widthIn max)"],
    },
    "discovery-grid-responsive": {
        "pros": ["Zero breakpoint code needed", "Scales from phone to TV automatically"],
        "cons": ["minSize requires tuning per card design"],
    },
    "list-detail-pane-large-screen": {
        "pros": ["Predictive back gesture built-in", "Handles single/dual pane automatically"],
        "cons": ["AnimatedPane is mandatory — easy to omit", "Needs @OptIn annotation"],
    },
    "column-vertical-scroll": {
        "pros": ["Simple fix, no dep changes", "Works for fixed-length lists"],
        "cons": ["Don't combine with LazyColumn — use LazyColumn for dynamic lists instead"],
    },
    "text-overflow-ellipsis": {
        "pros": ["Prevents silent clipping on all screen sizes"],
        "cons": ["Must set both maxLines AND overflow — overflow alone has no effect"],
    },
}

_feedback_lock = threading.Lock()


def load_playbook():
    if not PLAYBOOK_PATH.exists():
        return []
    with open(PLAYBOOK_PATH) as f:
        data = json.load(f)
    return data.get("patterns", [])


def filter_patterns(patterns, pattern_id=None, form_factor=None, src=None):
    if pattern_id:
        return [p for p in patterns if p["id"] == pattern_id]
    if form_factor:
        return [p for p in patterns if form_factor in p.get("form_factors", [])]
    # Default: all UX/layout patterns (skip low-level API fix patterns shown by default)
    ux_categories = {"Navigation", "LargeScreen", "Scrollability", "TextOverflow"}
    return [p for p in patterns if p.get("category") in ux_categories]


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_option_card(pattern, idx):
    pid = pattern["id"]
    category = pattern.get("category", "")
    form_factors = pattern.get("form_factors", [])
    ff_labels = " · ".join(FORM_FACTOR_LABELS.get(ff, ff) for ff in form_factors)
    code = escape_html(pattern.get("code_sketch", ""))
    problem = escape_html(pattern.get("problem", ""))
    pc = PROS_CONS.get(pid, {"pros": [], "cons": []})
    pros_html = "".join(f"<li>{escape_html(p)}</li>" for p in pc["pros"])
    cons_html = "".join(f"<li>{escape_html(c)}</li>" for c in pc["cons"])
    constraints = pattern.get("constraints", [])
    constraints_html = "".join(f"<li>{escape_html(c)}</li>" for c in constraints)
    approach = pattern.get("approach", [])
    approach_html = "".join(f"<li>{escape_html(step)}</li>" for step in approach)
    template_ref = pattern.get("template_ref") or ""
    atomic_fix = pattern.get("atomic_fix") or ""

    ff_tags = "".join(
        f'<span class="ff-tag ff-{ff}">{FORM_FACTOR_LABELS.get(ff, ff)}</span>'
        for ff in form_factors
    )

    return f"""
    <div class="option-card" id="card-{idx}" data-pattern="{pid}" data-form-factors="{','.join(form_factors)}">
      <div class="card-header">
        <div class="card-title-row">
          <span class="card-index">#{idx + 1}</span>
          <h2 class="card-title">{escape_html(pid.replace('-', ' ').title())}</h2>
          <span class="card-category">{escape_html(category)}</span>
        </div>
        <div class="ff-tags">{ff_tags}</div>
        <p class="card-problem"><strong>Problem:</strong> {problem}</p>
      </div>

      <div class="card-body">
        <div class="card-left">
          <h3>Implementation</h3>
          <pre class="code-block"><code>{code}</code></pre>
          {f'<p class="template-ref">Template: <code>{escape_html(template_ref)}</code></p>' if template_ref else ''}
          {f'<p class="atomic-fix">Atomic fix: <code>{escape_html(atomic_fix)}</code></p>' if atomic_fix else ''}
        </div>

        <div class="card-right">
          <div class="pros-cons">
            <div class="pros">
              <h3>Pros</h3>
              <ul>{pros_html if pros_html else "<li>See approach steps</li>"}</ul>
            </div>
            <div class="cons">
              <h3>Cons / Watch-outs</h3>
              <ul>{cons_html if cons_html else "<li>See constraints</li>"}</ul>
            </div>
          </div>

          <details class="approach-details">
            <summary>Approach steps</summary>
            <ol>{approach_html}</ol>
          </details>

          {f'<details class="constraints-details"><summary>Hard constraints</summary><ul>{constraints_html}</ul></details>' if constraints_html else ''}
        </div>
      </div>

      <div class="feedback-row">
        <span class="feedback-label">Was this pattern helpful?</span>
        <button class="vote-btn vote-up" onclick="vote('{pid}', 'up', this)" title="Yes, helpful">
          &#128077; Helpful
        </button>
        <button class="vote-btn vote-down" onclick="vote('{pid}', 'down', this)" title="Not helpful">
          &#128078; Not helpful
        </button>
        <span class="vote-status" id="status-{pid}"></span>
      </div>
    </div>
    """


def build_html(patterns, src_label=""):
    all_form_factors = sorted({ff for p in patterns for ff in p.get("form_factors", [])})
    cards_html = "".join(build_option_card(p, i) for i, p in enumerate(patterns))
    ff_filter_buttons = "".join(
        f'<button class="ff-filter" data-ff="{ff}" onclick="filterByFF(\'{ff}\')">'
        f'{FORM_FACTOR_LABELS.get(ff, ff)}</button>'
        for ff in all_form_factors
    )
    count = len(patterns)
    src_info = f" — {escape_html(src_label)}" if src_label else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Android Adaptive UI Preview</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f0f0f;
      color: #e0e0e0;
      min-height: 100vh;
      padding: 0 0 60px 0;
    }}
    .top-bar {{
      background: #1a1a2e;
      border-bottom: 1px solid #16213e;
      padding: 16px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .top-bar h1 {{
      font-size: 18px;
      font-weight: 600;
      color: #a0c4ff;
      flex: 1 0 auto;
    }}
    .top-bar .meta {{ font-size: 12px; color: #888; }}
    .filter-bar {{
      display: flex;
      gap: 8px;
      padding: 12px 24px;
      background: #141414;
      border-bottom: 1px solid #222;
      flex-wrap: wrap;
      align-items: center;
    }}
    .filter-label {{ font-size: 12px; color: #888; margin-right: 4px; }}
    .ff-filter {{
      padding: 4px 12px;
      border-radius: 16px;
      border: 1px solid #444;
      background: #1e1e1e;
      color: #ccc;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .ff-filter:hover, .ff-filter.active {{
      background: #1565c0;
      border-color: #1976d2;
      color: #fff;
    }}
    .ff-filter.all {{ border-color: #555; }}
    .cards-container {{ padding: 20px 24px; display: flex; flex-direction: column; gap: 20px; max-width: 1400px; margin: 0 auto; }}
    .option-card {{
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      overflow: hidden;
      transition: border-color 0.2s;
    }}
    .option-card:hover {{ border-color: #3a3a3a; }}
    .option-card.voted-up {{ border-color: #2e7d32; }}
    .option-card.voted-down {{ border-color: #c62828; }}
    .option-card.hidden {{ display: none; }}
    .card-header {{
      padding: 16px 20px 12px;
      background: #1e1e2e;
      border-bottom: 1px solid #2a2a2a;
    }}
    .card-title-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }}
    .card-index {{
      font-size: 11px;
      color: #666;
      background: #2a2a2a;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .card-title {{
      font-size: 16px;
      font-weight: 600;
      color: #e0e0e0;
      flex: 1;
    }}
    .card-category {{
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 12px;
      background: #162032;
      color: #64b5f6;
      border: 1px solid #1565c0;
    }}
    .ff-tags {{ display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }}
    .ff-tag {{
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 500;
    }}
    .ff-phone {{ background: #1b3a1b; color: #81c784; border: 1px solid #2e7d32; }}
    .ff-large-screen {{ background: #0d2540; color: #64b5f6; border: 1px solid #1565c0; }}
    .ff-foldable {{ background: #2d1b00; color: #ffcc02; border: 1px solid #f57c00; }}
    .ff-wear {{ background: #2d0032; color: #ce93d8; border: 1px solid #7b1fa2; }}
    .ff-auto {{ background: #1a0000; color: #ef9a9a; border: 1px solid #c62828; }}
    .card-problem {{ font-size: 13px; color: #aaa; line-height: 1.5; }}
    .card-body {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
    }}
    @media (max-width: 800px) {{ .card-body {{ grid-template-columns: 1fr; }} }}
    .card-left {{ padding: 16px 20px; border-right: 1px solid #2a2a2a; }}
    .card-right {{ padding: 16px 20px; }}
    .card-left h3, .card-right h3 {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; margin-bottom: 10px; }}
    .code-block {{
      background: #0d1117;
      border: 1px solid #21262d;
      border-radius: 8px;
      padding: 14px;
      font-size: 12px;
      line-height: 1.6;
      overflow-x: auto;
      color: #e6edf3;
      font-family: "SF Mono", "Fira Code", "Consolas", monospace;
      white-space: pre;
    }}
    .template-ref, .atomic-fix {{ font-size: 11px; color: #666; margin-top: 8px; }}
    .template-ref code, .atomic-fix code {{ background: #1e1e1e; padding: 1px 5px; border-radius: 3px; color: #a0c4ff; }}
    .pros-cons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }}
    .pros h3, .cons h3 {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
    .pros h3 {{ color: #81c784; }}
    .cons h3 {{ color: #ef9a9a; }}
    .pros ul, .cons ul {{ padding-left: 16px; }}
    .pros li, .cons li {{ font-size: 12px; line-height: 1.6; color: #ccc; }}
    details {{ margin-top: 10px; }}
    summary {{
      font-size: 12px;
      color: #888;
      cursor: pointer;
      padding: 4px 0;
      user-select: none;
    }}
    summary:hover {{ color: #aaa; }}
    details ol, details ul {{ padding-left: 18px; margin-top: 8px; }}
    details li {{ font-size: 12px; line-height: 1.7; color: #bbb; }}
    .feedback-row {{
      padding: 12px 20px;
      background: #141414;
      border-top: 1px solid #2a2a2a;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .feedback-label {{ font-size: 12px; color: #666; flex: 1; }}
    .vote-btn {{
      padding: 6px 16px;
      border-radius: 6px;
      border: 1px solid #444;
      background: #1e1e1e;
      color: #ccc;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .vote-btn:hover {{ border-color: #666; background: #2a2a2a; }}
    .vote-btn:disabled {{ opacity: 0.5; cursor: default; }}
    .vote-up.voted {{ background: #1b3a1b; border-color: #2e7d32; color: #81c784; }}
    .vote-down.voted {{ background: #2d0a0a; border-color: #c62828; color: #ef9a9a; }}
    .vote-status {{ font-size: 12px; color: #888; }}
    .empty-state {{ text-align: center; padding: 60px 24px; color: #555; }}
    .empty-state h2 {{ font-size: 18px; margin-bottom: 8px; color: #666; }}
  </style>
</head>
<body>
  <div class="top-bar">
    <h1>Android Adaptive UI Preview</h1>
    <span class="meta">{count} pattern{'' if count == 1 else 's'}{src_info}</span>
    <span class="meta">Feedback → ux_preview_output/feedback.json</span>
  </div>

  <div class="filter-bar">
    <span class="filter-label">Filter by form factor:</span>
    <button class="ff-filter all active" onclick="filterByFF('all')">All</button>
    {ff_filter_buttons}
  </div>

  <div class="cards-container" id="cards-container">
    {cards_html if cards_html else '<div class="empty-state"><h2>No patterns found</h2><p>Try running analyze_ui first, or pass --pattern &lt;id&gt;</p></div>'}
  </div>

  <script>
    let currentFF = 'all';

    function filterByFF(ff) {{
      currentFF = ff;
      document.querySelectorAll('.ff-filter').forEach(b => b.classList.remove('active'));
      document.querySelector(`.ff-filter[data-ff="${{ff}}"], .ff-filter.all`).classList.add('active');
      document.querySelectorAll('.option-card').forEach(card => {{
        const ffs = card.dataset.formFactors.split(',');
        card.classList.toggle('hidden', ff !== 'all' && !ffs.includes(ff));
      }});
    }}

    function vote(patternId, direction, btn) {{
      const card = btn.closest('.option-card');
      const allBtns = card.querySelectorAll('.vote-btn');
      allBtns.forEach(b => b.disabled = true);
      btn.classList.add('voted');
      card.classList.add(direction === 'up' ? 'voted-up' : 'voted-down');
      document.getElementById('status-' + patternId).textContent =
        direction === 'up' ? 'Marked helpful ✓' : 'Feedback recorded';

      fetch('/feedback', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{pattern_id: patternId, vote: direction, ts: new Date().toISOString()}})
      }}).catch(() => {{
        document.getElementById('status-' + patternId).textContent = '(offline — feedback not saved)';
      }});
    }}
  </script>
</body>
</html>"""


class PreviewHandler(BaseHTTPRequestHandler):
    html_content = b""
    feedback_path = OUTPUT_DIR / "feedback.json"

    def log_message(self, format, *args):
        pass  # suppress per-request logs

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(self.html_content)))
            self.end_headers()
            self.wfile.write(self.html_content)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                entry = json.loads(body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return

            with _feedback_lock:
                existing = []
                if self.feedback_path.exists():
                    with open(self.feedback_path) as f:
                        try:
                            existing = json.load(f)
                        except json.JSONDecodeError:
                            existing = []
                existing.append(entry)
                with open(self.feedback_path, "w") as f:
                    json.dump(existing, f, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Android Adaptive UI Preview Server")
    parser.add_argument("--src", help="Source path scanned by analyze_ui (informational label)")
    parser.add_argument("--pattern", help="Show a single pattern by ID")
    parser.add_argument("--form-factor", dest="form_factor", help="Filter by form factor (phone|large-screen|foldable|wear|auto)")
    parser.add_argument("--playbook", help="Path to solutions-playbook.json (default: skill bundled)")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    args = parser.parse_args()

    playbook_path = Path(args.playbook) if args.playbook else PLAYBOOK_PATH
    if not playbook_path.exists():
        print(f"ERROR: playbook not found at {playbook_path}", file=sys.stderr)
        sys.exit(1)

    patterns = load_playbook()
    if not patterns:
        print("ERROR: no patterns loaded from playbook", file=sys.stderr)
        sys.exit(1)

    filtered = filter_patterns(patterns, pattern_id=args.pattern, form_factor=args.form_factor, src=args.src)
    if not filtered:
        print(f"No patterns matched (pattern={args.pattern!r}, form_factor={args.form_factor!r})")
        print("Available IDs:", ", ".join(p["id"] for p in patterns))
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    html = build_html(filtered, src_label=args.src or "")
    html_bytes = html.encode("utf-8")

    index_path = OUTPUT_DIR / "index.html"
    index_path.write_bytes(html_bytes)
    PreviewHandler.html_content = html_bytes
    PreviewHandler.feedback_path = OUTPUT_DIR / "feedback.json"

    httpd = HTTPServer(("", args.port), PreviewHandler)

    print(f"\nUX Preview Server")
    print(f"  URL      : http://localhost:{args.port}")
    print(f"  Patterns : {len(filtered)}")
    print(f"  Feedback : {OUTPUT_DIR / 'feedback.json'}")
    print(f"\nPress Enter to stop the server.\n")

    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

    print("Stopping server...")
    httpd.shutdown()

    feedback_path = OUTPUT_DIR / "feedback.json"
    if feedback_path.exists():
        with open(feedback_path) as f:
            votes = json.load(f)
        if votes:
            print(f"\nFeedback summary ({len(votes)} votes):")
            tally = {}
            for v in votes:
                pid = v.get("pattern_id", "?")
                direction = v.get("vote", "?")
                if pid not in tally:
                    tally[pid] = {"up": 0, "down": 0}
                tally[pid][direction] = tally[pid].get(direction, 0) + 1
            for pid, counts in tally.items():
                print(f"  {pid}: +{counts.get('up', 0)} / -{counts.get('down', 0)}")


if __name__ == "__main__":
    main()
