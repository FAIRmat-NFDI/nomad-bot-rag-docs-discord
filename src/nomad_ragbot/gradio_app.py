"""Simple Gradio web interface for the LLM app."""

import os
from pathlib import Path
import gradio as gr
import base64

from nomad_ragbot.llm_client import generate_response


def create_gradio_app():
    """Create and launch Gradio app."""
    logo_path = Path(__file__).parents[2] / "assets" / "nomad.svg"

    # Convert logo to base64 for HTML use
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            logo_src = f"data:image/svg+xml;base64,{logo_data}"
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_src = "https://nomad-lab.eu/assets/img/nomad-logo.png"
    else:
        logo_src = "https://nomad-lab.eu/assets/img/nomad-logo.png"
    
    nomad_css = """
    /* NOMAD Corporate Colors */
    :root {
        --nomad-primary: #1f4788;
        --nomad-primary-dark: #163659;
        --nomad-secondary: #2d5aa0;
        --nomad-accent: #4a90a4;
        --nomad-light: #f8fafc;
        --nomad-gray: #64748b;
        --nomad-white: #ffffff;
    }

    /* Global styling */
    .gradio-container {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Header styling */
    .nomad-header {
        background: linear-gradient(135deg, var(--nomad-light) 0%, var(--nomad-white) 100%);
        padding: 30px 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(31, 71, 136, 0.1);
        border: 1px solid rgba(31, 71, 136, 0.1);
    }

    .nomad-header h1 {
        background: linear-gradient(135deg, var(--nomad-primary) 0%, var(--nomad-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .nomad-subtitle {
        color: var(--nomad-gray);
        font-size: 1.3em;              /* Increased from 1.1em */
        font-weight: 600;              /* Changed from 400 to 600 (bold) */
        margin-top: 20px;              /* Increased from 10px */
        line-height: 1.6;
    }
    
    /* Button styling */
    .nomad-primary {
        background: linear-gradient(135deg, var(--nomad-primary) 0%, var(--nomad-secondary) 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(31, 71, 136, 0.2) !important;
    }
    
    .nomad-primary:hover {
        background: linear-gradient(135deg, var(--nomad-primary-dark) 0%, var(--nomad-primary) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(31, 71, 136, 0.3) !important;
    }
    
    /* Input styling */
    .nomad-input textarea {
        border: 2px solid rgba(31, 71, 136, 0.1) !important;
        border-radius: 8px !important;
        transition: border-color 0.3s ease !important;
    }
    
    .nomad-input textarea:focus {
        border-color: var(--nomad-primary) !important;
        box-shadow: 0 0 0 3px rgba(31, 71, 136, 0.1) !important;
    }
    
    /* Output styling */
    .nomad-output {
        background: var(--nomad-light) !important;
        border: 1px solid rgba(31, 71, 136, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Examples styling */
    .nomad-examples {
        background: var(--nomad-white);
        border-radius: 12px;
        padding: 20px;
        margin-top: 30px;
        border: 1px solid rgba(31, 71, 136, 0.1);
        box-shadow: 0 2px 8px rgba(31, 71, 136, 0.05);
    }
    
    /* Footer styling */
    .nomad-footer {
        margin-top: 40px;
        padding: 20px;
        text-align: center;
        color: var(--nomad-gray);
        font-size: 0.9em;
        border-top: 1px solid rgba(31, 71, 136, 0.1);
    }
    
    .nomad-footer a {
        color: var(--nomad-primary);
        text-decoration: none;
        font-weight: 500;
    }
    
    .nomad-footer a:hover {
        text-decoration: underline;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .nomad-header {
            padding: 20px 15px;
        }
        
        .nomad-header h1 {
            font-size: 2em !important;
        }
    }
    """
    
    with gr.Blocks(
        title="NOMAD RAGalicious", 
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
        ), 
        css=nomad_css
    ) as app:
        
        # Professional header
        gr.HTML(f"""
            <div class="nomad-header">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <img src="{logo_src}" 
                         alt="NOMAD Logo" 
                         style="height: 50px; width: auto;">
                    <div>
                        <h1 style="margin: 0; font-size: 2.5em;">
                            RAGalicious NOMAD
                        </h1>
                        <div class="nomad-title">
                            Advanced AI Assistant for NOMAD Knowledge Base
                        </div>
                    </div>
                </div>
            </div>
        """)

        with gr.Row():
            with gr.Column(scale=2):
                input_text = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask about NOMAD features, documentation, troubleshooting, or best practices...",
                    lines=4,
                    elem_classes=["nomad-input"]
                )
                
                with gr.Row():
                    submit_btn = gr.Button(
                        "Ask NOMAD Assistant", 
                        elem_classes=["nomad-primary"],
                        size="lg"
                    )
                    clear_btn = gr.Button(
                        "Clear", 
                        elem_classes=["nomad-secondary"],
                        size="lg"
                    )

            with gr.Column(scale=3):
                output_text = gr.Textbox(
                    label="NOMAD Assistant Response",
                    lines=12,
                    interactive=False,
                    elem_classes=["nomad-output"]
                )

        # Enhanced examples section
        gr.HTML("""
            <div class="nomad-examples">
                <h3 style="color: #1f4788; margin-top: 0;">Try these example questions:</h3>
            </div>
        """)
        
        gr.Examples(
            examples=[
                "What makes NOMAD different from other materials databases?",
                "How do I upload and publish my DFT calculations?",
                "What file formats does NOMAD support for experimental data?",
                "How can I search for specific material properties in NOMAD?",
                "What are the best practices for data organization in NOMAD?",
                "How do I cite NOMAD data in my publications?"
            ],
            inputs=input_text,
            examples_per_page=3
        )

        # Professional footer
        gr.HTML(f"""
            <div class="nomad-footer">
                <p>
                    Powered by <a href="https://nomad-lab.eu" target="_blank">NOMAD Laboratory</a> | 
                    <a href="https://fairmat-nfdi.eu" target="_blank">FAIRmat NFDI</a> | 
                    Built with ❤️ for the materials science community
                </p>
                <p style="font-size: 0.8em; margin-top: 10px;">
                    This AI assistant is designed to help with NOMAD-related questions. 
                    For official support, visit the <a href="https://nomad-lab.eu/nomad-lab/documentation.html" target="_blank">NOMAD documentation</a>.
                </p>
            </div>
        """)

        # Event handlers
        submit_btn.click(
            fn=generate_response, 
            inputs=input_text, 
            outputs=output_text
        )
        
        clear_btn.click(
            fn=lambda: ("", ""),
            outputs=[input_text, output_text]
        )
        
        # Enter key submission
        input_text.submit(
            fn=generate_response,
            inputs=input_text,
            outputs=output_text
        )

    return app