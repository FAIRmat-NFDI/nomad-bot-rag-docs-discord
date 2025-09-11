# 🚀 XRD Auto Analyzer with NOMAD
Welcome! This tutorial will guide you through training a model using XRD-AutoAnalyzer in NOMAD. After training, you can archive the model, making it easy to find, share, and use for automatic analysis of your XRD patterns. 📊

## 📁 What's inside?
You’ll find a folder called All_CIFs. This contains structure files that can be used to train the model on a specific chemical space. The model will learn to identify if any of these structures match your XRD pattern! 🔍

> **Note:** You can easily replace these CIF files with those relevant to your chemical space of interest, so the model is trained specifically for your study. 🧪🔬

## 🛠️ How to get started
Follow the steps below to train the model using the provided CIF files, or feel free to add your own:

1. Click on the FILES tab and open `train-xrd-cnn.ipynb`.
2. Launch the notebook in Jupyter. If Jupyter is already running, stop it and start a new session.
3. Follow the instructions in the notebook to complete the tutorial. 🧑‍💻

## 📈 Run an auto XRD analysis?

Once you have trained the model, you can use it to analyze your XRD patterns automatically.
you can test this running the `auto-xrd-analysis.ipynb` notebook that will make use of a
NOMAD XRD entry. 🎉