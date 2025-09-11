import nbformat as nbf
from pathlib import Path
from textwrap import dedent

nb = nbf.v4.new_notebook()
nb.cells = []

nb.cells.append(nbf.v4.new_markdown_cell(dedent("""
# NOMAD RAG — Gold Q&A Reviewer (v2)

This notebook lets you **review** harvested Q&A candidates (`eval/gold_review.csv`),
preview their answers, and promote them into `eval/gold_nomad.jsonl`.

### Features
- Filter by score, method, search text  
- Preview full Q & A with source links  
- Add selected items to gold (deduplicated)  
- Automatic summary of gold set
""")))

nb.cells.append(nbf.v4.new_code_cell(dedent("""
import os, json, re
from pathlib import Path
import pandas as pd
from IPython.display import display, Markdown, HTML
import ipywidgets as W

# ---- Paths ----
CANDIDATE_CSV = Path("eval/gold_review.csv")
GOLD_JSONL    = Path("eval/gold_nomad.jsonl")
GOLD_JSONL.parent.mkdir(parents=True, exist_ok=True)

if not CANDIDATE_CSV.exists():
    raise FileNotFoundError(f"Candidate CSV not found: {CANDIDATE_CSV.resolve()}")

df_all = pd.read_csv(CANDIDATE_CSV)

required = {"question","proposed_answer","source_url","title","section","method","score","id"}
if missing := (required - set(df_all.columns)):
    raise ValueError(f"Candidate CSV missing columns: {missing}")

def load_gold(path: Path):
    if not path.exists(): return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

gold_list = load_gold(GOLD_JSONL)

def norm_question(q: str) -> str:
    q = (q or "").lower().strip()
    q = re.sub(r"\\s+", " ", q)
    q = re.sub(r"[^\\w\\s\\?\\-]", "", q)
    return q

existing_keys = {(norm_question(r.get("question","")), r.get("source_url","")) for r in gold_list}

print(f"Loaded {len(df_all)} candidates")
print(f"Loaded {len(gold_list)} existing gold entries from {GOLD_JSONL}")
""")))

nb.cells.append(nbf.v4.new_code_cell(dedent("""
# ---------- Widgets ----------
min_score = W.FloatSlider(value=0.55, min=0.0, max=1.0, step=0.05, description="Min score")
method_opts = ["(any)"] + sorted(df_all["method"].dropna().unique().tolist())
method_dd = W.Dropdown(options=method_opts, value="(any)", description="Method")
search_box = W.Text(value="", description="Search")
refresh_btn = W.Button(description="Refresh")
select_box = W.SelectMultiple(options=[], rows=12, description="Select")
add_btn = W.Button(description="Add to Gold", button_style="success")
status_out = W.Output()
preview_out = W.Output()
gold_summary_out = W.Output()

def format_option(row):
    q_short = (row["question"][:96] + "…") if len(row["question"]) > 100 else row["question"]
    return f"[{row['score']:.2f}] {row['method']}: {q_short}  —  ({row['title']} › {row['section']})"

def filtered_df():
    df = df_all.copy()
    df = df[df["score"] >= float(min_score.value)]
    if method_dd.value != "(any)":
        df = df[df["method"] == method_dd.value]
    q = search_box.value.strip().lower()
    if q:
        mask = (
            df["question"].str.lower().str.contains(q, na=False) |
            df["proposed_answer"].str.lower().str.contains(q, na=False) |
            df["title"].str.lower().str.contains(q, na=False) |
            df["section"].str.lower().str.contains(q, na=False)
        )
        df = df[mask]
    return df

def apply_filter(_=None):
    df = filtered_df()
    select_box.options = [(format_option(row), row["id"]) for _, row in df.iterrows()]
    with status_out:
        status_out.clear_output()
        print(f"Filtered candidates: {len(df)}")
    update_preview()

def update_preview(_=None):
    df = filtered_df()
    idx = {row["id"]: row for _, row in df.iterrows()}
    chosen = list(select_box.value)[:5]
    with preview_out:
        preview_out.clear_output()
        if not chosen:
            display(Markdown("> Select candidates to preview…"))
            return
        for cid in chosen:
            row = idx.get(cid)
            if row is None: continue
            html = f\"\"\"
            <div style='border:1px solid #ddd; padding:10px; margin:8px 0; border-radius:8px'>
              <b>Question:</b> {row['question']}<br/><br/>
              <b>Proposed answer:</b><br/>{row['proposed_answer']}<br/><br/>
              <b>Source:</b> <a href='{row['source_url']}' target='_blank'>{row['title']} › {row['section']}</a>
              &nbsp; | &nbsp; <i>{row['method']}</i> score={row['score']:.2f}
            </div>
            \"\"\"
            display(HTML(html))

def show_gold_summary():
    if GOLD_JSONL.exists():
        with GOLD_JSONL.open("r", encoding="utf-8") as f:
            gold = [json.loads(line) for line in f if line.strip()]
    else:
        gold = []
    with gold_summary_out:
        gold_summary_out.clear_output()
        display(Markdown(f"**Gold entries:** {len(gold)}"))
        if gold:
            gdf = pd.DataFrame(gold)
            display(gdf[["question","gold_urls"]].head(10))

def add_selected_to_gold(_):
    df = filtered_df()
    by_id = {row["id"]: row for _, row in df.iterrows()}
    picked_ids = list(select_box.value)
    if not picked_ids:
        with status_out:
            status_out.clear_output()
            display(Markdown("⚠️ **No candidates selected.**"))
        return

    added = []
    new_recs = []
    for cid in picked_ids:
        row = by_id.get(cid)
        if row is None: continue
        key = (norm_question(row["question"]), row["source_url"])
        if key in existing_keys: continue
        rec = {
            "question": row["question"],
            "gold_answer": row["proposed_answer"],
            "gold_urls": [row["source_url"]],
            "title": row.get("title",""),
            "section": row.get("section",""),
            "source_url": row["source_url"],
            "meta": {"method": row.get("method",""), "score": float(row.get("score",0)), "id": row.get("id","")}
        }
        new_recs.append(rec)
        added.append(row["question"])
        existing_keys.add(key)

    if new_recs:
        with GOLD_JSONL.open("a", encoding="utf-8") as f:
            for r in new_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\\n")

    with status_out:
        status_out.clear_output()
        if new_recs:
            items = "<br/>".join("• " + q for q in added[:5])
            more = "" if len(added) <= 5 else f"<br/>… and {len(added)-5} more"
            display(HTML(f"<div style='background:#e9f7ef;border-left:6px solid #2ecc71;padding:10px'>"
                         f"<b>Added {len(added)}</b> entries to <code>{GOLD_JSONL}</code>.<br/>{items}{more}</div>"))
        else:
            display(HTML("<div style='background:#fdecea;border-left:6px solid #e74c3c;padding:10px'>Nothing added (all duplicates).</div>"))
    show_gold_summary()

# wiring
refresh_btn.on_click(apply_filter)
select_box.observe(update_preview, names="value")
add_btn.on_click(add_selected_to_gold)

display(W.HBox([min_score, method_dd, search_box, refresh_btn]))
display(W.HBox([W.VBox([select_box, add_btn, status_out]), W.VBox([preview_out])]))
display(W.HTML("<hr/>"))
display(gold_summary_out)

apply_filter()
show_gold_summary()
""")))

# Save
out_path = Path("nomad_gold_reviewer_v2.ipynb")
out_path.write_text(nbf.writes(nb), encoding="utf-8")
print(f"Notebook written to {out_path.resolve()}")

