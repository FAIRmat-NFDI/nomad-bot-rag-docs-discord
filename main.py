"""Simple entry point for the LLM Gradio app."""

from nomad_ragbot import create_gradio_app

if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(share=False)
