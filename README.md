# GearGuide

**GearGuide** is a Flask-based web app for organizing and planning outdoor trips.  
Users can create trips, view trip details, manage packing lists, and keep track of friends who join their adventures.

Users should register an account to utilize GearGuide's features.

---

## How to Run Locally

### 1. Clone the repository
git clone https://github.com/tabbott207/GearGuide.git

cd GearGuide

### 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate  on Mac

OR

.venv\Scripts\activate   on Windows

### 3. Install dependencies
pip install .

### 4. Database Setup
flask db upgrade

### 5. Run the app
OPTION A:

export FLASK_APP=GearGuide  on Mac

OR

set FLASK_APP=GearGuide    on Windows


Then:

flask run


OPTION B:

python GearGuide.py



### 6. Open the app
Open your browser to: localhost:5000
