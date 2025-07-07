from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import re

WEEKDAY_MAP = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}

def extract_schedule(html_path, output_csv):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    courses = []
    course_titles = soup.find_all("td", class_="PAGROUPDIVIDER PSLEFTCORNER")

    for i, title_tag in enumerate(course_titles, start=0):
        def make_id(name): return f"{name}${i}"
        def safe_text(id_):
            tag = soup.find(id=id_)
            return tag.get_text(strip=True) if tag else ""

        full_title = title_tag.get_text(strip=True)
        code_match = re.search(r"[A-Z]{2,4}\s*\d{3}", full_title)
        course_code = code_match.group(0).replace(" ", "") if code_match else "UNKNOWN"
        instructor = safe_text(make_id("DERIVED_CLS_DTL_SSR_INSTR_LONG"))
        location = safe_text(make_id("MTG_LOC"))
        dates_text = safe_text(make_id("MTG_DATES"))
        schedule_text = safe_text(make_id("MTG_SCHED"))

        # Analysis of course time
        try:
            days_raw, time_range = schedule_text.split(" ", 1)
            days = re.findall(r"(Mo|Tu|We|Th|Fr|Sa|Su)", days_raw)
            start_time_str, end_time_str = time_range.split(" - ")
        except:
            continue  # Skip the abnormal format course

        # Analyze the range of course dates
        try:
            start_date, end_date = [datetime.strptime(d.strip(), "%Y/%m/%d") for d in dates_text.split(" - ")]
        except:
            continue

        # Notes: Full name of the course + name of the instructor
        notes = f"{full_title} - {instructor}"

        # Calculate all the classes by the day of the week
        current = start_date
        while current <= end_date:
            if current.weekday() in [WEEKDAY_MAP[d] for d in days]:
                start_dt = datetime.combine(current.date(), datetime.strptime(start_time_str, "%H:%M").time())
                end_dt = datetime.combine(current.date(), datetime.strptime(end_time_str, "%H:%M").time())
                courses.append({
                    "Course Code": course_code,
                    "Start Time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "End Time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": notes,
                    "Location": location
                })
            current += timedelta(days=1)

    # exaport CSV
    fieldnames = ["Course Code", "Start Time", "End Time", "Notes", "Location"]
    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(courses)

    print(f"✅{len(courses)} Course timings in total, saved as {output_csv}")

extract_schedule("schedule.html", "course_schedule.csv")
