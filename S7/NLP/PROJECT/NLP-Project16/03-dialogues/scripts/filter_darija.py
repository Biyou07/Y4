"""Filter the public Darija datasets (S30-S32) into the two dataset-format-v1 sheets.

messages: lines that contain a glossary term  -> 03-dialogues/messages_real_malak.{csv,xlsx}
general:  ordinary Darija lines with no term   -> 03-dialogues/darija-general-v1.{csv,xlsx}

Run from anywhere:
    python filter_darija.py messages --glossary glossary_starter_malak.csv
    python filter_darija.py general  --glossary glossary_starter_malak.csv
"""
import argparse
import random
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

MALAK_ROOT = Path(__file__).resolve().parents[2]
RAW = MALAK_ROOT / "01-sources" / "raw"
OUT = MALAK_ROOT / "03-dialogues"

ARABIC_LETTER = re.compile(r"[ء-يٱ-ۓڤکگ]")
LATIN_LETTER = re.compile(r"[A-Za-zÀ-ÿ]")
ARABIC_DIACRITICS = re.compile(r"[ً-ْٰـ]")

URL = re.compile(r"(https?://\S+|www\.\S+|\S+\.(com|net|org|dz|fr)\S*)", re.I)
EMAIL = re.compile(r"\S+@\S+\.\S+")
MENTION = re.compile(r"@[\w.؀-ۿ]+")
# A number is a run of digits not glued to letters, so Arabizi letters like 3, 7 and 9 in "ta3" or "7aja" survive.
STANDALONE_NUMBER = re.compile(r"(?<![\w؀-ۿ])[+]?[\d٠-٩][\d٠-٩ .,:/-]*(?![\w؀-ۿ])")

DARIJA_ARABIC_MARKERS = set("""
بزاف واش كيفاش علاش راني راك راكي راه راهي راهو راهم راهوم ماشي بصح تاع تاعي تاعك تاعو ديال نتا نتي نتوما حنا
هاذ هاذا هاذي هادو هذوك شحال درك دروك ضرك باه باش كاين كاينة كاينين مكانش ماكانش برك والو خويا ختي ياخو صحا
صحيت يعطيك بلاك مزال مازال ڨاع قاع شوية شويا بالاك علابالك وين منين كيما هكا ياسر مليح مليحة زعما زعمة يزي
نحب نحبك نشوف نقول ندير نروح نسيت حاب حابة حابين بغيت نديرو ديرو قولي قولو جاب نجيب نشالله
مرا ولاه يخي ڨلبي هدرة نهدر يهدر تهدر الهدرة دراهم صوالح غي بلي كي واقيلا ياك
علاه ضوك ضك بكري كامل يخويا ديالكم ديالي ديالو يحوس يحوسو لراك مين تع هاد هاذ غير ولله كيفي ساهل حبست علاش راكوم رانا نتوما
""".split())

DARIJA_LATIN_MARKERS = set("""
wach wech wesh rani rak raki rah rahi raho rahom bzaf bezaf bezzaf kifach kifech kifeh 3lach 3la ta3 ta3i ta3ek nta nti
ntoma hna hada hadi hado kayen kayn kayna makach makanch mazal mazel khoya khouya sahbi sah sa7 sa7a saha bark ghir
walou walo wallah wlh wellah nchallah inchallah incha rabi ya3tik ya3tek dork drk dorka bach ki kima chwiya chwia chouia
mlih mli7 zaama za3ma yakhi mchi machi ndir ndiro n7eb nheb n7ab tbghi bghit 3andi 3andek kho khti hakda haka bladi
lbled bled yasser yaser normal hadja 7aja 7ajja wahd wa7ed 9al gal tani bessah bsah lazem rabbi chkoun chkon win fin mnin
""".split())

FRENCH_WORDS = set("""
le la les un une des de du et est pas je tu il elle nous vous ils que qui pour avec dans sur mais ou donc ce cette ces
mon ma mes ton ta tes son sa ses plus tres bien tout tous comme faire fait vie merci bonjour aussi meme quand alors
""".split())


