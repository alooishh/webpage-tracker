# webpage_tracker.py
import os
import time
import difflib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from openpyxl import Workbook

# 📥 Step 1: Capture HTML Snapshot
def capture_html_snapshot(url: str, tag: str):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    os.makedirs("html_snapshots", exist_ok=True)
    with open(f"html_snapshots/{tag}.html", "w", encoding="utf-8") as f:
        f.write(html)

    driver.quit()

# 🔍 Step 2: Compare HTML Files
def load_html(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def compare_html_and_save_to_excel(old_path, new_path, output_path="/Users/anuraj/Desktop/html_changes.xlsx", url_tag=""):
    old_html = load_html(old_path)
    new_html = load_html(new_path)

    diff = difflib.unified_diff(old_html, new_html, lineterm="")

    wb = Workbook()
    ws = wb.active
    ws.title = "HTML Changes"
    ws.append(["Timestamp", "Change Type", "Content", "Tag/URL"])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for line in diff:
        if line.startswith("+ ") and not line.startswith("+++"):
            ws.append([timestamp, "Added", line[2:].strip(), url_tag])
        elif line.startswith("- ") and not line.startswith("---"):
            ws.append([timestamp, "Removed", line[2:].strip(), url_tag])
        elif line.startswith("@@"):
            ws.append([timestamp, "Context", line.strip(), url_tag])

    wb.save(output_path)
    print(f"✅ HTML changes saved to {output_path}")

# 🔁 Step 3: Automation Wrapper
def run_tracker(url: str, tag_prefix: str = "people"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_tag = f"{tag_prefix}_{timestamp}"
    new_path = f"html_snapshots/{new_tag}.html"

    # Capture new snapshot
    capture_html_snapshot(url, new_tag)

    # Find previous snapshot
    files = sorted([f for f in os.listdir("html_snapshots") if f.startswith(tag_prefix) and f.endswith(".html")])
    if len(files) < 2:
        print("🕒 Not enough snapshots to compare yet.")
        return

    old_path = f"html_snapshots/{files[-2]}"
    print(f"🔍 Comparing {files[-2]} → {new_tag}.html")

    # Compare and export
    compare_html_and_save_to_excel(
        old_path=old_path,
        new_path=new_path,
        output_path="/Users/anuraj/Desktop/html_changes.xlsx",
        url_tag=url
    )

# 🚀 Run the tracker
if __name__ == "__main__":
    run_tracker("https://www.brownadvisory.com/us/people")# webpage_tracker.py
import os
import time
import difflib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from openpyxl import Workbook

# 📥 Step 1: Capture HTML Snapshot
def capture_html_snapshot(url: str, tag: str):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)

    html = driver.page_source
    os.makedirs("html_snapshots", exist_ok=True)
    with open(f"html_snapshots/{tag}.html", "w", encoding="utf-8") as f:
        f.write(html)

    driver.quit()

# 🔍 Step 2: Extract Name + Designation
def extract_people_info(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    people_blocks = soup.find_all("div", class_="views-row")
    extracted = []

    for block in people_blocks:
        name_tag = block.find("div", class_="field--name-title")
        role_tag = block.find("div", class_="field--name-field-person-title")
        if name_tag and role_tag:
            name = name_tag.get_text(strip=True)
            role = role_tag.get_text(strip=True)
            extracted.append((name, role))

    return extracted

# 📊 Step 3: Compare and Save to Excel
def compare_and_save_to_excel(old_data, new_data, output_path="html_changes.xlsx", url_tag=""):
    old_set = set(old_data)
    new_set = set(new_data)

    added = new_set - old_set
    removed = old_set - new_set

    wb = Workbook()
    ws = wb.active
    ws.title = "People Changes"
    ws.append(["Timestamp", "Change Type", "Name", "Designation", "Tag/URL"])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for name, role in added:
        ws.append([timestamp, "Added", name, role, url_tag])
    for name, role in removed:
        ws.append([timestamp, "Removed", name, role, url_tag])

    wb.save(output_path)
    print(f"✅ People changes saved to {output_path}")

# 🔁 Step 4: Automation Wrapper
def run_tracker(url: str, tag_prefix: str = "people"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_tag = f"{tag_prefix}_{timestamp}"
    new_path = f"html_snapshots/{new_tag}.html"

    # Capture new snapshot
    capture_html_snapshot(url, new_tag)

    # Find previous snapshot
    files = sorted([f for f in os.listdir("html_snapshots") if f.startswith(tag_prefix) and f.endswith(".html")])
    if len(files) < 2:
        print("🕒 Not enough snapshots to compare yet.")
        return

    old_path = f"html_snapshots/{files[-2]}"
    print(f"🔍 Comparing {files[-2]} → {new_tag}.html")

    # Extract info
    old_data = extract_people_info(old_path)
    new_data = extract_people_info(new_path)

    # Compare and export
    compare_and_save_to_excel(
        old_data=old_data,
        new_data=new_data,
        output_path="html_changes.xlsx",
        url_tag=url
    )

# 🚀 Run the tracker
if __name__ == "__main__":
    run_tracker("https://www.brownadvisory.com/us/people")

