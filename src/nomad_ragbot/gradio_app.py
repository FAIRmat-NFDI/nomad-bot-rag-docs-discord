"""Simple Gradio web interface for the LLM app.

Check out the documentation: https://www.gradio.app/docs/
Customize themes here: https://www.gradio.app/guides/theming-guide
"""

import os
from pathlib import Path
import gradio as gr

from nomad_ragbot.llm_client import generate_response


def create_gradio_app():
    """Create and launch Gradio app."""
    logo_path = Path(__file__).parents[2] / "assets" / "nomad.svg"
    
    nomad_css = """
    /* NOMAD brand colors */
    .nomad-primary {
        background-color: #1f4788 !important;
        border: 2px solid #1f4788 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    
    .nomad-primary:hover {
        background-color: #163659 !important;
        border-color: #163659 !important;
        box-shadow: 0 2px 8px rgba(31, 71, 136, 0.3) !important;
    }
    
    .nomad-secondary {
        background-color: #f7fafc !important;
        border: 2px solid #1f4788 !important;
        color: #1f4788 !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    
    .nomad-secondary:hover {
        background-color: #1f4788 !important;
        color: white !important;
    }

    #logo-image {
        border: none !important;
        box-shadow: none !important;
    }
    
    #logo-image .image-container {
        border: none !important;
    }
    
    /* Style the header row */
    .header-row {
        align-items: center !important;
        margin-bottom: 20px !important;
    }
    
    /* Make title blue */
    .header-title h1 {
        color: #1f4788 !important;
        margin: 0 !important;
    }
    """
    
    # Chat interface - IMPORTANT: Add css parameter here!
    with gr.Blocks(title="NOMAD", theme=gr.themes.Soft(), css=nomad_css) as app:
        
        # Header with logo using Gradio components
        with gr.Row(elem_classes=["header-row"]):
            with gr.Column(scale=1, min_width=70):
                if logo_path.exists():
                    gr.Image(
                        str(logo_path),
                        height=60,
                        width=60,
                        show_label=False,
                        show_download_button=False,
                        show_share_button=False,
                        interactive=False,  # This removes the zoom icon
                        container=False,
                        elem_id="logo-image"
                    )
                else:
                    gr.Image(
                        "https://nomad-lab.eu/assets/img/nomad-logo.png",
                        height=60,
                        width=60,
                        show_label=False,
                        show_download_button=False,
                        show_share_button=False,
                        interactive=False,  # This removes the zoom icon
                        container=False,
                        elem_id="logo-image"
                    )
            with gr.Column(scale=4, elem_classes=["header-title"]):
                gr.Markdown("# RAGalicious")
        
        gr.Markdown("Ask any question about NOMAD usage, you will master it in no time!")

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="Your Prompt",
                    placeholder="Enter your question here...",
                    lines=3,
                )
                submit_btn = gr.Button("Ask NOMAD!", elem_classes=["nomad-primary"])

        with gr.Row():
            with gr.Column():
                output_text = gr.Textbox(
                    label="RAGalicious Response:", lines=10, interactive=False
                )

        # Connect the button to the function
        submit_btn.click(fn=generate_response, inputs=input_text, outputs=output_text)

        # Example prompts
        gr.Examples(
            examples=[
                "Is NOMAD open source, or proprietory?",
                "Is there DFT data on NOMAD?",
                "Can I mine bitcoin on NOMAD?",
                "How is the weather in Hawaii?",
            ],
            inputs=input_text,
        )

    return app