def normalise(text):
    text = unicodedata.normalize("NFC", text).lower()
    text = ARABIC_DIACRITICS.sub("", text)
    text = re.sub("[أإآٱ]", "ا", text)
    text = text.replace("ة", "ه").replace("ى", "ي").replace("ڨ", "ق").replace("ڤ", "ف").replace("گ", "ك")
    text = text.translate(str.maketrans("éèêëàâîïôöûüç", "eeeeaaiioouuc"))
    return re.sub(r"(.)\1+", r"\1", text)


def anonymise(text):
    text = URL.sub(" ", text)
    text = EMAIL.sub(" ", text)
    text = MENTION.sub(" ", text)
    text = STANDALONE_NUMBER.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text):
    return re.findall(r"[\w؀-ۿ']+", normalise(text))


def script_of(text):
    arabic = len(ARABIC_LETTER.findall(text))
    latin = len(LATIN_LETTER.findall(text))
    if arabic and arabic >= latin:
        return "arabic"
    if not latin:
        return None
    words = tokens(text)
    french = sum(w in FRENCH_WORDS for w in words)
    return "mixed-fr" if french >= 2 and french >= len(words) / 5 else "arabizi"


ARABIC_MARKERS = {normalise(w) for w in DARIJA_ARABIC_MARKERS}
LATIN_MARKERS = {normalise(w) for w in DARIJA_LATIN_MARKERS}


def is_darija(text, script, relaxed=False):
    words = tokens(text)
    if script == "arabic":
        negation = any(len(w) > 4 and w.startswith("ما") and w.endswith("ش") for w in words)
        min_markers = 1 if relaxed else 2
        return negation or len(ARABIC_MARKERS.intersection(words)) >= min_markers
    if script in ("arabizi", "mixed-fr"):
        negation = any(len(w) > 4 and w.startswith("ma") and w.endswith("ch") for w in words)
        digit_letter = any(re.search(r"[a-z][379]|[379][a-z]", w) for w in words)
        return negation or digit_letter or sum(w in LATIN_MARKERS for w in words) >= 1
    return False


def load_sources():
    s30 = pd.read_parquet(RAW / "S30_algerian_darija_hf" / "v1-00000-of-00001.parquet")
    yield from (("S30", t) for t in s30["Text"].dropna())
    s31 = pd.read_csv(RAW / "S31_youtube_comments_mendeley" / "ADArabic-cla-GE-t-l-lu-lc-vu-ad-45000.csv", usecols=["text"])
    yield from (("S31", t) for t in s31["text"].dropna())
    for split in ("train", "dev", "test"):
        conllu = (RAW / "S32_narabizi_treebank" / f"qaf_arabizi-ud-{split}.conllu").read_text(encoding="utf-8")
        yield from (("S32", line[len("# text = "):]) for line in conllu.splitlines() if line.startswith("# text = "))
    s33_path = RAW / "S33_algerian_darja_telegram" / "darja_corpus_telegram_2026-04-19.parquet"
    if s33_path.exists():
        s33 = pd.read_parquet(s33_path)
        col = "text" if "text" in s33.columns else s33.columns[0]
        yield from (("S33", t) for t in s33[col].dropna())


# YouTube replies often open with the Latin-script handle of the person answered ("archi الله يسلمك").
LEADING_LATIN_HANDLE = re.compile(r"^(?:[A-Za-z][\w.]*\s+){1,3}(?=[؀-ۿ])")
MAX_WORDS = 60

