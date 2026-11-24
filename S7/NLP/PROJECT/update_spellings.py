import csv

path = "NLP-Project16/04-glossary-and-rules/context-set-v1.csv"
with open(path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Normalization map for invented sentences
replacements = [
    ("هذا ", "هادا "),
    ("هذه ", "هادي "),
    ("هذيك ", "هاديك "),
    ("هذي ", "هادي "),
    ("هذوك ", "هادوك "),
    ("مكانش", "ماكاش"),
    ("تع ", "تاع "),
    ("بش ", "باش "),
    ("كفاش", "كيفاش"),
    ("شفتو", "شفتو"),
    (" 9bal", " qbal"),
    ("9bel", "qbel"),
]

for r in rows:
    if r["origin"] == "invented":
        s = r["sentence"]
        for old, new in replacements:
            s = s.replace(old, new)
        r["sentence"] = s

with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("Updated invented spellings.")
