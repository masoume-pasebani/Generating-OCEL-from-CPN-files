# Generating OCEL from CPN Files

This project aims to generate **Object-Centric Event Logs (OCEL)** from **CPN** (Colored Petri Nets) files. The tool extracts event data from CPN models, processes it, and outputs it as an **OCEL**, which can be used for event-based process analysis, such as process mining.

The project is built using **Django** for the backend and provides a user-friendly interface for uploading and processing CPN files.

## Features

* **CPN File Upload**: Allows users to upload CPN files (XML format) for processing.
* **Generate OCEL**: Converts CPN files into **Object-Centric Event Logs (OCEL)** format.
* **Event Log Visualization**: Provides visual representation of the generated OCELs.
* **Django Backend**: Handles file processing and event log generation.
* **Bootstrap Frontend**: Interactive user interface for file upload and OCEL visualization.

## Technologies Used

* **Backend**: Django (Python)
* **Frontend**: Bootstrap, HTML, CSS
* **CPN Parsing**: Custom parsing logic to process CPN XML files.
* **Event Log Generation**: Generates OCELs based on CPN model data.
* **Database**: SQLite3 (or any other preferred database)
* **Visualization**: Interactive views to display event logs in the frontend.

## Setup Instructions

### 1. Clone the Repository

git clone https://github.com/masoume-pasebani/Generating-OCEL-from-CPN-files.git
cd Generating-OCEL-from-CPN-files

2. Create and Activate Virtual Environment
bash
Copy code
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
3. Install Requirements
bash
Copy code
pip install -r requirements.txt
4. Run Django Migrations
bash
Copy code
python manage.py migrate
5. Start the Development Server
bash
Copy code
python manage.py runserver
Usage
Open your browser and navigate to: http://127.0.0.1:8000/

Upload a CPN XML file: Choose a file and click the "Upload" button.

The system will process the uploaded CPN file, generate an Object-Centric Event Log (OCEL), and display the resulting log in the web interface.

You can visualize the OCEL and inspect the events.

File Format
The project expects the CPN files to be in XML format. Ensure that the CPN models are well-structured and follow the standard CPN XML format for successful parsing and event log generation.

