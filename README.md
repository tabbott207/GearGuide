# GearGuide

**GearGuide** is a Flask-based web app for organizing and planning outdoor trips.  
Users can create trips, view trip details, manage packing lists, and keep track of friends who join their adventures.

Users muat register an account to utilize GearGuide's features.

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/tabbott207/GearGuide.git

cd GearGuide
```
### 2. Set up virtual environment

Mac/Linux
```bash
python -m venv .venv

source .venv/bin/activate
```
OR

Windows
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install .
```

### 4. Database Setup

Mac/Linux
```bash
export FLASK_APP=GearGuide
flask db upgrade
```

OR

Windows
```powershell
$env:FLASK_APP="GearGuide"
flask db upgrade
```
### 5. Run the app
```bash
python gearguide.py
```

### 6. Open the app
Open your browser to: http://127.0.0.1:5000