# Profanity and vulgarity filtering to exclude toxic or obscene social media comments.
BAD_WORDS_PATTERNS = [
    re.compile(r'(?:^|[^\w؀-ۿ])(?:ال|و|ف|ب|ل|وال|فال|بال|لل)?(?:زب[يناهوم]*|زك[يناهوم]*|منيك[ةهينوا]*|تناك[و]*|نيكت?[هموا]*|طحان[ةهينوا]*|قحب[ةهات]*|قحاب|ترم[ةه][كهما]*|خرا[ي]?|خري[ةه]|خريت[وا]*|زامل|زوامل|شمايت)(?:[^\w؀-ۿ]|$)', re.IGNORECASE),
    re.compile(r'(?:^|[^\w؀-ۿ])تفو+ه*(?:[^\w؀-ۿ]|$)', re.IGNORECASE),
    re.compile(r'\b(?:el)?[9q]a[h7]b?[ae]?[sh]?\b', re.IGNORECASE),
    re.compile(r'\b(?:el)?9hab\b', re.IGNORECASE),
    re.compile(r'\b(?:el)?z(e)?b+(i|na)?\b', re.IGNORECASE),
    re.compile(r'\b(?:m)?n(i|y)(a)?(e)?k(e)?(?:t|in)?\b', re.IGNORECASE),
    re.compile(r'\bniyake\b', re.IGNORECASE),
    re.compile(r'\bt(a)?ha+n\b', re.IGNORECASE),
    re.compile(r'\btfou+\b', re.IGNORECASE),
    re.compile(r'\btfo+h\b', re.IGNORECASE),
    re.compile(r'\bterm(a|ek|ha)\b', re.IGNORECASE),
    re.compile(r'\bkhra[y]?\b', re.IGNORECASE),
    re.compile(r'\bzw?amel\b', re.IGNORECASE),
    re.compile(r'(?:^|[^\w؀-ۿ])(?:ال|و|ف|ب|ل)?قلاو[يهك]+(?:[^\w؀-ۿ]|$)', re.IGNORECASE),
    re.compile(r'(?:^|[^\w؀-ۿ])[ينت]خر[ىي](?:[^\w؀-ۿ]|$)', re.IGNORECASE),
    re.compile(r'(?:اولاد|ولاد)\s+(?:ال|ل)?حرام', re.IGNORECASE),
    re.compile(r'(?:^|[^\w؀-ۿ])(?:ال|و|ف|ب|ل)?شكبي(?:[^\w؀-ۿ]|$)', re.IGNORECASE),
]


def has_bad_word(text):
    for pattern in BAD_WORDS_PATTERNS:
        if pattern.search(text):
            return True
    return False


def is_gibberish(text, script):
    words = text.split()
    if len(words) >= 4 and sum(len(w) == 1 for w in words) > len(words) / 2:
        return True
    if script == "arabic" and sum(w.startswith("ى") for w in words) >= 2:
        return True
    return False


def clean_lines(relaxed=False):
    """Anonymised, de-duplicated Darija/Arabizi lines, with their script."""
    seen = set()
    max_words = 90 if relaxed else MAX_WORDS
    for source_id, raw in load_sources():
        text = anonymise(str(raw))
        script = script_of(text)
        if script == "arabic":
            text = LEADING_LATIN_HANDLE.sub("", text)
        if not script or len(text.split()) > max_words or is_gibberish(text, script) or not is_darija(text, script, relaxed=relaxed) or has_bad_word(text):
            continue
        key = " ".join(tokens(text))
        if key in seen:
            continue
        seen.add(key)
        yield source_id, script, text


ARABIC_PREFIXES = ("", "و", "ب", "ف", "ل", "ال", "وال", "بال", "فال", "لل")
DROP_PREFIXED_FORMS = {"فروج", "بروج", "لروج", "لحقن"}

