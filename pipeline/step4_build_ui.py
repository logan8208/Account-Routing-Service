"""Step 4 - build the rep-book web UI as ONE self-contained HTML file.

All data is embedded in the page and there are no external scripts, fonts or servers, so the file
works offline: download it from GitHub (or clone the repo) and double-click it. Nothing is deployed.

Reads  output/step1_accounts.json, step2_use_cases.json, step3_assignments.json,
       step3_capacity.json
Writes web_ui/rep_books.html
Run    python pipeline/step4_build_ui.py   (or python run.py for the whole pipeline)
"""
import datetime
import json
import sys
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import OUTPUT, ROOT  # noqa: E402

UI_DIR = ROOT / "web_ui"


def load(name):
    return json.loads((OUTPUT / name).read_text(encoding="utf-8"))


def build_data():
    s1 = load("step1_accounts.json")
    uc = {u["account_id"]: u for u in load("step2_use_cases.json")}
    asg = {g["account_id"]: g for g in load("step3_assignments.json")}
    cap = load("step3_capacity.json")
    by_id = {a["account_id"]: a for a in s1}
    accounts = []
    for a in s1:
        g, u = asg.get(a["account_id"]), uc.get(a["account_id"])
        accounts.append({
            "id": a["account_id"], "name": a["company_name"], "web": a["website"],
            "city": a["city"], "state": a["state"], "region": a["region"],
            "seg": (g or {}).get("segment") or a["segment"], "ind": a["industry"],
            "emp": a["employee_count"], "stage": a["funding_stage"], "year": a["last_funding_year"],
            "notes": a["entity_notes"] if a["is_primary"] else ([a["notes"]] if a["notes"] else []),
            "status": a["status"], "excl_codes": a["exclusion_codes"],
            "excl": a["exclusion_reason"], "flags": a["flags"], "entity": a["entity_id"],
            "parent": a["parent_account_id"],
            "parent_name": by_id[a["parent_account_id"]]["company_name"] if a["parent_account_id"] else "",
            "uc": (u or {}).get("use_case", ""), "uc_conf": (u or {}).get("confidence", ""),
            "uc_why": (u or {}).get("rationale", ""),
            "rep": (g or {}).get("rep_id", ""), "a_status": (g or {}).get("status", ""),
            "score": (g or {}).get("fit_score"), "breakdown": (g or {}).get("score_breakdown", ""),
            "rank": (g or {}).get("pool_rank"), "pool": (g or {}).get("pool_size"),
            "reason": (g or {}).get("reason", ""),
        })
    st = Counter(a["status"] for a in s1)
    summary = {
        "raw_rows": len(s1), "entities": len({a["entity_id"] for a in s1}),
        "eligible": st["eligible"], "excluded": st["excluded"], "merged": st["merged_duplicate"],
        "assigned": sum(1 for g in asg.values() if g["status"] == "assigned"),
        "left_over": sum(1 for g in asg.values() if g["status"] == "left_over"),
        "generated": datetime.date.today().isoformat(),
    }
    return {"accounts": accounts, "capacity": cap, "summary": summary}


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rep Books</title>
<style>
:root{--bg:#f7f7f5;--panel:#ffffff;--ink:#1d1d1b;--muted:#6b6b66;--line:#e3e2dd;--accent:#1f6f4a;
--accent-soft:#e2f0d9;--warn:#9a5b00;--warn-soft:#fff1d6;--bad:#a1302b;--bad-soft:#fbe4e2;--chip:#efeeea}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161615;--panel:#1f1f1d;--ink:#ecebe6;
--muted:#a3a29b;--line:#34332f;--accent:#6fcf97;--accent-soft:#1d3a2a;--warn:#f0b35a;--warn-soft:#3a2e17;
--bad:#f08a83;--bad-soft:#3d1f1d;--chip:#2a2a27}}
:root[data-theme="dark"]{--bg:#161615;--panel:#1f1f1d;--ink:#ecebe6;--muted:#a3a29b;--line:#34332f;
--accent:#6fcf97;--accent-soft:#1d3a2a;--warn:#f0b35a;--warn-soft:#3a2e17;--bad:#f08a83;--bad-soft:#3d1f1d;--chip:#2a2a27}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:20px 16px 0;max-width:1200px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--muted);font-size:13px}
nav{display:flex;gap:4px;flex-wrap:wrap;max-width:1200px;margin:16px auto 0;padding:0 16px;border-bottom:1px solid var(--line)}
nav button{background:none;border:0;border-bottom:2px solid transparent;padding:8px 10px;color:var(--muted);font:inherit;cursor:pointer}
nav button.on{color:var(--ink);border-color:var(--accent);font-weight:600}
main{max-width:1200px;margin:0 auto;padding:16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}
.card b{display:block;font-size:22px}
.card span{color:var(--muted);font-size:12px}
.note{background:var(--warn-soft);border-left:3px solid var(--warn);padding:10px 12px;border-radius:4px;margin:10px 0;font-size:14px}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 10px}
input,select{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink)}
input[type=search]{flex:1;min-width:180px}
.tablewrap{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--panel);font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}
tr:last-child td{border-bottom:0}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-block;background:var(--chip);border-radius:10px;padding:1px 8px;font-size:12px;white-space:nowrap}
.chip.good{background:var(--accent-soft);color:var(--accent)}
.chip.warn{background:var(--warn-soft);color:var(--warn)}
.chip.bad{background:var(--bad-soft);color:var(--bad)}
.co{font-weight:600}
.meta{color:var(--muted);font-size:12px}
details summary{cursor:pointer;color:var(--muted);font-size:12px}
.count{color:var(--muted);font-size:13px;margin:6px 2px}
.hidden{display:none}
.howto h3{margin:18px 0 6px;font-size:16px}
.howto table td{font-size:13px}
.theme{float:right;font-size:12px}
</style>
</head>
<body>
<header>
  <select class="theme" id="theme" aria-label="Theme"><option value="">Auto theme</option><option value="light">Light</option><option value="dark">Dark</option></select>
  <h1>Rep Books</h1>
  <div class="sub" id="sub"></div>
