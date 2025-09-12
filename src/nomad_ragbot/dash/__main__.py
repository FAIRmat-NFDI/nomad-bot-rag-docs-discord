# nomad_ragbot/dash/__main__.py
import sys
import subprocess
from pathlib import Path


def main():
    app_path = Path(__file__).with_name("streamlit_app.py")

    # Split sys.argv[1:] at the first "--"
    argv = sys.argv[1:]
    if "--" in argv:
        sep = argv.index("--")
        st_args = argv[:sep]  # goes to streamlit
        app_args = argv[sep + 1 :]  # goes to your argparse
    else:
        # No explicit separator given by the user
        # Heuristics: streamlit flags start with "--server." / "--client."
        st_args = [
            a for a in argv if a.startswith("--server.") or a.startswith("--client.")
        ]
        app_args = [a for a in argv if a not in st_args]

    cmd = ["streamlit", "run", str(app_path), *st_args, "--", *app_args]
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
