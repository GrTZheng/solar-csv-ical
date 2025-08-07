from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import re
import xml.etree.ElementTree as ET

# Map day abbreviations to weekday numbers (0=Monday, 6=Sunday)
WEEKDAY_MAP = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}

def safe_text(element, default=""):
    """Safely extract text from an element, returning default if None."""
    return element.get_text(strip=True) if element else default

def parse_schedule(schedule_text):
    """Parse schedule text like 'MoWe 08:00 - 09:20' into days and times."""
    match = re.match(r"([A-Za-z]+)\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", schedule_text)
    if not match:
        return None, None, None
    days, start_time, end_time = match.groups()
    day_list = []
    for i in range(0, len(days), 2):
        day = days[i:i+2]
        if day in WEEKDAY_MAP:
            day_list.append(day)
    return day_list, start_time, end_time

def extract_schedule(xml_path, output_csv):
    try:
        # Parse XML file
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"XML parsing failed: {e}")
        return
    
    # Find the PAGECONTAINER field (handle potential namespaces)
    page_container = None
    for field in root.findall(".//FIELD"):
        if field.get("id") == "win0divPAGECONTAINER":
            page_container = field
            break
    
    if page_container is None:
        print("No PAGECONTAINER found in XML")
        return
    
    # Extract HTML content from CDATA
    html_content = page_container.text
    if not html_content:
        print("No HTML content found in PAGECONTAINER")
        return
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    courses = []
    # Find all course titles
    course_titles = soup.find_all("td", class_="PAGROUPDIVIDER PSLEFTCORNER")
    print(f"Found {len(course_titles)} courses")
    
    for idx, title_elem in enumerate(course_titles):
        course_title = safe_text(title_elem)
        course_code = re.search(r"[A-Z]{2,4}\s*\d{3}", course_title)
        course_code = course_code.group(0).replace(" ", "") if course_code else "UNKNOWN"
        print(f"Processing course: {course_title} ({course_code})")
        
        # Define IDs for course details
        base_id = f"win0divDERIVED_REGFRM1_DESCR20${idx}"
        instructor_id = f"DERIVED_CLS_DTL_SSR_INSTR_LONG${idx}"
        location_id = f"MTG_LOC${idx}"
        dates_id = f"MTG_DATES${idx}"
        schedule_id = f"MTG_SCHED${idx}"
        
        # Extract course details
        instructor = safe_text(soup.find(id=instructor_id))
        location = safe_text(soup.find(id=location_id))
        dates = safe_text(soup.find(id=dates_id))
        schedule_text = safe_text(soup.find(id=schedule_id))
        
        print(f"Instructor: {instructor}, Location: {location}, Dates: {dates}, Schedule: {schedule_text}")
        
        # Parse dates
        try:
            start_date_str, end_date_str = dates.split(" - ")
            start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
            end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
        except Exception as e:
            print(f"Date parsing failed for {course_title}: {e}")
            continue
        
        # Parse schedule
        days, start_time_str, end_time_str = parse_schedule(schedule_text)
        if not days:
            print(f"Schedule parsing failed for {course_title}")
            continue
        
        # Generate sessions for each day in the term
        current = start_date
        while current <= end_date:
            for day in days:
                if current.weekday() == WEEKDAY_MAP[day]:
                    try:
                        start_dt = datetime.combine(current.date(), datetime.strptime(start_time_str, "%H:%M").time())
                        end_dt = datetime.combine(current.date(), datetime.strptime(end_time_str, "%H:%M").time())
                        courses.append({
                            "Course Code": course_code,
                            "Start Time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "End Time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                            "Notes": f"{course_title} - {instructor}",
                            "Location": location
                        })
                        print(f"Added session for {course_code} on {current.date()} from {start_time_str} to {end_time_str}")
                    except Exception as e:
                        print(f"Session creation failed for {course_title} on {current.date()}: {e}")
            current += timedelta(days=1)
    
    # Write to CSV
    fieldnames = ["Course Code", "Start Time", "End Time", "Notes", "Location"]
    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(courses)
    
    print(f"✅ 共导出 {len(courses)} 个课程时间点，文件已保存为 {output_csv}")

# Example usage
extract_schedule("example.xml", "example.csv")