</header>
<nav id="nav"></nav>
<main id="main"></main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const A = D.accounts, CAP = D.capacity, S = D.summary;
const byId = Object.fromEntries(A.map(a => [a.id, a]));
const el = (t, attrs = {}, ...kids) => { const e = document.createElement(t);
  for (const [k, v] of Object.entries(attrs)) { if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else e.setAttribute(k, v); }
  for (const k of kids) if (k != null) e.append(k); return e; };
const fmt = n => n == null ? '' : n.toLocaleString('en-US');
const UC_LABEL = u => u ? u.replace(/_/g, ' ') : '';
const FLAG_TEXT = {
  employee_count_unknown: 'Employee count unknown', state_inferred_from_city: 'State filled from city — double-check',
  employee_count_vs_notes_conflict: 'Employee count conflicts with agent count in notes',
  data_conflict_churned_but_has_spend: 'Notes say churned but spend > $0 (treated as customer)',
  website_is_profile_page: 'Website is a LinkedIn/Twitter/Crunchbase page — domain needs enrichment',
  owner_decision_child_of_customer: 'Business unit of a customer (account management owns it)',
  merge_field_conflict: 'Merged records disagree on a field', duplicate_note_unresolved: '"Duplicate?" note, no duplicate found',
  parent_excluded_child_evaluated_alone: 'Parent excluded; judged on its own',
};
document.getElementById('sub').textContent =
  `${fmt(S.raw_rows)} CRM rows → ${fmt(S.entities)} companies · ${fmt(S.eligible)} eligible · ${fmt(S.assigned)} assigned to reps · ${fmt(S.left_over)} unassigned (books full) · ${fmt(S.excluded + S.merged)} excluded or merged · data built ${S.generated}`;

// ---------- theme (per-viewer convenience only)
const themeSel = document.getElementById('theme');
try { const t = localStorage.getItem('theme') || ''; themeSel.value = t; if (t) document.documentElement.dataset.theme = t; } catch (e) {}
themeSel.onchange = () => { const t = themeSel.value; if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
  try { localStorage.setItem('theme', t); } catch (e) {} };

