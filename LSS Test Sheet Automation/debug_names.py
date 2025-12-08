from pypdf import PdfReader, PdfWriter

INPUT_PDF = "95tsbronzestar2020_fillable.pdf"

OUTPUT_PDF = "debug_names.pdf"

reader = PdfReader(INPUT_PDF)

writer = PdfWriter()

writer.append(reader)

data_map = {}

fields = reader.get_fields()

print("Mapping all fields...")

for field_name in fields:

    # We only care about Name fields to identify the slots

    if "Name" in field_name:

        # Write the field's OWN NAME into the box

        data_map[field_name] = field_name

# Write to PDF

for page in writer.pages:

    writer.update_page_form_field_values(page, data_map)

with open(OUTPUT_PDF, "wb") as f:

    writer.write(f)

print(f"Done! Open '{OUTPUT_PDF}' and look at the Candidate 13 box.")

print("Tell me EXACTLY what text is written inside the Candidate 13 Name box.")
 