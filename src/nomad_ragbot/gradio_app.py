# src/nomad_ragbot/gradio_app.py

import base64
from pathlib import Path
import gradio as gr
from nomad_ragbot.llm_client import generate_response


def _logo_src() -> str:
    logo_path = Path(__file__).parents[2] / "assets" / "nomad.svg"
    if logo_path.exists():
        try:
            data = base64.b64encode(logo_path.read_bytes()).decode()
            return f"data:image/svg+xml;base64,{data}"
        except Exception:
            pass
    return "https://nomad-lab.eu/assets/img/nomad-logo.png"


NOMAD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');

/* Dark palette */
:root {
  --bg:#0b1220; --panel:#111a2e; --panel-2:#0e1729;
  --border:#1e2a47; --text:#e6edf7; --muted:#9fb0d3;
  --nomad-primary:#4b7bff; --nomad-primary-dark:#375dcc;
}

html, body, .gradio-container {
  background:var(--bg)!important;
  color:var(--text)!important;
  font-family:'Titillium Web',ui-sans-serif,system-ui,sans-serif!important;
  font-size:18px; line-height:1.6;
  max-width:1200px!important;
  margin:0 auto!important;
}

/* Header row: logo + title + subheader inline */
.nomad-header {
  display:flex; align-items:center; gap:18px;
  margin:12px 0 28px 0;
}
.nomad-header img {
  height:56px; width:auto;
}
.nomad-title {
  margin:0;
  font-weight:700;
  font-size:2.2rem;
  color:#c9d6ff; /* light bluish text */
}
.nomad-subheader {
  font-size:1.3rem; font-weight:500; color:var(--muted);
  margin-left:12px;
}

/* Inputs */
.nomad-input textarea {
  background:var(--panel)!important;
  color:var(--text)!important;
  border:1px solid var(--border)!important;
  border-radius:12px!important;
  font-size:18px;
}

/* Buttons */
.nomad-primary {
  background:linear-gradient(135deg,var(--nomad-primary) 0%,var(--nomad-primary-dark) 100%)!important;
  border:none!important; color:white!important; font-weight:600!important;
  border-radius:10px!important; padding:12px 20px!important;
  box-shadow:0 4px 12px rgba(75,123,255,.25)!important;
  transition:transform .2s ease;
}
.nomad-primary:hover { transform:translateY(-1px); }
.nomad-secondary {
  background:var(--panel)!important; color:var(--text)!important;
  border:1px solid var(--border)!important; border-radius:10px!important;
}

/* Free-floating outputs */
.answer-box, .citations-box {
  background:transparent!important; border:none!important;
  padding:0!important; margin:0 0 18px 0!important;
}
.citations-box { color:var(--muted)!important; }

/* Status */
.status-box { color:var(--muted)!important; font-style:italic; min-height:1.2em; }

/* Strip default boxes */
div[class*="block"], div[class*="panel"], .container, .tabs, .tabitem {
  background:transparent!important; border-color:transparent!important;
}
"""


def create_gradio_app():
    logo_src = _logo_src()

    with gr.Blocks(
        title="RAGBOT for AI Assistance with Citations",
        theme=gr.themes.Soft(
            primary_hue="blue", secondary_hue="slate", neutral_hue="slate"
        ),
        css=NOMAD_CSS,
    ) as app:
        # Header: logo left, title + subheader inline
        gr.HTML(
            f"""
            <div class="nomad-header">
              <img src="{logo_src}" alt="NOMAD Logo">
              <h1 class="nomad-title">RAGBOT: AI Assistance with Citations</h1>
            </div>
            """
        )
        #   <div class="nomad-subheader">Advanced AI Assistant for the NOMAD knowledge base</div>

        with gr.Row():
            with gr.Column(scale=2):
                input_text = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask about NOMAD features, docs, troubleshooting, or best practices…",
                    lines=4,
                    elem_classes=["nomad-input"],
                    show_label=True,
                )
                with gr.Row():
                    submit_btn = gr.Button(
                        "Ask NOMAD Assistant", elem_classes=["nomad-primary"]
                    )
                    clear_btn = gr.Button("Clear", elem_classes=["nomad-secondary"])
                status_md = gr.Markdown("", elem_classes=["status-box"])

            with gr.Column(scale=3):
                answer_md = gr.Markdown(label=None, elem_classes=["answer-box"])
                citations_md = gr.Markdown(label=None, elem_classes=["citations-box"])

        def _run(prompt: str):
            yield "", "", "⏳ Processing…"
            answer, cites = generate_response(prompt)
            yield answer, cites, ""

        submit_btn.click(
            fn=_run, inputs=input_text, outputs=[answer_md, citations_md, status_md]
        )
        input_text.submit(
            fn=_run,
            inputs=input_text,
            outputs=[answer_md, citations_md, status_md],
        )
        clear_btn.click(
            fn=lambda: ("", "", ""), outputs=[input_text, answer_md, citations_md]
        ).then(lambda: "", outputs=status_md)

        gr.Markdown("### Try these examples:")
        gr.Examples(
            examples=[
                "What is NOMAD?",
                "Does NOMAD support experimental measurement data and ELNs?",
                "What makes NOMAD different from other materials databases?",
                "What file formats does NOMAD support?",
                "How can I search for specific material properties in NOMAD?",
            ],
            inputs=input_text,
            examples_per_page=5,
        )

    return app


def main():
    app = create_gradio_app()
    app.launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