DROP_SINGLE_VARIANTS = {
    "كيف", "kif",                          # means 'how/like'; keep الكيف / el kif / lkif / قارو كيف
    "morceau", "morso",                    # music track; keep phrase 'morceau zatla'
    "cox", "coks", "كوكس",                 # biology COX enzyme / بر كوكس
    "canon", "canons", "كانون", "kanoun",  # Canon cameras / French idiom
    "black", "brown", "الاسمر",            # colors / race
    "royal", "royale", "رويال",            # Clash Royale / army
    "shit",                                # English swear word
    "roche", "روش",                        # beach / Mini Roche; keep la roche / laroche / لاروش / حبوب روش
    "كراك",                                # Darija 'كي راك' without space; keep الكراك / crack
    "المسك", "الهباله", "hbala", "حزمه", "hazma", "7azma",  # broken sub-variants
    "فاليوم",                              # Arabic 'في اليوم' (per day); keep valium/diazepam/فالبام
    "كوك", "coke", "كوكا", "coca",         # Hicham Cook / Coca-Cola / Algerian 'كوكا' tart
    "ice",                                 # English ice
    "سمطه", "samta", "semta", "السمطه",    # Darija 'boring/tasteless' (صامطة)
    "wed",                                 # normalised 'weed' collides with Algerian 'wed' (واد/river)
    "marto", "l'marto", "el marto",        # Darija Arabizi 'مرتو' (his wife), not French 'marteau'
    "كفالي",                               # football coach Cavalli; keep لكفالي
    "جامبو", "jambo",                      # Jumbo bouillon cube; keep jambon / جامبون
    "bouf", "بوف",                         # unverified; collides with French 'la bouffe' (food)
    "ليريك",                               # collides with 'لـ + يريك' (to show you); keep ليريكا / lyrica
    "chrabt",                              # verb 'I drank' (e.g. 'chrabt dwa'), not noun 'شراب' (alcohol)
    "افيون", "الافيون",                    # in Algerian Arabic, 'افيون' almost always means French 'avion' (airplane)
}

LOTTERY_RE = re.compile(
    r"امريكا|اميريكا|ميريكان|الامريك|العشوائي|عشوئي|عشواي|gren|green|قرين|غرين|مسابق|ربح|نربح|فزت|فاز|"
    r"ينجح|نجح|دعولي|ادعولي|حظك|فيزا|هجر|سجل|نسجل|بكالوريا|الضامن|مستضيف|حج|سكن|السكن|"
    r"جوائز|سحب|فايس ادس|ما جاتش|تخرج فالقرع|تخرج في القرع",
    re.I,
)
QAR3A_BALD_BAD_RE = re.compile(
    r"السيناريوهات القرع|جا قرع|مرقها قرع|ذاك القرع|قرعه ميعرقش|قرعه فور|وهو قرعه|"
    r"كاميرا كاشي القرع|قرعه تع الحراش|ورقه القرع|حسله قرعه|صويلح قرعه|بلاصت كاميرا كاشي القرع|"
    r"عاشور قرعه|قرعه والفاهم|قرعه بزاف",
    re.I,
)
CAMERA_CACHEE_RE = re.compile(
    r"كاميرا كاشي|كاميرات كاشي|كاميره كاشي|كامره كاشي|كميرا كاشي|كميرات كاشي|"
    r"كميره كاشي|كمرا كاشي|كميراء كاشي|لكميراء كاشي|الكاميرا الكاشي|خلعه كاشي|فيلم كاشي",
    re.I,
)
JOINT_CAR_RE = re.compile(r"joint de culase|culase|radiat|جوان كيلاص|جوان كلاس", re.I)
ROUGE_FP_RE = re.compile(
    r"rouge a levre|rouge levre|levre|بوا روج|روج زجاج|pasport rouge|zone rouge|vilage rouge|carton.*rouge|فو روج",
    re.I,
)
KASS_FP_RE = re.compile(r"لا كاس|تورنور|يبيعو لكاس|فيراي", re.I)
KHIT_FP_RE = re.compile(r"خيط الروح", re.I)
SPICE_FP_RE = re.compile(r"حوش ميهوب", re.I)
DOMINO_FP_RE = re.compile(r"اكل الدومينو|لسبيطار", re.I)
MISC_FP_RE = re.compile(
    r"fa bira|hboub sagya|الحبوب الطيوب|هشام كوك|كوكا كولا|coca cola|مش مورفين|مانيش مورفين|مود افيون|لا تسقني ماء الحياه",
    re.I,
)

