import pandas as pd

from pypdf import PdfReader, PdfWriter

import os

import math

# --- CONFIGURATION ---

INPUT_PDF = "95tsbronzestar2020_fillable.pdf"

INPUT_CSV = "roster.csv"

OUTPUT_FOLDER = "filled_forms/"

# --- THE MAPPING ---

candidate_map = [

    # === PAGE 1 (Candidates 1-6) ===

    # WORKING: Explicit names

    {"type": "explicit", "s": "1"}, # 1

    {"type": "explicit", "s": "2"}, # 2

    {"type": "explicit", "s": "3"}, # 3

    {"type": "explicit", "s": "4"}, # 4

    {"type": "explicit", "s": "5"}, # 5

    {"type": "explicit", "s": "6"}, # 6

    # === PAGE 2 (Candidates 7-13) ===

    # WORKING: 7-13

    {"type": "dot", "s": ".0"},           # 7

    {"type": "dot", "s": ".1.0"},         # 8

    {"type": "dot", "s": ".1.1.0"},       # 9

    {"type": "dot", "s": ".1.1.1.0"},     # 10

    {"type": "dot", "s": ".1.1.1.1.0"},   # 11

    {"type": "dot", "s": ".1.1.1.1.1.0"}, # 12

    {"type": "dot", "s": ".1.1.1.1.1.1"}, 

]

def clean_name(raw_name):

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

        slot = candidate_map[i]

        # --- BUILD FIELD NAMES ---

        target_suffixes = []

        is_explicit = False

        if slot["type"] == "explicit":

            target_suffixes = [slot["s"]]

            is_explicit = True

        elif slot["type"] == "dot":

            target_suffixes = [slot["s"]]

        elif slot["type"] == "shotgun":

            target_suffixes = slot["s_list"]

        # --- PREPARE DATA ---

        full_name = clean_name(row.get("AttendeeName", ""))

        address_val = str(row.get("Street", ""))

        city_val = str(row.get("City", ""))

        postal_val = str(row.get("PostalCode", ""))

        email_val = str(row.get("E-mail", ""))

        phone_val = str(row.get("AttendeePhone", ""))

        raw_dob = row.get("DateOfBirth", "")

        dd, mm, yy = "", "", ""

        if pd.notna(raw_dob):

            try:

                dt = pd.to_datetime(raw_dob, dayfirst=True)

                dd = str(dt.day).zfill(2)

                mm = str(dt.month).zfill(2)

                yy = str(dt.year)[-2:] 

            except: pass

        # --- LOOP THROUGH TARGETS ---

        for s in target_suffixes:

            if is_explicit:

                # Page 1 Format

                f_name = f"Name{s}"

                f_addr = f"Address{s}"

                f_city = f"City{s}"

                f_zip  = f"Postal{s}"

                f_email = f"Email{s}"

                f_phone = f"Phone{s}"

                f_dd = f"DOBD{s}"

                f_mm = f"DOBM{s}"

                f_yy = f"DOBY{s}"

            else:

                # Page 2 Format (Dot)

                f_name = f"Name{s}"

                f_addr = f"Address{s}"

                f_city = f"City{s}"

                f_zip  = f"Postal{s}"

                f_email = f"Email{s}"

                f_phone = f"Phone{s}"

                f_dd = f"DOBD{s}"

                f_mm = f"DOBM{s}"

                f_yy = f"DOBY{s}"

            data_map[f_name] = full_name

            data_map[f_addr] = address_val

            data_map[f_city] = city_val

            data_map[f_zip] = postal_val

            data_map[f_email] = email_val

            data_map[f_phone] = phone_val

            data_map[f_dd] = dd

            data_map[f_mm] = mm

            data_map[f_yy] = yy

    for page in writer.pages:

        writer.update_page_form_field_values(page, data_map)

    output_filename = f"{OUTPUT_FOLDER}Bronze_Star_Filled_{batch_num}.pdf"

    with open(output_filename, "wb") as f:

        writer.write(f)

    print(f"Generated: {output_filename}")

# --- MAIN EXECUTION ---

if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

BATCH_SIZE = 13

total_batches = math.ceil(len(df) / BATCH_SIZE)

for i in range(total_batches):

    batch = df.iloc[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]

    fill_pdf(batch, i + 1)

print("Bronze Star Done.")
 