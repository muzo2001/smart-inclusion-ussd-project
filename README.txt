# Smart Inclusion USSD System (Prototype)
This is a basic Flask prototype for a USSD system to assist small-scale farmers in Zambia.

## Requirements
- Python 3.9+
- Flask

## How to Run
1. Open a terminal or command prompt.
2. Navigate to the project folder.
3. Install Flask using pip:
   pip install -r requirements.txt
4. Run the app:
   python app.py
5. Visit http://127.0.0.1:5000 to test if it runs.

## Quick Start (Automated)
1. Double-click `run_ussd_app.bat` to install requirements and start the app automatically.

## USSD Simulation (Curl)
Use this command to simulate a USSD request:

    curl -X POST http://127.0.0.1:5000/ussd -d "sessionId=12345" -d "serviceCode=*123#" -d "phoneNumber=260971234567" -d "text=1"

## USSD Simulation (Postman)
1. Import `SmartInclusionUSSD.postman_collection.json` into Postman.
2. Use the "USSD Simulation" request to test the endpoint.

## New Feature: Farmer Registration
- Farmers can now register via USSD by selecting option 1 and following the prompts to enter their name, location, farm size, crops, and livestock.
- Data is stored in a local SQLite database (`farmers.db`).
