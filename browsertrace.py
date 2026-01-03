import os
import sqlite3
import shutil
from datetime import datetime


def chrome_time(chrome_timestamp):
    if chrome_timestamp == 0:
        return "N/A"
    return datetime.fromtimestamp(
        chrome_timestamp / 1000000 - 11644473600
    )


def copy_history_db():
    user = os.getlogin()
    chrome_path = f"C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"

    if not os.path.exists(chrome_path):
        print("Chrome history database not found.")
        return None

    temp_path = "History_copy"
    shutil.copy2(chrome_path, temp_path)
    return temp_path


def extract_history(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT url, title, last_visit_time
        FROM urls
        ORDER BY last_visit_time DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def detect_suspicious_entries(history_rows):
    suspicious = []
    for url, title, time in history_rows:
        if not title or title.strip() == "":
            suspicious.append((url, title, time))
    return suspicious

def build_timeline(history_rows):
    timeline = {}
    for url, title, time in history_rows:
        visit_time = chrome_time(time)
        if visit_time == "N/A":
            continue
        date = visit_time.date()
        timeline.setdefault(date, []).append(visit_time)
    return timeline

def generate_report(history, suspicious, timeline):
    with open("BrowserTrace_Report.txt", "w") as report:
        report.write("BROWSERTRACE – FORENSIC REPORT\n")
        report.write("="*40 + "\n\n")

        report.write("Recent Browser History:\n")
        for url, title, time in history:
            report.write(f"{chrome_time(time)} | {url} | {title}\n")

        report.write("\nSuspicious / Possibly Deleted Entries:\n")
        for url, title, time in suspicious:
            report.write(f"{chrome_time(time)} | {url}\n")

        report.write("\nTimeline Summary:\n")
        for date, times in timeline.items():
            report.write(f"{date} -> Visits: {len(times)}\n")


def main():
    print("BrowserTrace - Chrome Forensic Tool\n")

    db_copy = copy_history_db()
    if not db_copy:
        return

    history = extract_history(db_copy)

    print("Recent Browser History:\n")
    for url, title, time in history:
        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Visit Time: {chrome_time(time)}")
        print("-" * 50)

    print("\nForensic Browser Analysis Completed.")

if __name__ == "__main__":
    main()
