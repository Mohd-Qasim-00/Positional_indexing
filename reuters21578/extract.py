from bs4 import BeautifulSoup
import os

input_file = "reut2-000.sgm"
output_folder = "corpus"

os.makedirs(output_folder, exist_ok=True)

# Read SGML file
with open(input_file, "r", encoding="latin-1") as file:
    content = file.read()

# Parse SGML
soup = BeautifulSoup(content, "html.parser")

# Find all Reuters documents
documents = soup.find_all("reuters")

print("Total documents found:", len(documents))

# Extract first 100 documents
for i, document in enumerate(documents[:100], start=1):

    title_tag = document.find("title")
    body_tag = document.find("body")

    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    body = body_tag.get_text(" ", strip=True) if body_tag else ""

    text = title + " " + body

    output_file = os.path.join(
        output_folder,
        f"doc{i}.txt"
    )

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)

print("100 documents extracted successfully!")