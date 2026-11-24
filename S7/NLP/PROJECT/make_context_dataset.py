import csv, json, re, zipfile, xml.etree.ElementTree as ET

def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text = ''.join(t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text)
                shared_strings.append(text)
        sheet_tree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for row in sheet_tree.findall('.//s:row', ns):
            row_dict = {}
            for c in row.findall('s:c', ns):
                ref = c.get('r')
                col = ''.join(filter(str.isalpha, ref))
                t = c.get('t')
                val = ''
                if t == 's':
                    v = c.find('s:v', ns)
                    if v is not None and v.text and v.text.isdigit():
                        val = shared_strings[int(v.text)]
                elif t == 'inlineStr':
                    is_t = c.find('.//s:t', ns)
                    if is_t is not None and is_t.text:
                        val = is_t.text
                else:
                    v = c.find('s:v', ns)
                    if v is not None and v.text:
                        val = v.text
                row_dict[col] = val
            rows.append(row_dict)
        return rows

real_s = [r for r in read_xlsx('NLP-Project16/03-dialogues/messages_real_souha.xlsx')[1:] if r.get('A')]
real_m = [r for r in read_xlsx('NLP-Project16/03-dialogues/messages_real_malak.xlsx')[1:] if r.get('A')]
real_map = {r['A']: r for r in real_s + real_m}

def clean_txt(t):
    # take first sentence or clean whitespace
    t = ' '.join(t.split())
    # truncate if excessively long paragraph to keep it a concise sentence
    if len(t) > 220:
        parts = re.split(r'[\.\n!؟\?]', t)
        for p in parts:
            if len(p.strip()) > 20:
                return p.strip()
    return t

print("Cleaner ready.")