DRUG_CONTEXT_RE = re.compile(
    r"مخدرات|مهلوس|تعاطي|(?<![\w؀-ۿ])ن?كمي(?![\w؀-ۿ])|تبلع|نبلع|نضرب حبات|ندرب صاروخ|ndrob saroukh|"
    r"ناكل صاروخ|يبيع الكاشي|يبيع الزطل|منسكر|(?<![\w؀-ۿ])(?:ال)?خمر(?![\w؀-ۿ])|زطل|كوكاين|"
    r"(?<![\w؀-ۿ])(?:ال)?بيره(?![\w؀-ۿ])|ليريكا|قرقوبي|الكاشيات|كاشيات|قارو زطل|قارو كيف|جامي شميت|"
    r"كحول|الكبائر|تع الرقاد|ريفوتريل|alcool|chrab|saroukh|zatla|canabis|cocaine|wiski|"
    r"بقرعه بيره|قرعه شراب|قرع تاع شراب|حامل قرعه|تاع شراب|الشراب|يتناول ف هاذ الحبوب|"
    r"الحلوه هي المخدرات|الحلوي هي المخدرات|محشي بالكيف|قصبه وشراب|لا شراب لا دخان|كباريهات|عري و شراب|محرمات شراب|بزناز|"
    r"يبيع الشير|يكمي الشير|يتكيفو شيرا|شيره.*زطل|زطل.*شير|ايشم الغبر|يشم الغبر|شم الغبر|غبره.*يزطل|"
    r"مثل الصاروخ|اخطار الحبوب المهلوس|شراب روج|قرعه روج|كاشي روج|يشرب الروج|"
    r"هيروين|الهيروين|مورفين|كودايين|سوبوتكس|الميثادون|ترامادول|اكستازي|كيتامين|ماحيا|لادروق|تعمار|يزطل|يتكيف",
    re.I,
)
SHRAB_NORMAL_RE = re.compile(r"الماء تاع شراب|ماكله وشراب|اكل لا شراب|kali charab", re.I)
RAW_WEED_RE = re.compile(r"\bweed\b", re.I)

TIER2_ALLOWED_TERMS = {
    "9ar3a",      # bottle of water / juice
    "حشيش",       # culinary herbs / grass
    "7alwa",      # Eid pastry / sweets
    "l'kass",     # drinking glass / tea / cup
    "صاروخ",      # rocket / missile
    "الغبرة",     # household dust / powdered milk
    "garou",      # ordinary tobacco cigarette
    "التاكسي",    # taxi cab
    "الحبوب",     # grains / crops / pimples / medical tablets
    "طاسة",       # water bowl
    "المارطو",    # hammer
    "صفيحة",      # metal plate / solar panel / platelets
    "الناموسة",   # mosquito
    "اللومبات",   # lightbulb
    "7o9na",      # medical / motivation injection
}


def is_false_positive(term, spelling, text):
    nt = normalise(text)
    if term == "9ar3a" or spelling in {"قرعه", "القرعه", "9ar3a", "qar3a", "gar3a", "9er3a"}:
        if LOTTERY_RE.search(nt) or QAR3A_BALD_BAD_RE.search(nt):
            return True
    if spelling == "كاشي" and CAMERA_CACHEE_RE.search(nt):
        return True
    if spelling in {"joint", "joints", "جوان"} and JOINT_CAR_RE.search(nt):
        return True
    if (term == "rouge" or spelling in {"rouge", "روج"}) and ROUGE_FP_RE.search(nt):
        return True
    if spelling in {"كاس", "لكاس", "الكاس"} and KASS_FP_RE.search(nt):
        return True
    if spelling == "خيط" and KHIT_FP_RE.search(nt):
        return True
    if spelling == "السبايس" and SPICE_FP_RE.search(nt):
        return True
    if spelling == "الدومينو" and DOMINO_FP_RE.search(nt):
        return True
    if spelling in {"bira", "hboub", "حبوب", "الحبوب", "كوكا", "coca", "مورفين", "افيون", "ماء الحياه"} and MISC_FP_RE.search(nt):
        return True
    return False


