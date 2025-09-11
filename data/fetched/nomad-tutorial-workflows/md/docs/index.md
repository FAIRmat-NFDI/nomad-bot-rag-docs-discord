# Workflow and Project Management with NOMAD

## 🧭 What You Will Learn

- Organize and manage complex research workflows using NOMAD
- Integrate diverse data sources into a single, reproducible project
- Track data provenance and metadata
- Interface with the NOMAD repository programmatically for automation and high-throughput use

## 📌 Prerequisites

This tutorial supports both **graphical (GUI)** and **programmatic (Python/CLI)** workflows.

### Required

- 🌐 **NOMAD account**
  Free registration is required to upload and manage data

### Recommended (for efficiency and automation)

- 💻 **Terminal environment**
  Install the workflow utility module via Bash (Linux/macOS) or PowerShell (Windows)

- 🐍 **Basic Python knowledge**
  Utilize workflow utility tools using provided Jupyter notebooks

!!! tip "Can't code? No problem."
    You can complete the tutorial entirely using the :

    - Use provided templates to create input files manually
    - Upload and manage workflows via NOMAD's web interface
    - Skip all Python- and Jupyter-related steps

    ⚠️ Some tasks may be **more manual and time-consuming**, but all core functionality is accessible without programming.

---

## ⚙️ Tutorial Preparation

### 1. Create a NOMAD account at [NOMAD Test Deployment](https://nomad-lab.eu/prod/v1/test/gui/about/information){:target="\_blank"}

Click `LOGIN/REGISTER` at the top right.

!!! warning "Attention"
    This entire tutorial will us the **test deployment**. When you are ready to upload and share your real data with the public, use the [NOMAD Central Deployment](https://nomad-lab.eu/prod/v1/gui/about/information){:target="\_blank"}.


### 2. Install the nomad-utility-workflows module

Open a terminal and create a virtual environment with python==3.11 (It may be possible to use python>=3.9, but the module has only been fully tested with 3.11):

=== "macOS and Linux"

    ```console
    python3.11 -m venv .pyenv
    ```

=== "Windows PowerShell"

    ```console
    py -3.11 -m venv .pyenv
    ```

??? tip "Install missing Python 3.11 interpreter"
    To install Python 3.11 interpreter:

    === "Debian Linux"

    ```console
    sudo apt install python3.11
    ```
    === "Red Hat Linux"

    ```console
    sudo dnf install python3.11
    ```
    === "macOS"

    ```console
    brew install python@3.11
    ```
    === "Windows PowerShell"
    Download the installer from the [official Python website](https://www.python.org/downloads/release/python-3110/) and run it.
    Make sure to check the box that says "Add Python 3.11 to PATH" during installation.

Activate the Python virtual environment:

=== "macOS and Linux"

    ```console
    . .pyenv/bin/activate
    ```

=== "Windows PowerShell"

    ```console
    .pyenv\Scripts\activate
    ```

Upgrade pip and install uv (recommended):

```sh
pip install --upgrade pip
pip install uv
```

Install the latest pypi version of the plugin using pip:

```bash
uv pip install "nomad-utility-workflows[vis]>=0.2.0"
```

Install `python-dotenv` package.
In order to use a Jupyter notebook in the following, install ipython and then create a Jupyter kernel for this venv (this kernel can then be be identified and loaded into your IDE):

```bash
uv pip install python-dotenv
uv pip install --upgrade ipython
uv pip install --upgrade ipykernel
ipython kernel install --user --name=nomad-tutorial-workflows
```

Now you should be able to simply launch a Jupyter notebook browser with `jupyter notebook` in the terminal.
Open a (new) `.ipynb` file, and then select `nomad-tutorial-workflows` from the kernel list.

## **Resources**

### 1. Explore the [NOMAD documentation](https://nomad-lab.eu/prod/v1/docs/){:target="\_blank"}.

### 2. Join our vibrant Discord community! [Invitation to Discord :fontawesome-brands-discord:](https://discord.gg/Gyzx3ukUw8){:target="\_blank"}
