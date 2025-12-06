import pandas as pd
from pypdf import PdfReader, PdfWriter
import os
import math

# --- CONFIGURATION ---
INPUT_PDF = "95tsbronzemedallion2020_fillable.pdf"
INPUT_CSV = "roster.csv"
OUTPUT_FOLDER = "filled_forms/"

# --- THE MAPPING (Exact working copy from your last message) ---
candidate_map = [
    # === PAGE 1 (Candidates 1-6) ===
    # 1: WORKING
    {"base": "1", "s": ".0"},           
    
    # 2: WORKING
    {"base": "1", "s": ".1.0"},         
    
    # 3: WORKING
    {"base": "1", "s": ".1.1.0"},       
    
    # 4: WORKING
    {"base": "1", "s": ".1.1.1.0"},     
    
    # 5: WORKING
    {"base": "1", "s": ".1.1.1.1.0"},   
    
    # 6: WORKING
    {"base": "1", "s": ".1.1.1.1.1"},   

    # === PAGE 2 (Candidates 7-13) ===
    # 7: WORKING
    {"base": "", "s": ".0.0"},              
    
    # 8: WORKING
    {"base": "", "s": ".0.1.0"},        
    
    # 9: WORKING
    {"base": "", "s": ".0.1.1.0"},      
    
    # 10: WORKING
    {"base": "", "s": ".0.1.1.1.0"},    
    
    # 11: WORKING
    {"base": "", "s": ".0.1.1.1.1.0"},  
    
    # 12: WORKING
    {"base": "", "s": ".0.1.1.1.1.1.0"},
    
    # 13: WORKING
    {"base": "", "s": ".0.1.1.1.1.1.1"},
]

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
        
        # Get the suffix pattern for this candidate
        slot = candidate_map[i]
        b = slot["base"]
        s = slot["s"]
        
        # Build field names
        f_name = f"Name{b}{s}"
        f_addr = f"Address{b}{s}"
        f_city = f"City{b}{s}"
        f_zip  = f"Postal{b}{s}"
        f_email = f"Email{b}{s}"
        f_phone = f"Phone{b}{s}"
        f_dd = f"DOBD{b}{s}"
        f_mm = f"DOBM{b}{s}"
        f_yy = f"DOBY{b}{s}"

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
                # CHANGE: Only take the last 2 digits ([-2:])
                yy = str(dt.year)[-2:] 
            except: pass

        # 3. Map Data
        data_map[f_name] = full_name
        data_map[f_addr] = str(row.get("Street", ""))
        data_map[f_city] = str(row.get("City", ""))
        data_map[f_zip] = str(row.get("PostalCode", ""))
        data_map[f_email] = str(row.get("E-mail", ""))
        data_map[f_phone] = str(row.get("AttendeePhone", ""))
        data_map[f_dd] = dd
        data_map[f_mm] = mm
        data_map[f_yy] = yy

    # Apply to all pages
    for page in writer.pages:
        writer.update_page_form_field_values(page, data_map)

    output_filename = f"{OUTPUT_FOLDER}Bronze_Medallion_Test_Sheet_{batch_num}.pdf"
    with open(output_filename, "wb") as f:
        writer.write(f)
    print(f"Generated: {output_filename}")

# --- MAIN EXECUTION ---
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

print("Reading roster.csv...")
df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

BATCH_SIZE = 13
total_batches = math.ceil(len(df) / BATCH_SIZE)

print(f"Processing {len(df)} candidates into {total_batches} batch(es)...")

for i in range(total_batches):
    batch = df.iloc[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
    fill_pdf(batch, i + 1)

print("Done.")