# Air Pollution & Health Impact Dashboard

**5DATA004C Data Science Project Lifecycle — Individual Coursework**
University of Westminster · 2025/26

---

## Files in this repository

```
repository/
├── app.py              ← Main Streamlit dashboard (the only file you run)
├── data_prep.py        ← Optional: explore/verify your data
├── requirements.txt    ← Python packages to install
└── README.md           ← This file
```

> **Important:** Place `DataExtract.csv` in the same folder as these files before running locally.
> On Streamlit Cloud the data file is loaded from the repository automatically.

---

## Live App

The dashboard is published on Streamlit Community Cloud:
👉 **[Insert your Streamlit app link here]**

---

## Step-by-step local setup

### Step 1 — Install Python
Make sure Python 3.9 or newer is installed.
Check by opening a terminal and typing:
```
python --version
```
If not installed: https://www.python.org/downloads/

---

### Step 2 — Open a terminal in your project folder

**Windows:** Open File Explorer → navigate to your folder → click the address bar → type `cmd` → press Enter

**Mac:** Open Terminal → type `cd ` (with a space) → drag the folder into Terminal → press Enter

---

### Step 3 — Install the required packages

```
pip install -r requirements.txt
```

This installs Streamlit, Plotly, and Pandas. It takes about 1–2 minutes.

---

### Step 4 — (Optional) Explore your data

```
python data_prep.py
```

Prints a summary of the dataset columns and row counts. Run this once to verify the data loaded correctly.

---

### Step 5 — Run the dashboard locally

```
streamlit run app.py
```

You will see output like:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

---

### Step 6 — Open the dashboard in your browser

Open any browser (Chrome, Firefox, Edge) and go to:
```
http://localhost:8501
```

To stop the app, press `Ctrl + C` in the terminal.

---

## Folder structure (where to put DataExtract.csv)

```
my_project/               ← your project folder
├── DataExtract.csv       ← WHO dataset (put it HERE for local use)
├── app.py
├── data_prep.py
├── requirements.txt
└── README.md
```

---

## Deploying to Streamlit Community Cloud

1. Push all files (including `DataExtract.csv`) to your **public** GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repository → set the main file to `app.py`
4. Click **Deploy** — the app will be live in ~2 minutes

---

## Dataset

- **Source:** WHO/EEA Urban Air Quality Dataset 2022
- **Coverage:** 37 European countries · 973 cities · 3 pollutants (PM2.5, NO2, O3)
- **Baseline:** WHO 2021 Air Quality Guidelines (AQG)
- **Health indicators:** Attributable Deaths, YLL, DALY, YLD

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'streamlit'` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: DataExtract.csv` | Move the CSV file to the same folder as `app.py` |
| Map shows no data | Filters are too restrictive — clear all filters and try again |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