def load_glossary(path):
    """Map every spelling (with attached Arabic prefixes) to (term, ambiguous, spelling); multi-word spellings are kept as tuples."""
    glossary = pd.read_csv(path).fillna("")
    single, phrases = {}, {}
    for row in glossary.itertuples():
        ambiguous = getattr(row, "ambiguous", "") == "yes"
        raw_spellings = [
            row.term,
            getattr(row, "canonical_arabic", ""),
            getattr(row, "canonical_arabizi", ""),
            *[v.strip() for v in re.split(r"[;,]", getattr(row, "variants", "")) if v.strip()],
        ]
        for spelling in raw_spellings:
            if not spelling or spelling == "–":
                continue
            words = tokens(spelling)
            if len(words) == 1:
                word = words[0]
                if word in DROP_SINGLE_VARIANTS or len(word) < 3:
                    continue
                # Ensure G-086 (rabrah) does not overwrite G-079 (الغبرة) as unambiguous.
                sp_ambig = ambiguous or (word in {"غبره", "الغبره"})
                if ARABIC_LETTER.search(word):
                    prefixes = ("", "و", "ب", "ف", "ل") if word.startswith("ال") else ARABIC_PREFIXES
                    for prefix in prefixes:
                        key = prefix + word
                        if key in DROP_PREFIXED_FORMS:
                            continue
                        if key in single:
                            single[key] = (single[key][0], single[key][1] or sp_ambig, single[key][2])
                        else:
                            single[key] = (row.term, sp_ambig, word)
                else:
                    if word in single:
                        single[word] = (single[word][0], single[word][1] or sp_ambig, single[word][2])
                    else:
                        single[word] = (row.term, sp_ambig, word)
            elif words:
                phrases[tuple(words)] = (row.term, ambiguous, " ".join(words))
    return single, phrases


def find_term(text, terms, filter_fp=True):
    single, phrases = terms
    words = tokens(text)
    for phrase, hit in phrases.items():
        size = len(phrase)
        if any(tuple(words[i:i + size]) == phrase for i in range(len(words) - size + 1)):
            if not (filter_fp and is_false_positive(hit[0], hit[2], text)):
                return hit
    if RAW_WEED_RE.search(text):
        return ("حشيش", True, "weed")
    candidates = [
        single[word]
        for word in words
        if word in single and not (filter_fp and is_false_positive(single[word][0], single[word][2], text))
    ]
    if candidates:
        candidates.sort(key=lambda hit: hit[1])
        return candidates[0]
    return None


def write_sheet(frame, name, note=None):
    OUT.mkdir(exist_ok=True)
    frame.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUT / f"{name}.xlsx", engine="openpyxl") as writer:
        start = 2 if note else 0
        frame.to_excel(writer, index=False, sheet_name=name[:31], startrow=start)
        if note:
            writer.sheets[name[:31]].cell(row=1, column=1, value=note)