// ---------- tabs
const TABS = [['overview', 'Overview'], ...CAP.map(c => [c.rep_id, c.rep_name.split(' ')[0] + ' · ' + c.region[0] + c.region.slice(1).toLowerCase() + ' ' + (c.segment === 'Enterprise' ? 'Ent' : 'MM')]),
  ['leftover', 'Unassigned'], ['excluded', 'Excluded & merged'], ['flags', 'Needs review'], ['how', 'How it works']];
const nav = document.getElementById('nav'), main = document.getElementById('main');
TABS.forEach(([id, label]) => nav.append(el('button', { 'data-tab': id, text: label })));
nav.onclick = e => { const b = e.target.closest('button'); if (b) show(b.dataset.tab); };
function show(id) { [...nav.children].forEach(b => b.classList.toggle('on', b.dataset.tab === id)); main.replaceChildren(RENDER[id] ? RENDER[id]() : RENDER.rep(id));
  try { history.replaceState(null, '', '#' + id); } catch (e) {} window.scrollTo(0, 0); }

// ---------- shared table with search + filters
function table(rows, cols, opts = {}) {
  const wrap = el('div'); const tools = el('div', { class: 'tools' });
  const q = el('input', { type: 'search', placeholder: opts.placeholder || 'Search company, notes, reason…', 'aria-label': 'Search' });
  tools.append(q);
  const filters = (opts.filters || []).map(([label, get]) => {
    const vals = [...new Set(rows.map(get).flat().filter(Boolean))].sort();
    const s = el('select', { 'aria-label': label }); s.append(el('option', { value: '', text: label + ': all' }));
    vals.forEach(v => s.append(el('option', { value: v, text: opts.labelFor ? opts.labelFor(v) : v }))); tools.append(s); return [s, get]; });
  const count = el('div', { class: 'count' }); const tw = el('div', { class: 'tablewrap' }); const t = el('table');
  const thead = el('thead'); const hr = el('tr'); cols.forEach(c => hr.append(el('th', { text: c[0] }))); thead.append(hr); t.append(thead);
  const tb = el('tbody'); t.append(tb); tw.append(t);
  function draw() {
    const needle = q.value.trim().toLowerCase();
    const shown = rows.filter(r => (!needle || (r.name + ' ' + r.id + ' ' + r.notes.join(' ') + ' ' + r.reason + ' ' + r.excl + ' ' + r.ind).toLowerCase().includes(needle))
      && filters.every(([s, get]) => !s.value || [].concat(get(r)).includes(s.value)));
    tb.replaceChildren(...shown.slice(0, 600).map(r => { const tr = el('tr'); cols.forEach(c => { const td = el('td', c[2] ? { class: c[2] } : {}); const v = c[1](r); td.append(v instanceof Node ? v : document.createTextNode(v ?? '')); tr.append(td); }); return tr; }));
    count.textContent = `${fmt(shown.length)} of ${fmt(rows.length)} shown` + (shown.length > 600 ? ' (first 600 — narrow the search to see more)' : '');
  }
  q.oninput = draw; filters.forEach(([s]) => s.onchange = draw); draw();
  wrap.append(tools, count, tw); return wrap;
}
const company = r => el('div', {}, el('div', { class: 'co', text: r.name }),
  el('div', { class: 'meta', text: [r.id, r.web, [r.city, r.state].filter(Boolean).join(', ')].filter(Boolean).join(' · ') }),
  r.parent ? el('div', { class: 'meta', text: 'Business unit of ' + r.parent_name + ' (' + r.parent + ')' }) : null);
const ucChip = r => r.uc ? el('span', { class: 'chip' + (r.uc === 'none' ? '' : ' good'), text: UC_LABEL(r.uc) }) : '';
const reasonCell = r => el('div', {}, el('div', { text: r.reason }), r.breakdown ? el('details', {}, el('summary', { text: 'Score breakdown' }), el('div', { class: 'meta', text: r.breakdown })) : null,
  r.flags.length ? el('div', {}, ...r.flags.map(f => el('span', { class: 'chip warn', text: FLAG_TEXT[f] || f }))) : null);

