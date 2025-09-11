import argparse, os, json
import pandas as pd, numpy as np
import streamlit as st

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_path", required=True, help="Path to eval_results.parquet or .csv")
    return parser.parse_args(parser.parse_known_args()[1])[0]

@st.cache_data
def load_results(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)

def _load_meta(results_path: str):
    d = os.path.dirname(results_path)
    meta_path = os.path.join(d, "config_snapshot.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def main():
    st.set_page_config(page_title="RAGBot Eval", layout="wide")
    st.title("📊 RAGBot — Evaluation Dashboard")
    args = get_args()
    df = load_results(args.results_path)

    meta = _load_meta(args.results_path)
    with st.expander("Run metadata", expanded=False):
        st.json(meta or {"info": "no metadata found"})

    # Sidebar filters
    st.sidebar.header("Filters")
    sources = sorted(df["source"].dropna().unique().tolist())
    selected_sources = st.sidebar.multiselect("Source types", sources, default=sources)
    metric = st.sidebar.selectbox("Metric", ["f1", "em", "jaccard", "lev_ratio", "semantic_sim", "judge_score"])
    threshold = st.sidebar.slider("Pass threshold", 0.0, 1.0, 0.7, 0.01)
    search = st.sidebar.text_input("Search in question", "")

    fdf = df[df["source"].isin(selected_sources)]
    if search:
        fdf = fdf[fdf["question"].str.contains(search, case=False, na=False)]

    st.markdown(f"**Rows:** {len(fdf)}")

    # Summary by source
    if metric not in fdf.columns:
        st.warning(f"Metric '{metric}' not found in results.")
    else:
        by_src = (
            fdf.groupby("source")[metric]
            .agg(["count", "mean", lambda s: (s >= threshold).mean() if s.notna().any() else np.nan])
            .rename(columns={"<lambda_0>": f"pass@{threshold:.2f}"})
            .reset_index()
            .sort_values("mean", ascending=False)
        )
        st.subheader("By Source")
        st.dataframe(by_src, use_container_width=True)

        st.subheader("Distribution")
        st.bar_chart(fdf[[metric]].dropna())

    # Detailed table
    st.subheader("Details")
    cols = ["id", "source", "question", "gold_answer", "model_answer"]
    if metric in fdf.columns:
        cols.append(metric)
    st.dataframe(fdf[cols], use_container_width=True, height=420)

def main_entry():
    main()

if __name__ == "__main__":
    main()
