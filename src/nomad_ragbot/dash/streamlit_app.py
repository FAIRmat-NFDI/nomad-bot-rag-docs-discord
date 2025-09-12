import argparse, os, sys, json, gzip, re
import pandas as pd, numpy as np
import streamlit as st
from typing import List, Optional, Tuple
from urllib.parse import urlparse


# ----------------------------
# Args
# ----------------------------
def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--results_path",
        required=False,
        help="Path to eval results (.parquet | .csv | .jsonl | .jsonl.gz)",
    )
    parser.add_argument(
        "--gold_path",
        required=False,
        help="Optional path to gold_all.jsonl (to derive source_kind)",
    )
    args, _ = parser.parse_known_args()
    return args


# ----------------------------
# I/O
# ----------------------------
def _read_jsonl(path: str) -> pd.DataFrame:
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return pd.read_json(f, lines=True)
    return pd.read_json(path, lines=True)


@st.cache_data
def load_results(path: str) -> pd.DataFrame:
    p = path.lower()
    if p.endswith(".parquet"):
        df = pd.read_parquet(path)
    elif p.endswith(".csv"):
        df = pd.read_csv(path)
    elif p.endswith(".jsonl") or p.endswith(".jsonl.gz"):
        df = _read_jsonl(path)
    else:
        df = _read_jsonl(path)
    return _normalize_results_df(df)


@st.cache_data
def load_gold(gold_path: str) -> Optional[pd.DataFrame]:
    if not gold_path or not os.path.exists(gold_path):
        return None
    gdf = _read_jsonl(gold_path)
    return _normalize_gold_df(gdf)


def _maybe_find_gold_near(results_path: str) -> Optional[str]:
    if not results_path:
        return None
    d = os.path.dirname(results_path)
    for c in [
        os.path.join(d, "gold_all.jsonl"),
        os.path.join(os.path.dirname(d), "gold_all.jsonl"),
    ]:
        if os.path.exists(c):
            return c
    return None


# ----------------------------
# Helpers
# ----------------------------
_URL_RE = re.compile(r"https?://[^\s\]\)\"'>]+", re.IGNORECASE)
INVALID_STRINGS = {"", "nan", "none", "null", "unknown", "nat"}


def _first_url(text: Optional[str]) -> Optional[str]:
    if not isinstance(text, str) or not text.strip():
        return None
    m = _URL_RE.search(text)
    return m.group(0) if m else None


