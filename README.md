# Automated Nanoindentation Workflow

This repository contains code for automating nanoindentation workflows on **iMicro (KLA)** nanoindenters. It integrates:
- Real-time image-based feature detection
- Crosshair alignment
- Automated stage movement
- Execution of indentation sequences

### ⚙️ System Requirements
- This code is designed for setups where the **iMicro UI is on Monitor 2** with **1920x1080 resolution**.
- If your screen layout and UI appearance are similar to the original, the automation will work with minimal changes.

### 📁 Repository Structure
- `automation/`: Core modules for alignment, detection, and automation logic.
- `assets/`: Image templates and sample UI screenshots.
- `examples/`: Sample notebooks to demonstrate workflow.
- `requirements.txt`: List of dependencies.

### 🚀 Quick Start (Colab)
You can run the example notebook directly in Google Colab. This version skips live screen capture and instead simulates the workflow using sample images.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](./examples/demo_notebook.ipynb)

---


### 🔧 Notes
- The full automation (with screen reading and mouse control) only works on local machines.
- For safety, always verify coordinate commands before enabling hardware movement.

---

### 📃 License
MIT License
