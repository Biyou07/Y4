# -*- coding: utf-8 -*-
import csv, subprocess, os, re, zipfile, xml.etree.ElementTree as ET

# Read real messages map
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
all_real = {r['A']: r for r in real_s + real_m}

def get_real_text(mid, fallback):
    if mid in all_real:
        txt = all_real[mid].get('C', '').strip()
        txt = ' '.join(txt.split())
        # Anonymize any phone/names if needed (validator checks for numbers)
        txt = re.sub(r'\b0[567]\d{8}\b', '[هاتف]', txt)
        # Keep it single concise sentence if possible
        if len(txt) > 220:
            parts = re.split(r'[\.\n!؟\?]', txt)
            for p in parts:
                if len(p.strip()) > 20:
                    return p.strip()
        return txt
    return fallback

DATA = [
    # 1. G-002: الكيف / كيف (cannabis)
    {
        "term": "الكيف", "canon": "كيف", "drug": "cannabis",
        "rows": [
            {"term": "الكيف", "sentence": get_real_text("M-S30-0033", "راه مبلي بتدخين الكيف المعالج وما قدرش يتوقف وحدو."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0033"},
            {"term": "kif", "sentence": get_real_text("M-S36-0010", "kayen nas ybi3o l'kif f l'houma 3inani w drari tbellaw."), "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S36-0010"},
            {"term": "الكيف", "sentence": get_real_text("M-S38-0007", "12 سنة نتكيف زطله يوميا و وقفة عليها في نهار حاليا عندي فوق من عشرة سنوات باعد عليه."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S38-0007"},
            {"term": "كيف", "sentence": get_real_text("M-S38-0002", "كيفي ينصح فالناس وهو مابطلش كمبلاتمون."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S38-0002"},
            {"term": "kif", "sentence": "hada l'film dja 3la kif ta3i w 3jebni bezzaf.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 2. G-003: chira / شيرة (cannabis)
    {
        "term": "chira", "canon": "شيرة", "drug": "cannabis",
        "rows": [
            {"term": "chira", "sentence": get_real_text("M-S38-0006", "dkhalt f triq chira w drouk habelt l'walidin m3aya."), "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S38-0006"},
            {"term": "chira", "sentence": get_real_text("M-S25-0003", "sahbi bda yconsommi chira kol lila w ma bqach yrouh yakhdem."), "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S25-0003"},
            {"term": "chira", "sentence": "on a trouvé un morceau de chira dans sa poche.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "شيرة", "sentence": "هاديك الشيرة تقرا معايا في لافاك وناس ملاح بزاف.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "chira", "sentence": "chira ta3 wahren hadik jat tchouf la famille hna.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 3. G-004: garou / قارو (cannabis)
    {
        "term": "قارو", "canon": "قارو", "drug": "cannabis",
        "rows": [
            {"term": "قارو", "sentence": get_real_text("M-S30-0013", "كي لسقلك الڨارو في فمك تفكرت كي كنا نديروها بالورق نتاع الشمشة تسطر."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0013"},
            {"term": "garou", "sentence": get_real_text("M-S30-0014", "الدخل اليومي مايكفينيش فطور الصباح نتاع قارو كيف."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0014"},
            {"term": "قارو", "sentence": get_real_text("M-S31-0009", "الزوالي قارو زطلة حكمو عليه سنين هل يعقل هاذا قاع."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S31-0009"},
            {"term": "قارو", "sentence": get_real_text("M-S30-0015", "يا مستر الجائزة نتع العام هذا تروح للقارو نتع الدخان ماشي للمرسيدس."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0015"},
            {"term": "قارو", "sentence": get_real_text("M-S33-0028", "انا ڨارو هذا نشوفو غير برا مكانش كامل فلافامي يتكيفو دخان."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S33-0028"},
        ]
    },
    # 4. G-005: jwan / جوان (cannabis)
    {
        "term": "جوان", "canon": "جوان", "drug": "cannabis",
        "rows": [
            {"term": "جوان", "sentence": get_real_text("M-S38-0005", "louled 3 snin w noss ntkyef wsselt nhar b 2gram jwan w marat akther."), "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S38-0005"},
            {"term": "jwan", "sentence": "kmiyet jwan zatla w rani n7es b doukha kbira drouk.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "jwan", "sentence": "fumé un jwan de shit avec les voisins au quartier.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "جوان", "sentence": "الامتحانات تاع السداسي تبدا في شهر جوان إن شاء الله.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "jwan", "sentence": "lazem nbadlo l'jwan ta3 l'robinet راه يسيل بالما.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 5. G-006: barrette / باريطة (cannabis)
    {
        "term": "باريطة", "canon": "باريطة", "drug": "cannabis",
        "rows": [
            {"term": "باريطة", "sentence": "لقاو عندو باريطة زطلة كان حاب يبيعها قدام الباب.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "barrette", "sentence": "chra barrette ta3 1000 da w qsemha m3a sahbo.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "barrette", "sentence": "il a caché une barrette de résine sous le siège.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "باريطة", "sentence": "شريت باريطة رام جديدة باش نركبها في الميكرو تاعي.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "barrette", "sentence": "khti daret barrette chaba f ch3arha lyoum.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 6. G-007: plaquette / بلاكيطة (cannabis)
    {
        "term": "بلاكيطة", "canon": "بلاكيطة", "drug": "cannabis",
        "rows": [
            {"term": "بلاكيطة", "sentence": get_real_text("M-S30-0030", "حجز أكثر من عشرة آلاف قرص وبلاكيطة من الحبوب المهلوسة في العملية."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0030"},
            {"term": "plaquette", "sentence": "jabo plaquette ta3 zatla men l'frontière w qabdouhom.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "plaquette", "sentence": "la police a saisi une plaquette de psychotropes.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "بلاكيطة", "sentence": "شريت بلاكيطة شوكولا نوار باش ندير بيها كاطو.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "plaquette", "sentence": "lazem nbadel les plaquettes de frein ta3 l'auto 9bal ma nsafar.", "script": "mixed-fr", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 7. G-008: حشيش / حشيش (cannabis)
    {
        "term": "حشيش", "canon": "حشيش", "drug": "cannabis",
        "rows": [
            {"term": "حشيش", "sentence": get_real_text("M-S30-0036", "كان يتعاطى الحشيش بزاف حتى ولا عندو وسواس وخوف."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0036"},
            {"term": "7achich", "sentence": get_real_text("M-S30-0037", "l'7achich hada wlla yji mkhallat w ydir la folie."), "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0037"},
            {"term": "hachich", "sentence": "il a arrêté de fumer le hachich depuis deux mois.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "حشيشة", "sentence": get_real_text("M-S33-0076", "اعتقد حرية شخصية هاديك مش حشيشة هاديك نعناعة لاني نحب نعناع."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S33-0076"},
            {"term": "حشيش", "sentence": "روحي للسوق واشري حشيش ومعدنوس للشوربة تاع العشية.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 8. G-009: صفيحة / صفيحة (cannabis)
    {
        "term": "صفيحة", "canon": "صفيحة", "drug": "cannabis",
        "rows": [
            {"term": "صفيحة", "sentence": get_real_text("M-S30-0045", "تم توقيف شبكة ومعاهم صفيحة كيف معالج مجهزة للبيع."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0045"},
            {"term": "صفيحة", "sentence": get_real_text("M-S34-0003", "حجز صفيحة من المخدرات كانت موجهة للتوزيع في الحي."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S34-0003"},
            {"term": "safiha", "sentence": "trafic d'une safiha de drogue dans la région.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "صفيحة", "sentence": "حطت الخبز فوق صفيحة حديد ودخلاتو للكوشة يطيب.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "safi7a", "sentence": "rkebna safi7a jdida ta3 l'aluminium f l'khedma.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 9. G-011: الكمية / كمية (cannabis)
    {
        "term": "كمية", "canon": "كمية", "drug": "cannabis",
        "rows": [
            {"term": "كمية", "sentence": get_real_text("M-S25-0004", "حكموه ومعاه كمية معتبرة من الكيف المعالج مجهزة للترويج."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S25-0004"},
            {"term": "كمية", "sentence": get_real_text("M-S28-0001", "ضبط كمية من المخدرات والأقراص المهلوسة بحوزة المتهمين."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S28-0001"},
            {"term": "كمية", "sentence": get_real_text("M-S34-0010", "كمية السموم المحجوزة تبين حجم الخطر على صحة المواطنين."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S34-0010"},
            {"term": "كمية", "sentence": "زيد كمية صغيرة تاع سكر في القهوة باش تنقص المرارة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "kmiya", "sentence": "l'kmiya ta3 l'farina ma tekfich باش نديرو الخبز كامل.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 10. G-012: spice / سبايس (cannabis)
    {
        "term": "سبايس", "canon": "سبايس", "drug": "cannabis",
        "rows": [
            {"term": "سبايس", "sentence": get_real_text("M-S36-0007", "المخدرات هادي سبايس تخلي الشاب يغيب عن الوعي تماما."), "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S36-0007"},
            {"term": "spice", "sentence": "dreb dokhan spice w wlla y3ayet w khayef bla sba.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "spice", "sentence": "c'est une drogue synthétique appelée spice très dangereuse.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "سبايس", "sentence": "شريت سبايس تاع الطياب هندي فيه ريحة شابة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "spice", "sentence": "darna les épices w spice f l'makla باش تجي بنينة.", "script": "mixed-fr", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 11. G-013: صاروخ / صاروخ (pills)
    {
        "term": "صاروخ", "canon": "صاروخ", "drug": "pills",
        "rows": [
            {"term": "صاروخ", "sentence": get_real_text("M-S28-0004", "تلقى شباب صغار يبلعو الصاروخ والحمراء ويطيحو في الغيبوبة."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S28-0004"},
            {"term": "الصاروخ", "sentence": get_real_text("M-S35-0001", "الصاروخ هبل الشباب في الحومة وما بقاوش يعقلو حتى والديهم."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0001"},
            {"term": "saroukh", "sentence": get_real_text("M-S30-0044", "rah yakhod saroukh 300 mg w dima 3inih 7omr."), "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0044"},
            {"term": "صاروخ", "sentence": get_real_text("M-S35-0014", "شراب ولا صاروخ الزوالي دايخ بيناتهم."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S35-0014"},
            {"term": "صاروخ", "sentence": "أطلقت وكالة الفضاء صاروخ جديد حامل للأقمار الصناعية.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 12. G-015: الحمراء / حمرة (pills)
    {
        "term": "الحمراء", "canon": "حمرة", "drug": "pills",
        "rows": [
            {"term": "الحمراء", "sentence": get_real_text("M-S35-0011", "يشربو كاشيات الحمراء تاع البوليز مع الما ويديرو المشاكل."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0011"},
            {"term": "الحمراء", "sentence": get_real_text("M-S37-0006", "الحمراء والمهلوسات دمرت عائلات بأكملها ربي يعفو عليكم خوتي."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0006"},
            {"term": "hamra", "sentence": "il mélange la hamra avec l'alcool chaque weekend.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "حمراء", "sentence": "لبست فستان لونو وردة حمراء في العرس تاع بنت خالتها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "7amra", "sentence": "chrit tomobil 7amra jdida men la maison.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 13. G-016: zar9a / زرقة (pills)
    {
        "term": "زرقة", "canon": "زرقة", "drug": "pills",
        "rows": [
            {"term": "زرقة", "sentence": get_real_text("M-S35-0008", "كاشيات الحبة الزرقة هادوك تاع الأعصاب هلكو الصحة."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0008"},
            {"term": "zar9a", "sentence": "chrab zar9a ta3 les nerfs bla ordonnance w tgham 3lih.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "zarqa", "sentence": "il a avalé une gélule zarqa avant de dormir.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "زرقة", "sentence": "السماء كانت صافية وزرقة اليوم وما كاين حتى غيمة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "zar9a", "sentence": "chrit tricot couleur zar9a chbab bezzaf l'khouya.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 14. G-017: التاكسي / تاكسي (pills)
    {
        "term": "التاكسي", "canon": "تاكسي", "drug": "pills",
        "rows": [
            {"term": "التاكسي", "sentence": get_real_text("M-S30-0028", "حكمو كمية تاع التاكسي 300 عند مروج كان يبيع للشباب."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0028"},
            {"term": "taxi", "sentence": get_real_text("M-S30-0026", "dreb haba taxi w wlla dayekh ma yqderch ymchi f triq."), "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0026"},
            {"term": "ليريكا", "sentence": get_real_text("M-S37-0009", "هنا في أوروبا ليريكا دواء تاع العضم والتاكسي يستعملوه بحذر كبير."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0009"},
            {"term": "تاكسي", "sentence": get_real_text("M-S30-0027", "خرجت للشارع وحكمت تاكسي باش نلحق للخدمة بكري."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0027"},
            {"term": "taxi", "sentence": "win nelqa taxi bach nrouh l l'aéroport drouk?", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 15. G-018: 7alwa / حلوة (pills)
    {
        "term": "الحلوى", "canon": "حلوة", "drug": "pills",
        "rows": [
            {"term": "الحلوى", "sentence": get_real_text("M-S30-0001", "على حساب واش فهمت الحلوى هي المخدرات لي راهم يخرجوها في السري."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0001"},
            {"term": "7alwa", "sentence": get_real_text("M-S35-0017", "sahbi klé 7alwa f la fête w wlla yhelwes w ma 3refnach."), "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S35-0017"},
            {"term": "exta", "sentence": get_real_text("M-S38-0003", "أنا ل exta والحلوة تعبتني و دمرتني و نحب نتعالج والله تعبت."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S38-0003"},
            {"term": "حلوة", "sentence": get_real_text("M-S30-0002", "يا زنقا ريحو هكدا غير ولاد الحومة والله حلوة وتضحك من قلبك ربي يوفقكم."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0002"},
            {"term": "7alwa", "sentence": "mama taybet 7alwa bnina ta3 l'3id w darna l'qahwa.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 16. G-020: la roche / لاروش (pills)
    {
        "term": "لاروش", "canon": "لاروش", "drug": "pills",
        "rows": [
            {"term": "لاروش", "sentence": get_real_text("M-S30-0018", "الريفوتريل ولاروش واش كانت دير في الدار تع البوليس والإدمان."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0018"},
            {"term": "لاروش", "sentence": get_real_text("M-S30-0029", "أقراص لاروش والحبوب هاديك تتباع بالسري وتدمر العقل."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0029"},
            {"term": "la roche", "sentence": "il consomme des comprimés de la roche sans ordonnance.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "لاروش", "sentence": "شريت بومادا شابة تاع لاروش بوزاي من لافارماسي للوجه.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "la roche", "sentence": "q3adna fouq la roche f l'bhar nchoufo l'mouj.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 17. G-026: cachiyates / كاشيات (pills)
    {
        "term": "كاشيات", "canon": "كاشيات", "drug": "pills",
        "rows": [
            {"term": "كاشيات", "sentence": get_real_text("M-S30-0011", "ونتوما عطيتونا غير الكاشيات و تعمار الراس بالسموم."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0011"},
            {"term": "كاشيات", "sentence": get_real_text("M-S30-0010", "عندك الحق خلوطة كبيرة بعدا الحلقة تاع اليوم والكاشيات لي يهدرو عليهم."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0010"},
            {"term": "كاشيات", "sentence": get_real_text("M-S30-0012", "المسلسلات يهدرو على الكاشيات والإدمان مالقري عنده سنين."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0012"},
            {"term": "كاشيات", "sentence": get_real_text("M-S31-0003", "الحمد لله عل نعمة العقل.. عمري سنة نخدم عل دارنا واهلي منسكر ما نتكيف كاشيات."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S31-0003"},
            {"term": "cachiyates", "sentence": "lazem nchreb cachiyates ta3 l'vitamine C kol sba7.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 18. G-027: قفالي / قفالي (pills)
    {
        "term": "قفالي", "canon": "قفالي", "drug": "pills",
        "rows": [
            {"term": "قفالي", "sentence": get_real_text("M-S35-0003", "هاد الصوالح وحبوب القفالي خربت المجتمع والشباب راهم ضايعين."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0003"},
            {"term": "qfali", "sentence": "chrab habat qfali m3a l'bira w dkhlo f غيبوبة.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "qfali", "sentence": "il a pris deux qfali pour oublier ses problèmes.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "قفالي", "sentence": "طاحولي زوج قفالي من الفيستة ولازم نديها للخياط يركبهم.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "qfali", "sentence": "qfali ta3 l'qamija tqet3o w drouk ma nqderch nelbessha.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 19. G-028: الحبوب / حبوب (pills)
    {
        "term": "حبوب", "canon": "حبوب", "drug": "pills",
        "rows": [
            {"term": "حبوب", "sentence": get_real_text("M-S30-0031", "الحبوب والمهلوسات هادو هما لي خلاو الجريمة تزيد في بلادنا."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0031"},
            {"term": "حبوب", "sentence": get_real_text("M-S31-0010", "شكون راه يدخل زطلا وحبوب للبلاد هادو هما لي هلكو الشباب."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S31-0010"},
            {"term": "حبوب", "sentence": get_real_text("M-S35-0005", "دار أوفر دوز بسبايب حبوب الأعصاب وداوه للإسقاع مستعجل."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0005"},
            {"term": "حبوب", "sentence": "الفلاح زرع حبوب القمح والشعير في الأرض بعد ما صبت النو.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "hboub", "sentence": "kharjouli hboub sghar f wejhi men l'chmisa lazm كريم.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 20. G-029: اللومبات / لومبات (pills)
    {
        "term": "اللومبات", "canon": "لومبات", "drug": "pills",
        "rows": [
            {"term": "اللومبات", "sentence": get_real_text("M-S30-0034", "كاشيات اللومبات يديرو خفة العقل ويفقدو بنادم الوعي."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0034"},
            {"term": "اللومبات", "sentence": get_real_text("M-S36-0009", "هاد الصوالح واللومبات لي راهم يبيعوهم للدراري سموم خطيرة."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S36-0009"},
            {"term": "loumbat", "sentence": "il vend des comprimés loumbat aux jeunes du quartier.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "لومبات", "sentence": "شريت زوج لومبات ليد بيوضة باش نركبهم في الكوزينة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "loumbat", "sentence": "tfeina ga3 les loumbat ta3 l'couloir 9bal ma norqdo.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 21. G-034: المرقازة / مرقازة (pills)
    {
        "term": "المرقازة", "canon": "مرقازة", "drug": "pills",
        "rows": [
            {"term": "المرقازة", "sentence": get_real_text("M-S37-0008", "لادروق وحبات المرقازة هادو هما لي خلاو الشباب يدخل في حيط."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0008"},
            {"term": "merqaza", "sentence": "chrab habat merqaza w wlla dayer hbal f l'houma.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "merguez", "sentence": "on l'appelle merguez à cause de sa forme rouge allongée.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "مرقازة", "sentence": "شريت رطل مرقازة عند البوشي ودرنا بيها عشاء شباب.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "merqaza", "sentence": "chwina merqaza f l'ghaba m3a les amis weekend hada.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 22. G-035: الكريستالة / كريستالة (pills)
    {
        "term": "الكريستالة", "canon": "كريستالة", "drug": "pills",
        "rows": [
            {"term": "الكريستالة", "sentence": get_real_text("M-S37-0012", "تعاطي الكريستالة والمهلوسات يوصل لنهايات مأساوية في السبيطار."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0012"},
            {"term": "kristala", "sentence": "dreb habat kristala m3a sahbo w dakhlo f crise d'angoisse.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "cristale", "sentence": "le dealer proposait de la cristale aux jeunes du café.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "كريستالة", "sentence": "ماما شرات كيسان كريستالة شابين وحطتهم في الفيترينا للضياف.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "kristala", "sentence": "tharsset kristala ta3 l'lustre li f l'salon w lazem nbedlouha.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 23. G-036: double signature / دوبل سينياتور (pills)
    {
        "term": "دوبل سينياتور", "canon": "دوبل سينياتور", "drug": "pills",
        "rows": [
            {"term": "دوبل سينياتور", "sentence": get_real_text("M-S37-0003", "خطر الإدمان يخلي المروجين يحوسو على وصفات دوبل سينياتور بطرق ملتوية."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0003"},
            {"term": "double signature", "sentence": "qabdouh yzower f l'ordonnance double signature ta3 les psychotropes.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "double signature", "sentence": "il faut une double signature médicale pour ces analgésiques.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "دوبل سينياتور", "sentence": "باش ندي الكريدي من لابنك طلبو عليا دوبل سينياتور في الدوسي.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "double signature", "sentence": "l'contrat hada lazmou double signature men l'directeur w l'comptable.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 24. G-037: المارطو / مارطو (pills)
    {
        "term": "المارطو", "canon": "مارطو", "drug": "pills",
        "rows": [
            {"term": "المارطو", "sentence": get_real_text("M-S30-0035", "المارطو لي شربو خلاه دايخ وما قدرش ينوض من الفراش."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0035"},
            {"term": "المارطو", "sentence": get_real_text("M-S35-0012", "ساروخ والمارطو راهم يتباعو في الحومة وما خلو حتى عقل للشباب."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0012"},
            {"term": "marteau", "sentence": "cette pilule frappe comme un marteau sur la tête.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "مارطو", "sentence": get_real_text("M-S33-0069", "لالا عندي شونطي مارطو بيكور ماكيطا حبيبي راهو نوفو كونتور قالولي عندك شونطي نجي نخدم."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S33-0069"},
            {"term": "مارطو", "sentence": "جيبلي المارطو والمسامر باش نخدم هاد الطابلة لي تكسرت.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 25. G-038: الناموسة / ناموسة (pills)
    {
        "term": "الناموسة", "canon": "ناموسة", "drug": "pills",
        "rows": [
            {"term": "الناموسة", "sentence": get_real_text("M-S35-0013", "حبة الناموسة والصاروخ هادوك يتباعو بالسرقة بين الشباب في الكوانات."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0013"},
            {"term": "الناموسة", "sentence": get_real_text("M-S35-0002", "الإدمان على الناموسة والأقراص خلا الشباب يضيعو حياتهم وقرايتهم."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0002"},
            {"term": "namousa", "sentence": "le dealer avait plusieurs comprimés de namousa sur lui.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "ناموسة", "sentence": get_real_text("M-S33-0073", "خخخ نتا ناموسة ما تقدر دير والو غير الهدرة الزايدة."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S33-0073"},
            {"term": "ناموسة", "sentence": "قرصتني ناموسة البارح في يدي وحكمتني حكة كبيرة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 26. G-039: الدومينو / دومينو (pills)
    {
        "term": "الدومينو", "canon": "دومينو", "drug": "pills",
        "rows": [
            {"term": "الدومينو", "sentence": get_real_text("M-S37-0002", "فيلم يمثل الواقع وحبوب الدومينو ربي يعفو على كل مبلي."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S37-0002"},
            {"term": "domino", "sentence": "habat domino mkhallta m3a l'chrab daratlo overdose f lil.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "domino", "sentence": "ils ont saisi des cachets gravés en forme de domino.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "دومينو", "sentence": "قعدنا نلعبو الدومينو في القهوة بعد صلاة المغرب مع الجماعة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "domino", "sentence": "rbe7t partie domino chaba contre sahbi f l'houma.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 27. G-045: rouge / روج (pills)
    {
        "term": "روج", "canon": "روج", "drug": "pills",
        "rows": [
            {"term": "روج", "sentence": get_real_text("M-S25-0002", "الروج والكاشيات هادو هما لي راهم مخرجين الشباب على عقلهم ويزطلو كل يوم."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S25-0002"},
            {"term": "روج", "sentence": get_real_text("M-S25-0001", "أنا شخصيا بلغت أكثر من مرة على مروج كاشيات روج في الحي وما تحرك حد."), "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S25-0001"},
            {"term": "rouge", "sentence": get_real_text("M-S34-0002", "hboub rouge w les comprimés dakhlo bzaf drari f triq l'in7iraf."), "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S34-0002"},
            {"term": "روج", "sentence": "شرات روج شافي وماكياج جديد من لافوار للعرس.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "rouge", "sentence": "daret veste rouge chaba li lbestha f la soutenance.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 28. G-046: 9ar3a / قرعة (alcohol)
    {
        "term": "قرعة", "canon": "قرعة", "drug": "alcohol",
        "rows": [
            {"term": "قرعة", "sentence": get_real_text("M-S30-0007", "سنة يخدم بقرعة بيرة فلاريسبسيون كي تلحق العشية."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0007"},
            {"term": "قرعة", "sentence": get_real_text("M-S30-0005", "زوج عجوزات طاحو على قرعة شراب وشربوها كاملة حتى سكروا."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0005"},
            {"term": "قرعة", "sentence": get_real_text("M-S30-0006", "الحمدلله حتى ليوم باش شفت حلقة شابة وشبي جدكم لعام لي فات قرعة ويسكي."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0006"},
            {"term": "بيرة", "sentence": get_real_text("M-S30-0008", "روح للقناة تاعك احكيلهم كيفاش تليفري البيرة وقرعة الما."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0008"},
            {"term": "قرعة", "sentence": "عطيني قرعة ما باردة راني عطشان بزاف من السخانة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 29. G-047: شراب / شراب (alcohol)
    {
        "term": "شراب", "canon": "شراب", "drug": "alcohol",
        "rows": [
            {"term": "شراب", "sentence": get_real_text("M-S30-0019", "شراب الويسكي لي ضحكاته هاد لقطة يدير جام ويكف عن البلية."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0019"},
            {"term": "شراب", "sentence": get_real_text("M-S30-0038", "الشراب هذا راه مرض في الكبدة ويخرب ديار العائلات."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0038"},
            {"term": "شراب", "sentence": get_real_text("M-S30-0039", "إذا ماتشوكيتيش من الشراب لي هو من الكبائر منين تشوكاي الجيل تاع دوك."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0039"},
            {"term": "chrab", "sentence": get_real_text("M-S30-0042", "ldjiha li yroha liha ywesskhoha b zbel w chrab apres yolek makach win nhawsso."), "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "M-S30-0042"},
            {"term": "شراب", "sentence": "عطاني الطبيب شراب تاع السعلة نشرب منو مغرف في الليل.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 30. G-049: l'alcool / لالكول (alcohol)
    {
        "term": "لالكول", "canon": "لالكول", "drug": "alcohol",
        "rows": [
            {"term": "لالكول", "sentence": get_real_text("M-S30-0016", "يا دقيوس مقيوس تاع زمر اعلاش تلعبو زعمى خمر و لالكول عيب عليكم."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0016"},
            {"term": "l'alcool", "sentence": get_real_text("M-S30-0040", "bghit nhabes l'alcool win nlqa centre d'aide f wahren?"), "script": "arabizi", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0040"},
            {"term": "بيرا", "sentence": get_real_text("M-S30-0009", "كيما لوسكي كيما لبيرا كي الفوتكا لالكول كامل يضر الصحة."), "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0009"},
            {"term": "لالكول", "sentence": "نقي الجرح بشوية قطن و لالكول طبي باش ما يتعفنش.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "l'alcool", "sentence": "chrit l'alcool 70 degrés men l'pharmacie باش نعقم بيه الدوزان.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 31. G-052: الغبرة / غبرة (cocaine)
    {
        "term": "الغبرة", "canon": "غبرة", "drug": "cocaine",
        "rows": [
            {"term": "الغبرة", "sentence": get_real_text("M-S30-0032", "الغبرة البيضاء هاديك راهي سم قاتل يخرب القلب والعروق."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0032"},
            {"term": "ghabra", "sentence": get_real_text("M-S33-0067", "dreb ghabra f la fête w wlla qelbo yakhbet bzaf."), "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "M-S33-0067"},
            {"term": "غبرة", "sentence": get_real_text("M-S33-0102", "مزطول مصورخ سكران يدير كلش غبرة برك جيه غالية كون غبر تان."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S33-0102"},
            {"term": "غبرة", "sentence": "الريح والجاج عَمرو الدار كاملة بالغبرة ولازم نسيقوها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "ghabra", "sentence": "khelat l'ghabra ta3 l'hlib m3a l'ma dافي باش يشرب الصغير.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 32. G-053: beida / بيضاء (cocaine)
    {
        "term": "البيضاء", "canon": "بيضاء", "drug": "cocaine",
        "rows": [
            {"term": "البيضاء", "sentence": get_real_text("M-S37-0005", "السموم البيضاء هادي راهي تهلك في ولادنا ولازم وقفة حقيقية."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S37-0005"},
            {"term": "لخماج", "sentence": get_real_text("M-S36-0004", "ربي يفرج علينا ونطيشو هاد لخماج والغبرة البيضاء والله تعبنا."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S36-0004"},
            {"term": "blanche", "sentence": "il consomme de la blanche et il ne mange plus rien.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "بيضاء", "sentence": "كليت حبة بيضاء مغلية مع الصباح قبل ما نروح نقرا.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "beida", "sentence": "lbest qamija beida nqiya l'salat l'djoumou3a.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 33. G-054: coke / كوك (cocaine)
    {
        "term": "كوكايين", "canon": "كوك", "drug": "cocaine",
        "rows": [
            {"term": "كوكايين", "sentence": get_real_text("M-S34-0008", "الكوكايين هادي راهي تدخل بطرق غير شرعية وتدمر الشباب."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S34-0008"},
            {"term": "كوكاين", "sentence": get_real_text("M-S30-0048", "شحال من واحد تلف حياتو بسبايب الكوكاين والفلوس الحرام."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0048"},
            {"term": "coke", "sentence": get_real_text("M-S30-0047", "il a sniffé de la coke dans les toilettes de la boîte."), "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0047"},
            {"term": "كوكايين", "sentence": get_real_text("M-S30-0049", "قضية كوكايين خرج نظيف منها بصح الكوكا كولا يشربوها كامل الناس."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0049"},
            {"term": "كوكا", "sentence": "اشريلي قرعة كوكا كولا باردة نشربوها مع البيتزا في الليل.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 34. G-055: crack / كراك (cocaine)
    {
        "term": "كراك", "canon": "كراك", "drug": "cocaine",
        "rows": [
            {"term": "كوكايين", "sentence": get_real_text("M-S34-0009", "في وقت الإستعمار لم تكن هناك لا مخدرات و لا كراك و لا هم يحزنون."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S34-0009"},
            {"term": "crack", "sentence": "fumé du crack avec un tuyau w drouk sdro yharqo bezzaf.", "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "crack", "sentence": "le crack provoque une dépendance psychologique immédiate.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "كراك", "sentence": "تيليشارجيت كراك تاع اللعبة باش نقدر نلعبها بلا سيريال.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "crack", "sentence": "sahbi crack f les maths yjib dima 20 f l'examen.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 35. G-057: el kheit / خيط (cocaine)
    {
        "term": "خيط", "canon": "خيط", "drug": "cocaine",
        "rows": [
            {"term": "خيط", "sentence": get_real_text("M-S35-0024", "راني نشوف فالفيديو ودمعتي على خدي خيط كوكايين تلفني وضيعلي حياتي."), "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S35-0024"},
            {"term": "kheit", "sentence": "sterna kheit ta3 ghabra w wlla galbo ybatt bzaf.", "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "ligne", "sentence": "il a tracé une ligne de poudre blanche sur son téléphone.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "خيط", "sentence": "خيط التريسينتي تقطع ولازم نجيبو التريسيان يعاودو.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "kheit", "sentence": "kheit l'chargeur thares w ma bqach ychargi l'portable.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 36. G-059: 7o9na / حقنة (heroin)
    {
        "term": "حقنة", "canon": "حقنة", "drug": "heroin",
        "rows": [
            {"term": "حقنة", "sentence": get_real_text("M-S30-0003", "نتا راك متأثر بفيديوهاتو و ماتعرفش النفاق لي يدير فيه حقنة هيروين تهرد صحتك."), "script": "arabic", "sense": "drug", "drug": "heroin", "origin": "M-S30-0003"},
            {"term": "حقنة", "sentence": get_real_text("M-S38-0001", "Kont netkayef kolyoum w dkhalt f l'7oqna ta3 l'heroin w Hamdoulah bataltha."), "script": "arabizi", "sense": "drug", "drug": "heroin", "origin": "M-S38-0001"},
            {"term": "seringue", "sentence": "partager une seringue pour injecter la drogue transmet les virus.", "script": "mixed-fr", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "حقنة", "sentence": get_real_text("M-S30-0004", "حيياك يا خويا فعلا شخصية إيجابية بإمتياز حقنة تحفيز جيدة لجميع الشباب."), "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0004"},
            {"term": "7oqna", "sentence": "darouli 7oqna ta3 l'vaccin f sbitar w ma wj3atnich bezzaf.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 37. G-064: héroïne / هيروين (heroin)
    {
        "term": "هيروين", "canon": "هيروين", "drug": "heroin",
        "rows": [
            {"term": "هيروين", "sentence": get_real_text("M-S36-0001", "انا رحت مركز علاج الإدمان بعد ما هلكتني الهيروين والحمد لله كاين تحسن."), "script": "arabic", "sense": "drug", "drug": "heroin", "origin": "M-S36-0001"},
            {"term": "heroine", "sentence": "sahbi wlla y7qan l'heroine w drouk rah f sbitar mrid.", "script": "arabizi", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "héroïne", "sentence": "la surdose d'héroïne peut provoquer un arrêt respiratoire immédiat.", "script": "mixed-fr", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "هيروين", "sentence": "البطلة في الرواية هاديك كانت هيروين حقيقية أنقذت شعبها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "héroïne", "sentence": "l'actrice l3bat rôle ta3 héroïne f l'film l'djedid li khrej.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
]

# Flatten and assign sequential ctx_id
out_rows = []
ctx_num = 1
for term_data in DATA:
    canon = term_data["canon"]
    for r in term_data["rows"]:
        cid = f"C-{ctx_num:03d}"
        ctx_num += 1
        out_rows.append({
            "ctx_id": cid,
            "term": r["term"],
            "canonical_spelling": canon,
            "sentence": r["sentence"],
            "script": r["script"],
            "sense": r["sense"],
            "drug": r["drug"],
            "origin": r["origin"],
            "written_by": "Mohamed Ayoub Belhimer"
        })

print(f"Generated {len(out_rows)} rows.")
real_count = sum(1 for r in out_rows if r["origin"] != "invented")
print(f"Real count: {real_count} / {len(out_rows)} ({real_count/len(out_rows)*100:.1f}%)")

# Write CSV
csv_path = "NLP-Project16/04-glossary-and-rules/context-set-v1.csv"
fieldnames = ["ctx_id", "term", "canonical_spelling", "sentence", "script", "sense", "drug", "origin", "written_by"]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)

print(f"Saved CSV to {csv_path}")

# Convert to XLSX using LibreOffice
xlsx_path = "NLP-Project16/04-glossary-and-rules/context-set-v1.xlsx"
outdir = "NLP-Project16/04-glossary-and-rules"
cmd = ["soffice", "--headless", "--convert-to", "xlsx", csv_path, "--outdir", outdir]
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"LibreOffice conversion output: {res.stdout.strip()}")
if os.path.exists(xlsx_path):
    print(f"Successfully created XLSX at {xlsx_path} (size: {os.path.getsize(xlsx_path)} bytes)")
else:
    print(f"Error creating XLSX: {res.stderr}")
