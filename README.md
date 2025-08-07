# Extracting Course Schedules from Stony Brook SOLAR to CSV

This repository is a fork of [csv-ical](https://github.com/albertyw/csv-ical), licensed under MIT License. 
This guide explains how to extract course schedule data from Stony Brook University's SOLAR system, available in XML or HTML formats, and convert it into a CSV file for use in calendar applications or analysis. The provided Python scripts parse the data, generate recurring class sessions, and output them to a CSV file with columns for course code, start time, end time, notes, and location.

## Prerequisites

To run the scripts, ensure you have the following installed:
- **Python 3.6+**: Download from [python.org](https://www.python.org/downloads/).
- **Required Libraries**:
  ```bash
  pip install beautifulsoup4 lxml
  ```
- **Input Files**:
  - **XML File**: From SOLAR’s List View, containing `<FIELD id='win0divPAGECONTAINER'>` with HTML content in a CDATA section.
  - **HTML File**: From SOLAR’s Weekly Calendar View, saved as an HTML file (e.g., `schedule.html`).
- **Text Editor**: To verify input file contents (e.g., VS Code, Notepad++).

## Scripts Overview

Two Python scripts are provided to handle different input formats:
1. **XML to CSV (List View)**: Parses an XML file containing List View HTML, extracting course details like course code, instructor, location, dates, and schedule.
2. **HTML to CSV (Weekly Calendar View)**: Parses an HTML file from the List View, extracting course data from a table grid.

Both scripts output a CSV file with the following columns:
- **Course Code**: E.g., `AMS301`.
- **Start Time**: Session start in `YYYY-MM-DD HH:MM:SS` format.
- **End Time**: Session end in `YYYY-MM-DD HH:MM:SS` format.
- **Notes**: Course title and instructor (if available).
- **Location**: Classroom or `ONLINE`.

## XML to CSV Script

### Purpose
This script processes an XML file from SOLAR’s List View, which contains course details in a structured table with `<td class="PAGROUPDIVIDER PSLEFTCORNER">` for course titles and specific IDs for details (e.g., `DERIVED_CLS_DTL_SSR_INSTR_LONG$0`).

### Usage
1. Save the XML file as `example.xml` in the script’s directory (e.g., `c:\Users\YourName\Desktop\PyCode\iCal_from_solar\`).
2. Run the script:
   ```bash
   python xml_to_csv.py
   ```
3. The script generates `example.csv` with all class sessions.

### Example Input
The XML contains a `<FIELD id='win0divPAGECONTAINER'>` with HTML content, such as:
```xml
<FIELD id='win0divPAGECONTAINER'><![CDATA[
  <table class='PSPAGECONTAINER'>
    <td class='PAGROUPDIVIDER PSLEFTCORNER'>AMS 301 - Finite Mathematical Structures</td>
    <span id='DERIVED_CLS_DTL_SSR_INSTR_LONG$0'>Evangelos Coutsias</span>
    <span id='MTG_LOC$0'>JAVITS LECTR 102 WESTCAMPUS</span>
    <span id='MTG_DATES$0'>2025/08/25 - 2025/12/18</span>
    <span id='MTG_SCHED$0'>TuTh 12:30 - 13:50</span>
    <!-- More courses -->
  </table>
]]></FIELD>
```

### Example Output
For a term from August 25, 2025, to December 18, 2025, with four courses (AMS 301, AMS 341, ISE 337, ISE 391), the script generates 136 sessions (34 per course, 2 days/week × 17 weeks):
```csv
Course Code,Start Time,End Time,Notes,Location
AMS301,2025-08-26 12:30:00,2025-08-26 13:50:00,AMS 301 - Finite Mathematical Structures - Evangelos Coutsias,JAVITS LECTR 102 WESTCAMPUS
AMS341,2025-08-25 08:00:00,2025-08-25 09:20:00,AMS 341 - Op Rsrch I: Determinist Models - Esther Arkin,ONLINE ONLINE ONLINE
ISE337,2025-08-25 09:30:00,2025-08-25 10:50:00,ISE 337 - Scripting Languages - Ritwik Banerjee,HUMANITIES 1006 WESTCAMPUS
ISE391,2025-08-25 20:00:00,2025-08-25 21:20:00,ISE 391 - Topics in Information Systems - Ali Raza,COMPUTER SCI 2120 WESTCAMPUS
...
```

### Troubleshooting
- **Error: "No PAGECONTAINER found in XML"**:
  - **Cause**: The script couldn’t find `<FIELD id='win0divPAGECONTAINER'>`.
  - **Fix**: Verify `example.xml` contains the correct `<FIELD>` element. Run this debug code:
    ```python
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse("example.xml")
        root = tree.getroot()
        page_container = None
        for field in root.findall(".//FIELD"):
            if field.get("id") == "win0divPAGECONTAINER":
                page_container = field
                break
        print(f"PAGECONTAINER found: {page_container is not None}")
    except ET.ParseError as e:
        print(f"XML parsing failed: {e}")
    ```
    Ensure the file is saved as UTF-8 without BOM.
- **DeprecationWarning**: If you see a warning about testing an element’s truth value, the script has been updated to use `page_container is None` for compatibility.

## HTML to CSV Script

### Purpose
This script processes an HTML file from SOLAR’s Weekly Calendar View, which displays courses in a table grid (`<table id="WEEKLY_SCHED_HTMLAREA">`). It extracts course data from cells with a specific background color.

### Usage
1. Log into SOLAR, select "My Class Schedule," choose **Weekly Calendar View**, and save the page as `schedule.html`.
2. Run the script:
   ```bash
   python html_to_csv.py
   ```
3. The script generates `course_schedule.csv`.

### Example Input
The HTML contains a table like:
```html
<table id="WEEKLY_SCHED_HTMLAREA">
  <tr>
    <th>Monday</th>
    <th>Tuesday</th>
    <!-- Other days -->
  </tr>
  <tr>
    <td>13:30</td>
    <td style="background-color:rgb(182,209,146)">WRT  102 - 05<br>LEC<br>13:30 - 16:55<br>Humanities 2046</td>
    <td style="background-color:rgb(182,209,146)">IAP  390 - 01<br>LEC<br>13:30 - 16:55<br>Social and Behavioral Scien N117</td>
  </tr>
</table>
```

### Example Output
For a term from July 7, 2025, to August 16, 2025, with two courses (WRT 102, IAP 390), the script generates 24 sessions (12 per course, 2 days/week × 6 weeks):
```csv
Course Code,Start Time,End Time,Notes,Location
WRT102,2025-07-07 13:30:00,2025-07-07 16:55:00,WRT  102 - 05,Humanities 2046
IAP390,2025-07-08 13:30:00,2025-07-08 16:55:00,IAP  390 - 01,Social and Behavioral Scien N117
...
```

### Troubleshooting
- **Error: "No PAGECONTAINER found in HTML"**:
  - **Cause**: The HTML lacks `<DIV id='win0divPAGECONTAINER'>`.
  - **Fix**: Ensure the saved HTML is from SOLAR’s Weekly Calendar View and contains the `PAGECONTAINER` div. Run:
    ```python
    from bs4 import BeautifulSoup
    with open("schedule.html", 'r', encoding='utf-8-sig') as f:
        soup = BeautifulSoup(f, 'html.parser')
        page_container = soup.find("div", id="win0divPAGECONTAINER")
        print(f"PAGECONTAINER found: {page_container is not None}")
    ```
- **Missing Instructor Data**: Weekly Calendar View may not include instructors unless "Show Instructors" is checked in SOLAR. Use List View for instructor details.

## Common Issues and Fixes
- **File Encoding**: Save XML/HTML files as UTF-8 without BOM to avoid parsing errors.
- **Incorrect View**: Ensure the input matches the script (XML for List View, HTML for Weekly Calendar View).
- **Term Dates**: The HTML script hardcodes term dates (e.g., 2025/07/07–2025/08/16). Update them based on SOLAR’s "Term Information" page.
- **Library Versions**: Use `pip show beautifulsoup4 lxml` to confirm you have the latest versions.

## Next Steps
- **Calendar Import**: Import the CSV to **CSV/iCal Converter**.

# CSV/iCal Converter

[![PyPI](https://img.shields.io/pypi/v/csv-ical)](https://pypi.org/project/csv-ical/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/csv-ical)
![PyPI - License](https://img.shields.io/pypi/l/csv-ical)

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/csv-ical/status.svg)](https://drone.albertyw.com/albertyw/csv-ical)
[![Code Climate](https://codeclimate.com/github/albertyw/csv-ical/badges/gpa.svg)](https://codeclimate.com/github/albertyw/csv-ical)
[![Test Coverage](https://codeclimate.com/github/albertyw/csv-ical/badges/coverage.svg)](https://codeclimate.com/github/albertyw/csv-ical/coverage)

A simple script to convert data in CSV format to iCal format and vice
versa.

## Installation

```bash
pip install csv-ical
```

## Usage

See the example folder.

## Development

```bash
pip install -e .[test]
ruff check .
mypy . --strict --ignore-missing-imports
coverage run -m unittest
coverage report -m
```

# Final Steps
- Get the [ICS To Calendar](https://www.icloud.com/shortcuts/76e984f27b194fbf9c81044bf8bd0109) shortcut.
- Send the ICS file to your iPhone.
- Open it and click on the share icon and select **ICS To Calendar**.