def build_messages(terms, target, per_term_cap, seed, ambig_cap=3):
    matches = []
    for source_id, script, text in clean_lines(relaxed=True):
        if len(text.split()) < 3:
            continue
        hit = find_term(text, terms, filter_fp=True)
        if hit:
            matches.append((source_id, script, text, hit[0], hit[1], hit[2]))

    tier1, tier2 = [], []
    for row in matches:
        source_id, script, text, term, ambiguous, spelling = row
        nt = normalise(text)
        if (not ambiguous) or (DRUG_CONTEXT_RE.search(nt) and not SHRAB_NORMAL_RE.search(nt)):
            tier1.append(row)
        elif term in TIER2_ALLOWED_TERMS:
            tier2.append(row)

    rng = random.Random(seed)
    rng.shuffle(tier1)
    rng.shuffle(tier2)

    tier1_limit = max(0, target - 42)
    picked, per_term = [], {}
    tier1_kept = 0
    for row in tier1:
        term = row[3]
        if per_term.get(term, 0) < per_term_cap:
            per_term[term] = per_term.get(term, 0) + 1
            picked.append(row)
            tier1_kept += 1
        if len(picked) >= tier1_limit:
            break

    tier2_kept, tier2_per_term = 0, {}
    if len(picked) < target:
        for row in tier2:
            term = row[3]
            if tier2_per_term.get(term, 0) < ambig_cap:
                tier2_per_term[term] = tier2_per_term.get(term, 0) + 1
                picked.append(row)
                tier2_kept += 1
            if len(picked) >= target:
                break

    picked.sort(key=lambda row: (row[0], row[3]))

    rows, counters = [], {}
    for source_id, script, text, _, _, spelling in picked:
        counters[source_id] = counters.get(source_id, 0) + 1
        rows.append({
            "msg_id": f"M-{source_id}-{counters[source_id]:04d}", "source_id": source_id, "text": text,
            "script": script, "drug_term": spelling, "drug_sense": "", "drug": "", "user_type": "", "request": "",
            "danger": "", "collected_by": "Malak", "labelled_by": "",
        })
    frame = pd.DataFrame(rows)
    write_sheet(frame, "messages_real_malak")
    print(
        f"{len(matches)} clean matching lines found, {len(frame)} kept "
        f"(Tier 1 drug/context: {tier1_kept}, Tier 2 diverse normal-meaning: {tier2_kept})"
    )
    print(frame.groupby(["source_id", "script"]).size().to_string())
    print(frame.drug_term.value_counts().to_string())


def build_general(terms, quotas, seed):
    pools = {source_id: [] for source_id in quotas}
    for source_id, script, text in clean_lines(relaxed=False):
        if len(text.split()) >= 4 and not find_term(text, terms, filter_fp=False):
            pools[source_id].append((script, text))
    rng = random.Random(seed)
    rows = []
    for source_id, quota in quotas.items():
        sample = rng.sample(pools[source_id], min(quota, len(pools[source_id])))
        for n, (script, text) in enumerate(sample, 1):
            rows.append({"line_id": f"L-{source_id}-{n:04d}", "source_id": source_id, "script": script, "text": text})
    frame = pd.DataFrame(rows)
    counts = frame.source_id.value_counts().sort_index()
    note = "Lines per source: " + " | ".join(f"{s} = {n}" for s, n in counts.items()) + f" | total = {len(frame)}"
    write_sheet(frame, "darija-general-v1", note)
    print({s: len(p) for s, p in pools.items()}, "eligible lines")
    print(note)
    print(frame.groupby(["source_id", "script"]).size().to_string())


def main():
    default_glossary = Path(__file__).with_name("slang-glossary-v1.csv")
    if not default_glossary.exists():
        default_glossary = Path(__file__).with_name("glossary_starter_malak.csv")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["messages", "general"])
    parser.add_argument("--glossary", type=Path, default=default_glossary)
    parser.add_argument("--target", type=int, default=185, help="messages: rows to keep")
    parser.add_argument("--per-term-cap", dest="per_term_cap", type=int, default=18, help="messages: max rows per glossary term")
    parser.add_argument("--ambig-cap", dest="ambig_cap", type=int, default=3, help="messages: max Tier 2 normal-meaning rows per glossary term")
    parser.add_argument("--seed", type=int, default=15)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    terms = load_glossary(args.glossary)
    if args.mode == "messages":
        build_messages(terms, args.target, args.per_term_cap, args.seed, args.ambig_cap)
    else:
        build_general(terms, {"S30": 1800, "S31": 1500, "S32": 500, "S33": 1200}, args.seed)


if __name__ == "__main__":
    main()