const RENDER = {
  overview() {
    const box = el('div');
    box.append(el('div', { class: 'cards' }, ...[[S.raw_rows, 'CRM rows in'], [S.entities, 'distinct companies'], [S.eligible, 'eligible'], [S.assigned, 'assigned to reps'],
      [S.left_over, 'unassigned — books full'], [S.excluded, 'excluded with a reason'], [S.merged, 'duplicate rows merged']].map(([n, l]) => el('div', { class: 'card' }, el('b', { text: fmt(n) }), el('span', { text: l })))));
    const short = CAP.filter(c => c.shortfall > 0), over = CAP.filter(c => c.left_over > 0);
    short.forEach(c => box.append(el('div', { class: 'note', text: `${c.rep_name} (${c.region} ${c.segment}) has ${c.shortfall} empty slots: only ${c.eligible_in_pool} eligible accounts exist in that region and segment. Per rules.md the book is not filled from another region or segment (owner decision D35).` })));
    const strong = A.filter(a => a.a_status === 'left_over' && a.score >= 60);
    if (strong.length) { const per = {}; strong.forEach(a => per[a.rep] = (per[a.rep] || 0) + 1);
      box.append(el('div', { class: 'note', text: `${strong.length} unassigned accounts score 60 or more but did not fit: ` + Object.entries(per).map(([r, n]) => `${n} in ${CAP.find(c => c.rep_id === r).rep_name}'s pool`).join(', ') + '. Worth a manager look (see the Unassigned tab).' })); }
    const tw = el('div', { class: 'tablewrap' }), t = el('table');
    const head = ['Rep', 'Region', 'Segment', 'Current book', 'Room (260 − current)', 'Eligible in pool', 'Assigned', 'New book', 'Left over', 'Shortfall', 'Lowest assigned score'];
    t.append(el('thead', {}, el('tr', {}, ...head.map(h => el('th', { text: h })))));
    t.append(el('tbody', {}, ...CAP.map(c => el('tr', {}, el('td', { class: 'co', text: c.rep_name }), el('td', { text: c.region }), el('td', { text: c.segment }),
      ...[c.current_book_size, c.room, c.eligible_in_pool, c.assigned, c.new_book_size, c.left_over, c.shortfall, c.lowest_assigned_score].map(v => el('td', { class: 'num', text: fmt(v) }))))));
    tw.append(t); box.append(el('h3', { text: 'Book capacity' }), tw);
    return box;
  },
  rep(id) {
    const c = CAP.find(x => x.rep_id === id);
    const rows = A.filter(a => a.rep === id && a.a_status === 'assigned').sort((x, y) => x.rank - y.rank);
    const box = el('div');
    box.append(el('h2', { text: `${c.rep_name} — ${c.region} ${c.segment}` }),
      el('div', { class: 'sub', text: `${c.assigned} new accounts assigned (book ${c.current_book_size} → ${c.new_book_size} of 260)` + (c.shortfall ? ` · ${c.shortfall} slots empty — region and segment exhausted` : ` · ${c.left_over} more eligible accounts did not fit (see Unassigned)`) }));
    box.append(table(rows, [['#', r => r.rank, 'num'], ['Company', company], ['Use case', ucChip], ['Score', r => r.score, 'num'], ['Why this account', reasonCell]],
      { filters: [['Use case', r => r.uc]], labelFor: UC_LABEL }));
    return box;
  },
  leftover() {
    const rows = A.filter(a => a.a_status === 'left_over').sort((x, y) => (x.rep > y.rep ? 1 : x.rep < y.rep ? -1 : x.rank - y.rank));
    const box = el('div'); box.append(el('h2', { text: 'Unassigned — the rep’s book was full' }),
      el('div', { class: 'sub', text: 'Eligible accounts ranked below the cut-off in their region and segment. They are not lost: they are the next in line if a book frees up.' }));
    box.append(table(rows, [['Pool rep', r => CAP.find(c => c.rep_id === r.rep).rep_name], ['#', r => r.rank, 'num'], ['Company', company], ['Use case', ucChip], ['Score', r => r.score, 'num'], ['Why not assigned', reasonCell]],
      { filters: [['Rep', r => CAP.find(c => c.rep_id === r.rep).rep_name], ['Use case', r => r.uc]], labelFor: v => UC_LABEL(v) }));
    return box;
  },
  excluded() {
    const rows = A.filter(a => a.status !== 'eligible');
    const box = el('div'); box.append(el('h2', { text: 'Excluded & merged' }),
      el('div', { class: 'sub', text: 'Every CRM row that is not in a rep’s book, with the reason. Nothing was dropped silently.' }));
    box.append(table(rows, [['Company', company], ['Status', r => el('span', { class: 'chip ' + (r.status === 'merged_duplicate' ? '' : 'bad'), text: r.status === 'merged_duplicate' ? 'merged duplicate' : 'excluded' })], ['Reason', r => el('div', {}, el('div', { text: r.excl }), el('div', { class: 'meta', text: r.notes.join(' / ') }))]],
      { filters: [['Status', r => r.status], ['Reason', r => r.excl_codes.split('; ')]], placeholder: 'Search company, reason…' }));
    return box;
  },
  flags() {
    const rows = A.filter(a => a.flags.length);
    const box = el('div'); box.append(el('h2', { text: 'Needs a human double-check' }),
      el('div', { class: 'sub', text: 'Data problems that were handled by a rule but are worth confirming.' }));
    box.append(table(rows, [['Company', company], ['Status', r => r.a_status ? (r.a_status === 'assigned' ? 'assigned to ' + CAP.find(c => c.rep_id === r.rep).rep_name : 'unassigned') : r.status.replace('_', ' ')],
      ['Flags', r => el('div', {}, ...r.flags.map(f => el('div', {}, el('span', { class: 'chip warn', text: FLAG_TEXT[f] || f }))))]],
      { filters: [['Flag', r => r.flags]], labelFor: v => FLAG_TEXT[v] || v }));
    return box;
  },
  how() {
    const box = el('div', { class: 'howto' });
    const t = (rows) => { const tw = el('div', { class: 'tablewrap' }), tb = el('table'); tb.append(el('tbody', {}, ...rows.map(r => el('tr', {}, ...r.map(c => el('td', { text: c })))))); tw.append(tb); return tw; };
    box.append(el('h2', { text: 'How the books were built' }),
      el('h3', { text: '1. Clean and de-duplicate' }), el('p', { text: 'Websites normalized to a bare domain. Rows with the same company domain, or notes saying "Billing domain for X", "Same company as X" or "Product brand of X", were merged into one company. LinkedIn/Twitter/Crunchbase links are never used to merge. Business units stay separate accounts and go to their parent’s rep.' }),
      el('h3', { text: '2. Eligibility (rules.md)' }), el('p', { text: 'Excluded: existing customers (any spend in the last 12 months, on any record of the company), under 20 employees, competitors whose core product is a speech engine, companies that no longer exist (shut down, parked domain, acquired), headquarters outside the team’s US/Canada territory, and business units of customers. Region comes from state/province, never from the country column.' }),
      el('h3', { text: '3. Use case' }), el('p', { text: 'One use case per company from its notes. A note that names a use case decides it; a note showing only speech interest uses the industry if it clearly implies one; otherwise "none". Hand check: 0 errors in a 150-company blind sample (95% CI 0–2.5%).' }),
      el('h3', { text: '4. Fit score (0–100)' }), t([['Notes name a speech use case', '35'], ['Notes show speech interest only', '20'], ['Buying intent (demo request 2025/26, evaluating vendors)', '+5'], ['Win-list industry / other industry', '25 / 5'],
        ['Employees 200–10,000 / 50–199 / 20–49 / over 10,000 / unknown', '20 / 12 / 6 / 8 / 4'], ['Funded 2025–26 / 2024', '15 / 8']]),
      el('h3', { text: '5. Assignment' }), el('p', { text: 'Each rep owns one region + segment (Enterprise = 500+ employees or Public / Private Equity). Room = 260 − current book. Highest scores first; ties broken by use-case confidence, then size, then funding year. A rep with room left is not filled from another region or segment; the shortfall is reported. Every reason is generated only from that account’s own data and checked by script.' }));
    return box;
  },
};
show((location.hash || '#overview').slice(1));
</script>
</body>
</html>
"""


def main():
    data = build_data()
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    UI_DIR.mkdir(exist_ok=True)
    out = UI_DIR / "rep_books.html"
    out.write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB, "
          f"{len(data['accounts'])} rows embedded)")


if __name__ == "__main__":
    main()
