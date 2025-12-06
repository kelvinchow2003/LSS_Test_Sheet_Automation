import pandas as pd
from pypdf import PdfReader, PdfWriter
import os
import math

# --- CONFIGURATION ---
INPUT_PDF = "95efa_on2014.pdf"
INPUT_CSV = "roster.csv"
OUTPUT_FOLDER = "filled_forms/"

# --- THE MAPPING ---
# Based on the field dump: "Name 1", "Name 2"...
# except for Candidate 10, whose name field is just "10".
candidate_map = []

# Generate the map for candidates 1 to 10
for i in range(1, 11):
    suffix = str(i)
    
    entry = {
        "name": f"Name {suffix}",
        "addr": f"Address {suffix}",
        "city": f"City {suffix}",
        "zip": f"Postal {suffix}",
        "email": f"Email {suffix}",
        "phone": f"Phone {suffix}",
        "dd": f"Day {suffix}",
        "mm": f"Month {suffix}",
        "yy": f"Year {suffix}"
    }
    
    # SPECIAL CASE: Candidate 10's Name field is just "10"
    if i == 10:
        entry["name"] = "10"
        
    candidate_map.append(entry)

def clean_name(raw_name):
    """Converts 'Ausar , Lautaro' to 'Lautaro Ausar'."""
    if pd.isna(raw_name): return ""
    raw_name = str(raw_name)
    if "," in raw_name:
        parts = raw_name.split(",")
        if len(parts) >= 2:
            return f"{parts[1].strip()} {parts[0].strip()}"
    return raw_name

def fill_pdf(batch_df, batch_num):
    reader = PdfReader(INPUT_PDF)
    writer = PdfWriter()
    writer.append(reader)
    
    data_map = {}
    
    for i, (idx, row) in enumerate(batch_df.iterrows()):
        if i >= len(candidate_map): break
        
        # Get the field names for this slot
        fields = candidate_map[i]
        
        # 1. Clean Name
        full_name = clean_name(row.get("AttendeeName", ""))
        
        # 2. Parse Date
        raw_dob = row.get("DateOfBirth", "")
        dd, mm, yy = "", "", ""
        if pd.notna(raw_dob):
            try:
                dt = pd.to_datetime(raw_dob, dayfirst=True)
                dd = str(dt.day).zfill(2)
                mm = str(dt.month).zfill(2)
                # CHANGED: Now using the full 4-digit year
                yy = str(dt.year)
            except: pass

        # 3. Map Data
        data_map[fields["name"]] = full_name
        data_map[fields["addr"]] = str(row.get("Street", ""))
        data_map[fields["city"]] = str(row.get("City", ""))
        data_map[fields["zip"]] = str(row.get("PostalCode", ""))
        data_map[fields["email"]] = str(row.get("E-mail", ""))
        data_map[fields["phone"]] = str(row.get("AttendeePhone", ""))
        data_map[fields["dd"]] = dd
        data_map[fields["mm"]] = mm
        data_map[fields["yy"]] = yy

    # Apply to all pages
    for page in writer.pages:
        writer.update_page_form_field_values(page, data_map)

    output_filename = f"{OUTPUT_FOLDER}EFA_Test_Sheet_{batch_num}.pdf"
    with open(output_filename, "wb") as f:
        writer.write(f)
    print(f"Generated: {output_filename}")

# --- MAIN EXECUTION ---
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

print("Reading roster.csv...")
df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

# This form fits 10 candidates per file
BATCH_SIZE = 10
total_batches = math.ceil(len(df) / BATCH_SIZE)

print(f"Processing {len(df)} candidates into {total_batches} batch(es)...")

for i in range(total_batches):
    batch = df.iloc[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
    fill_pdf(batch, i + 1)

print("Done.")