def _first_domain(text: Optional[str]) -> Optional[str]:
    u = _first_url(text)
    if not u:
        return None
    host = urlparse(u).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _best_existing(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _parse_meta(meta_val) -> dict:
    """Return dict for meta; accepts dict or JSON string; else {}."""
    if isinstance(meta_val, dict):
        return meta_val
    if isinstance(meta_val, str):
        s = meta_val.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                return json.loads(s)
            except Exception:
                return {}
    return {}


def _clean_label(v) -> Optional[str]:
    """Normalize to non-empty string or None, treating 'nan'/'none'/... as None."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    s = str(v).strip()
    return None if s.lower() in INVALID_STRINGS else s


def _norm_q(s: Optional[str]) -> Optional[str]:
    """Normalized question key for fallback joining when ids don't match."""
    if not isinstance(s, str):
        return None
    return re.sub(r"\s+", " ", s.lower()).strip() or None


# ----------------------------
# Normalizers
# ----------------------------
def _normalize_results_df(df: pd.DataFrame) -> pd.DataFrame:
    # id/idx → id (string)
    if "id" not in df.columns and "idx" in df.columns:
        df = df.rename(columns={"idx": "id"})
    elif "id" not in df.columns:
        df["id"] = np.arange(len(df)) + 1
    df["id"] = df["id"].astype(str).str.strip()

    # text fields
    df = df.rename(columns={"gold_answer": "gold", "model_answer": "pred"})
    for col in ["question", "gold", "pred"]:
        if col not in df.columns:
            df[col] = np.nan

    # normalized question key for joining when ids don't match
    df["qkey"] = df["question"].apply(_norm_q)

    # optional
    for col in ["citations", "error"]:
        if col not in df.columns:
            df[col] = np.nan

    # displayable citations
    if "citations" in df.columns:
        df["citations"] = df["citations"].apply(
            lambda x: x
            if isinstance(x, str)
            else (json.dumps(x, ensure_ascii=False) if pd.notna(x) else np.nan)
        )

    # metrics
    _coerce_numeric(
        df,
        [
            "f1",
            "em",
            "sim",
            "sem",
            "jaccard",
            "lev_ratio",
            "semantic_sim",
            "judge_score",
        ],
    )
    return df.sort_values("id").reset_index(drop=True)


def _normalize_gold_df(gdf: pd.DataFrame) -> pd.DataFrame:
    # --- Robust ID handling for mixed presence ---
    if "id" not in gdf.columns and "idx" in gdf.columns:
        gdf = gdf.rename(columns={"idx": "id"})
    elif "id" not in gdf.columns:
        gdf["id"] = np.arange(len(gdf)) + 1

    if "id" in gdf.columns:
        s = gdf["id"]
        is_missing = s.isna() | (s.astype(str).str.strip() == "")
        if is_missing.any():
            n = int(is_missing.sum())
            gdf.loc[is_missing, "id"] = [f"auto-{i}" for i in range(n)]

    gdf["id"] = gdf["id"].astype(str).str.strip()
    # ------------------------------------------------

    # question + qkey for fallback alignment
    if "question" not in gdf.columns:
        gdf["question"] = np.nan
    gdf["qkey"] = gdf["question"].apply(_norm_q)

    # Ensure 'meta' exists and extract meta.type / meta.method (cleaned)
    if "meta" not in gdf.columns:
        gdf["meta"] = None

    gdf["meta_type"] = gdf["meta"].apply(
        lambda v: _clean_label(_parse_meta(v).get("type"))
    )
    gdf["meta_method"] = gdf["meta"].apply(
        lambda v: _clean_label(_parse_meta(v).get("method"))
    )

    # Build source_kind with precedence: source → meta.type → meta.method
    if "source" in gdf.columns:
        src_series = gdf["source"].apply(_clean_label)
    else:
        src_series = pd.Series([None] * len(gdf))

    gdf["source_kind"] = src_series
    gdf["source_kind"] = gdf["source_kind"].where(
        gdf["source_kind"].notna(), gdf["meta_type"]
    )
    gdf["source_kind"] = gdf["source_kind"].where(
        gdf["source_kind"].notna(), gdf["meta_method"]
    )
    gdf["source_kind"] = gdf["source_kind"].fillna("unknown")

    # Optional sample URL/domain for the top table
    url_col = _best_existing(gdf, ["source_url", "gold_url", "url", "doc_url"])
    if url_col:
        gdf["_sample_url"] = gdf[url_col].astype(str)
    elif "citations" in gdf.columns:
        gdf["_sample_url"] = gdf["citations"].apply(_first_url)
    else:
        gdf["_sample_url"] = np.nan

    gdf["_sample_domain"] = gdf["_sample_url"].apply(
        lambda u: urlparse(u).netloc.lower()
        if isinstance(u, str) and u.startswith("http")
        else np.nan
    )

    return gdf[
        [
            "id",
            "qkey",
            "source_kind",
            "meta_type",
            "meta_method",
            "_sample_url",
            "_sample_domain",
        ]
    ].drop_duplicates()


def _attach_source_kind(
    df: pd.DataFrame, gdf: Optional[pd.DataFrame]
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    out = df.copy()
    out["id"] = out["id"].astype(str).str.strip()

    src_meta = None
    if gdf is not None:
        g = gdf.copy()
        g["id"] = g["id"].astype(str).str.strip()

        # Primary merge on id
        out = out.merge(g, on="id", how="left", suffixes=("", "_gold"))

        def first_non_null(s: pd.Series):
            return s.dropna().iloc[0] if s.notna().any() else np.nan

        # Corpus sources table (counts by source_kind)
        base = g.groupby("source_kind", dropna=False)
        src_meta = (
            base.size()
            .rename("n_items")
            .reset_index()
            .merge(
                base.agg(
                    sample_url=("_sample_url", first_non_null),
                    sample_domain=("_sample_domain", first_non_null),
                    meta_type=("meta_type", first_non_null),
                    meta_method=("meta_method", first_non_null),
                ).reset_index(),
                on="source_kind",
                how="left",
            )
            .sort_values("n_items", ascending=False)
            .reset_index(drop=True)
        )

        # ---- Fallback fill via qkey for rows still missing source_kind ----
        if "qkey" in out.columns:
            need = out["source_kind"].isna() | (out["source_kind"] == "")
            if need.any():
                q2_kind = (
                    g.dropna(subset=["qkey"])
                    .drop_duplicates(subset=["qkey"])
                    .set_index("qkey")["source_kind"]
                )
                q2_type = (
                    g.dropna(subset=["qkey"])
                    .drop_duplicates(subset=["qkey"])
                    .set_index("qkey")["meta_type"]
                )
                q2_method = (
                    g.dropna(subset=["qkey"])
                    .drop_duplicates(subset=["qkey"])
                    .set_index("qkey")["meta_method"]
                )

                out.loc[need, "source_kind"] = (
                    out.loc[need, "qkey"]
                    .map(q2_kind)
                    .fillna(out.loc[need, "source_kind"])
                )
                if "meta_type" in out.columns:
                    out.loc[need, "meta_type"] = (
                        out.loc[need, "qkey"]
                        .map(q2_type)
                        .fillna(out.loc[need, "meta_type"])
                    )
                if "meta_method" in out.columns:
                    out.loc[need, "meta_method"] = (
                        out.loc[need, "qkey"]
                        .map(q2_method)
                        .fillna(out.loc[need, "meta_method"])
                    )
        # ------------------------------------------------------------------

    # Ensure we always have a source_kind in results (fallback to domain from citations if needed)
    if "source_kind" not in out.columns:
        out["source_kind"] = np.nan

    needs = out["source_kind"].isna() | (out["source_kind"] == "")
    if needs.any() and "citations" in out.columns:
        out.loc[needs, "source_kind"] = out.loc[needs, "citations"].apply(
            lambda x: _first_domain(
                x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
            )
            or "unknown"
        )

    out["source_kind"] = out["source_kind"].fillna("unknown")
    return out, src_meta


# ----------------------------
# Run-level metadata
# ----------------------------
def _load_meta(results_path: str):
    if not results_path:
        return None
    d = os.path.dirname(results_path)
    meta_path = os.path.join(d, "config_snapshot.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


# ----------------------------
# App
# ----------------------------
def main():
    st.set_page_config(page_title="RAGBot Eval", layout="wide")
    st.title("📊 RAGBot — Evaluation Dashboard")

    args = get_args()
    if not args.results_path:
        st.error(
            "⚠️ Please provide `--results_path path/to/file.jsonl` when starting the app."
        )
        st.stop()

    df = load_results(args.results_path)
    gold_path = args.gold_path or _maybe_find_gold_near(args.results_path)
    gdf = load_gold(gold_path) if gold_path else None

    # Attach source_kind (source → meta.type → meta.method), with fallbacks + qkey
    df, src_meta = _attach_source_kind(df, gdf)

    # Run metadata (expander)
    meta = _load_meta(args.results_path)
    with st.expander("Run metadata", expanded=False):
        st.json(meta or {"info": "no metadata found"})

    # Corpus sources (by source_kind)
    st.subheader("Corpus sources")
    if src_meta is not None and not src_meta.empty:
        st.dataframe(src_meta, width="stretch")
        corpus_kinds = src_meta["source_kind"].astype(str).tolist()
    else:
        counts = (
            df["source_kind"]
            .value_counts(dropna=False)
            .rename_axis("source_kind")
            .reset_index(name="n_items")
        )
        st.dataframe(counts, width="stretch")
        corpus_kinds = counts["source_kind"].astype(str).tolist()

    # Sidebar filters
    st.sidebar.header("Filters")
    # Keep sidebar kinds aligned with corpus table, but only those present in results to avoid empty selection
    present = set(df["source_kind"].dropna().astype(str).unique().tolist())
    kinds = [k for k in corpus_kinds if k in present]
    selected_kinds = st.sidebar.multiselect(
        "Source types (source_kind)", kinds, default=kinds
    )

    # Metrics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    preferred = [
        "sem",
        "f1",
        "em",
        "sim",
        "semantic_sim",
        "judge_score",
        "jaccard",
        "lev_ratio",
    ]
    metrics_available = [m for m in preferred if m in numeric_cols] or numeric_cols
    metric = st.sidebar.selectbox(
        "Metric", metrics_available or ["f1"], index=0 if metrics_available else 0
    )
    threshold = st.sidebar.slider("Pass threshold", 0.0, 1.0, 0.7, 0.01)
    search = st.sidebar.text_input("Search in question", "")

    # Apply filters
    fdf = df.copy()
    if selected_kinds:
        fdf = fdf[fdf["source_kind"].astype(str).isin(selected_kinds)]
    if search:
        fdf = fdf[
            fdf["question"].astype(str).str.contains(search, case=False, na=False)
        ]

    st.markdown(f"**Rows:** {len(fdf)}")

    import altair as alt  # add at top

    # ----- Charts -----
    if metric in fdf.columns and not fdf.empty:
        st.subheader("Score by index")

        s = fdf.reset_index()[[metric]]
        s = s.reset_index().rename(columns={"index": "row"})

        chart = (
            alt.Chart(s)
            .mark_bar()
            .encode(
                x="row:O",
                y=alt.Y(f"{metric}:Q", scale=alt.Scale(domain=[0, 1])),
                tooltip=[metric],
            )
        )

        threshold_line = (
            alt.Chart(pd.DataFrame({"y": [threshold]}))
            .mark_rule(
                color="#ff0000", strokeDash=[4, 4], size=3
            )  # bright red, thicker
            .encode(y="y:Q")
        )

        st.altair_chart(chart + threshold_line, use_container_width=True)

        st.subheader("Score distribution")
        vals = fdf[metric].dropna().astype(float)
        if not vals.empty:
            bins = np.linspace(0.0, 1.0, 21)
            counts, edges = np.histogram(vals.values, bins=bins)
            centers = (edges[:-1] + edges[1:]) / 2.0
            hist_df = pd.DataFrame({"score": centers, "count": counts})

            # hist_chart = alt.Chart(hist_df).mark_bar().encode(x="score:Q", y="count:Q")
            # st.altair_chart(hist_chart, use_container_width=True)
            hist_chart = (
                alt.Chart(hist_df)
                .mark_bar(color="#8fb1d6", width=50)  # wider bars, custom color
                .encode(
                    x=alt.X("score:Q", bin=alt.Bin(maxbins=20), title="Score"),
                    y=alt.Y("count:Q", title="Count"),
                )
            )
            st.altair_chart(hist_chart, use_container_width=True)

    # ----- Details -----
    st.subheader("Details")
    id_col = "id" if "id" in fdf.columns else _best_existing(fdf, ["idx"])

    # Passed column (boolean) based on threshold
    if metric in fdf.columns:
        passed_bool = (fdf[metric] >= threshold).fillna(False)
        fdf = fdf.assign(passed=passed_bool)
    else:
        fdf = fdf.assign(passed=np.nan)

    cols = [
        c
        for c in [
            id_col,
            "source_kind",
            "meta_type",
            "meta_method",
            "question",
            "gold",
            "pred",
            "citations",
            "error",
            "passed",
            metric if metric in fdf.columns else None,
        ]
        if c and c in fdf.columns
    ]
    display_df = fdf[cols].rename(columns={id_col or "id": "id"})

    cfg = {}
    if "passed" in display_df.columns:
        cfg["passed"] = st.column_config.CheckboxColumn(
            "passed", help="Metric ≥ threshold", disabled=True
        )

    st.dataframe(display_df, width="stretch", height=520, column_config=cfg)

    st.caption(f"Gold file used: {gold_path if gold_path else '(not found)'}")


def main_entry():
    main()


if __name__ == "__main__":
    main()
