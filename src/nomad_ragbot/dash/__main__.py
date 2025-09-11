import sys
import subprocess
from pathlib import Path

def main():
    app_path = Path(__file__).with_name("streamlit_app.py")
    cmd = ["streamlit", "run", str(app_path), "--", *sys.argv[1:]]
    raise SystemExit(subprocess.call(cmd))

if __name__ == "__main__":
    main()

