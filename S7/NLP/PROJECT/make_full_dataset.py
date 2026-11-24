# -*- coding: utf-8 -*-
import csv, subprocess, os, re

# Define the 37 terms and their exact specifications
# Format per term:
# tid: term_id
# term: term
# canon: canonical_spelling
# drug: target drug category
# sentences: list of 5 dicts:
#   {"sentence": str, "script": "arabic"|"arabizi"|"mixed-fr", "sense": "drug"|"not-drug", "drug": drug|"", "origin": msg_id|"invented"}

DATA = [
    # 1. G-002: الكيف / كيف (cannabis)
    {
        "term": "الكيف", "canon": "كيف", "drug": "cannabis",
        "rows": [
            {"term": "الكيف", "sentence": "راه مبلي بتدخين الكيف المعالج وما قدرش يتوقف وحدو.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0033"},
            {"term": "kif", "sentence": "kayen nas ybi3o l'kif f l'houma 3inani w drari tbellaw.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S36-0010"},
            {"term": "kif", "sentence": "il fume du kif chaque soir avec ses amis pour déstresser.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "كيف", "sentence": "قعدنا نهدرو كيف كيف حتى للصباح وما حسيناش بالوقت.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "kif", "sentence": "hada l'film dja 3la kif ta3i w 3jebni bezzaf.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 2. G-003: chira / شيرة (cannabis)
    {
        "term": "chira", "canon": "شيرة", "drug": "cannabis",
        "rows": [
            {"term": "chira", "sentence": "dkhalt f triq chira w drouk habelt l'walidin m3aya.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S38-0006"},
            {"term": "الشيرة", "sentence": "الشيرة هادي دمرت شحال من شاب وضيعتلهم مستقبلهم.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "chira", "sentence": "on a trouvé un morceau de chira dans sa poche.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "شيرة", "sentence": "هاديك الشيرة تقرا معايا في لافاك وناس ملاح بزاف.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "chira", "sentence": "chira ta3 wahren hadik jat tchouf la famille hna.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 3. G-004: garou / قارو (cannabis)
    {
        "term": "قارو", "canon": "قارو", "drug": "cannabis",
        "rows": [
            {"term": "قارو", "sentence": "كل ليلة يشعل قارو كيف ويسهر وحدو في الدار.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0013"},
            {"term": "garou", "sentence": "dhaq garou m3a shabo w men tema wlla yhab dima ykmih.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0014"},
            {"term": "garou", "sentence": "il a roulé un garou de zatla avant de sortir f lil.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "قارو", "sentence": "يا مستر الجائزة نتع العام هذا تروح للقارو نتع الدخان ماشي للمرسيدس.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0015"},
            {"term": "garou", "sentence": "medli garou دخان khlasli l'paquet w hanout b3id.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 4. G-005: jwan / جوان (cannabis)
    {
        "term": "جوان", "canon": "جوان", "drug": "cannabis",
        "rows": [
            {"term": "جوان", "sentence": "حكموه البوليس وفي جيبو نص جوان حشيش مخبي.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "invented"},
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
            {"term": "بلاكيطة", "sentence": "حجزت مصالح الأمن بلاكيطة مخدرات كانت مخبية في الطوموبيل.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "invented"},
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
            {"term": "حشيش", "sentence": "كان يتعاطى الحشيش بزاف حتى ولا عندو وسواس وخوف.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0036"},
            {"term": "7achich", "sentence": "l'7achich hada wlla yji mkhallat w ydir la folie.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0037"},
            {"term": "hachich", "sentence": "il a arrêté de fumer le hachich depuis deux mois.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "حشيش", "sentence": "روحي للسوق واشري حشيش ومعدنوس للشوربة تاع العشية.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "7achich", "sentence": "l'djenina rahi m3amra b l'7achich l'khdar lazmou tqta3.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 8. G-009: صفيحة / صفيحة (cannabis)
    {
        "term": "صفيحة", "canon": "صفيحة", "drug": "cannabis",
        "rows": [
            {"term": "صفيحة", "sentence": "تم توقيف شبكة ومعاهم صفيحة كيف معالج مجهزة للبيع.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S30-0045"},
            {"term": "safi7a", "sentence": "lqaw 3ando safi7a ta3 zatla f l'coffre ta3 l'kousha.", "script": "arabizi", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "safiha", "sentence": "trafic d'une safiha de drogue dans la région.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "صفيحة", "sentence": "حطت الخبز فوق صفيحة حديد ودخلاتو للكوشة يطيب.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "safi7a", "sentence": "rkebna safi7a jdida ta3 l'aluminium f l'khedma.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 9. G-011: الكمية / كمية (cannabis)
    {
        "term": "كمية", "canon": "كمية", "drug": "cannabis",
        "rows": [
            {"term": "كمية", "sentence": "حكموه ومعاه كمية معتبرة من الكيف المعالج مجهزة للترويج.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "M-S25-0004"},
            {"term": "kmiya", "sentence": "chra kmiya kbira ta3 l'ghabra w wlla ykhellat f l'houma.", "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "quantité", "sentence": "la brigade a trouvé une grande quantité de drogue.", "script": "mixed-fr", "sense": "drug", "drug": "cannabis", "origin": "invented"},
            {"term": "كمية", "sentence": "زيد كمية صغيرة تاع سكر في القهوة باش تنقص المرارة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "kmiya", "sentence": "l'kmiya ta3 l'farina ma tekfich باش نديرو الخبز كامل.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 10. G-012: spice / سبايس (cannabis)
    {
        "term": "سبايس", "canon": "سبايس", "drug": "cannabis",
        "rows": [
            {"term": "سبايس", "sentence": "هاد المخدر الجديد سبايس راه يطير العقل ويدير الهلوسة.", "script": "arabic", "sense": "drug", "drug": "cannabis", "origin": "invented"},
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
            {"term": "صاروخ", "sentence": "تلقى شباب صغار يبلعو الصاروخ والحمراء ويطيحو في الغيبوبة.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S28-0004"},
            {"term": "صاروخ", "sentence": "الصاروخ هبل الشباب في الحومة وما بقاوش يعقلو حتى والديهم.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0001"},
            {"term": "saroukh", "sentence": "rah yakhod saroukh 300 mg w dima 3inih 7omr.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0044"},
            {"term": "صاروخ", "sentence": "أطلقت وكالة الفضاء صاروخ جديد حامل للأقمار الصناعية.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "saroukh", "sentence": "l'joueur dharba b saroukh f filet marqua but chbab.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 12. G-015: الحمراء / حمرة (pills)
    {
        "term": "الحمراء", "canon": "حمرة", "drug": "pills",
        "rows": [
            {"term": "الحمراء", "sentence": "يشربو كاشيات الحمراء تاع البوليز مع الما ويديرو المشاكل.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0011"},
            {"term": "7amra", "sentence": "sahbi klé 7amra w rani khayef 3lih psk ma rahoch f wa3yo.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "hamra", "sentence": "il mélange la hamra avec l'alcool chaque weekend.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "حمراء", "sentence": "لبست فستان لونو وردة حمراء في العرس تاع بنت خالتها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "7amra", "sentence": "chrit tomobil 7amra jdida men la maison.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 13. G-016: zar9a / زرقة (pills)
    {
        "term": "زرقة", "canon": "زرقة", "drug": "pills",
        "rows": [
            {"term": "الزرقة", "sentence": "الكاشية الزرقة هاديك ترقد وتخلي بنادم مريض في راسو.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
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
            {"term": "التاكسي", "sentence": "حكمو كمية تاع التاكسي 300 عند مروج كان يبيع للشباب.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0028"},
            {"term": "taxi", "sentence": "dreb haba taxi w wlla dayekh ma yqderch ymchi f triq.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0026"},
            {"term": "taxi", "sentence": "la brigade a arrêté un dealer de taxi près du stade.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "تاكسي", "sentence": "خرجت للشارع وحكمت تاكسي باش نلحق للخدمة بكري.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0027"},
            {"term": "taxi", "sentence": "win nelqa taxi bach nrouh l l'aéroport drouk?", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 15. G-018: 7alwa / حلوة (pills)
    {
        "term": "الحلوى", "canon": "حلوة", "drug": "pills",
        "rows": [
            {"term": "الحلوى", "sentence": "على حساب واش فهمت الحلوى هي المخدرات لي راهم يخرجوها في السري.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0001"},
            {"term": "7alwa", "sentence": "sahbi klé 7alwa f la fête w wlla yhelwes w ma 3refnach.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S35-0017"},
            {"term": "halwa", "sentence": "les jeunes appellent cette pilule halwa dans le quartier.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "حلوة", "sentence": "يا زنقا ريحو هكدا غير ولاد الحومة والله حلوة وتضحك من قلبك ربي يوفقكم.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0002"},
            {"term": "7alwa", "sentence": "mama taybet 7alwa bnina ta3 l'3id w darna l'qahwa.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 16. G-020: la roche / لاروش (pills)
    {
        "term": "لاروش", "canon": "لاروش", "drug": "pills",
        "rows": [
            {"term": "لاروش", "sentence": "راه مدمن على كاشيات لاروش تاع المهدئات وبلا بيهم ما يرقدش.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "la roche", "sentence": "khda haba la roche w wlla ghayeb 3la denya.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0018"},
            {"term": "la roche", "sentence": "il consomme des comprimés de la roche sans ordonnance.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "لاروش", "sentence": "شريت بومادا شابة تاع لاروش بوزاي من لافارماسي للوجه.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "la roche", "sentence": "q3adna fouq la roche f l'bhar nchoufo l'mouj.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 17. G-026: cachiyates / كاشيات (pills)
    {
        "term": "كاشيات", "canon": "كاشيات", "drug": "pills",
        "rows": [
            {"term": "كاشيات", "sentence": "ونتوما عطيتونا غير الكاشيات و تعمار الراس بالسموم.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0011"},
            {"term": "كاشيات", "sentence": "حكموه يبيع الكاشيات المهلوسة قدام باب ليسي.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0010"},
            {"term": "cachiyates", "sentence": "rah yebla3 cachiyates ta3 l'a3ssab bla ma ychouf tbib.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0012"},
            {"term": "كاشيات", "sentence": "طبيب العائلة عطاني كاشيات دوليبران على وجع الراس والسطر.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "cachiyates", "sentence": "lazem nchreb cachiyates ta3 l'vitamine C kol sba7.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 18. G-027: قفالي / قفالي (pills)
    {
        "term": "قفالي", "canon": "قفالي", "drug": "pills",
        "rows": [
            {"term": "قفالي", "sentence": "لقاو عندو ساشي معمرة بحبوب القفالي تاع المهلوسات.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "qfali", "sentence": "chrab habat qfali m3a l'bira w dkhlo f غيبوبة.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "qfali", "sentence": "il a pris deux qfali pour oublier ses problèmes.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "قفالي", "sentence": "طاحولي زوج قفالي من الفيستة ولازم نديها للخياط يركبهم.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "qfali", "sentence": "qfali ta3 l'qamija tqet3o w drouk ma nqderch nelbessha.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 19. G-028: الحبوب / حبوب (pills)
    {
        "term": "الحبوب", "canon": "حبوب", "drug": "pills",
        "rows": [
            {"term": "الحبوب", "sentence": "الحبوب المهلوسة راهم ينشرو فيها بين القصر في الأحياء.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0029"},
            {"term": "الحبوب", "sentence": "حجز أكثر من عشرة آلاف قرص من الحبوب المهلوسة في العملية.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0030"},
            {"term": "hboub", "sentence": "wlla madloum f dar psk dima yebla3 hboub m3a shabo.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S30-0031"},
            {"term": "حبوب", "sentence": "الفلاح زرع حبوب القمح والشعير في الأرض بعد ما صبت النو.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "hboub", "sentence": "kharjouli hboub sghar f wejhi men l'chmisa lazm كريم.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 20. G-029: اللومبات / لومبات (pills)
    {
        "term": "اللومبات", "canon": "لومبات", "drug": "pills",
        "rows": [
            {"term": "اللومبات", "sentence": "كاشيات اللومبات يديرو خفة العقل ويفقدو بنادم الوعي.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0034"},
            {"term": "loumbat", "sentence": "sahbi klé haba loumbat w tgham f l'bit ma qderch ynod.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "loumbat", "sentence": "il vend des comprimés loumbat aux jeunes du quartier.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "لومبات", "sentence": "شريت زوج لومبات ليد بيوضة باش نركبهم في الكوزينة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "loumbat", "sentence": "tfeina ga3 les loumbat ta3 l'couloir 9bal ma norqdo.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 21. G-034: المرقازة / مرقازة (pills)
    {
        "term": "المرقازة", "canon": "مرقازة", "drug": "pills",
        "rows": [
            {"term": "المرقازة", "sentence": "حكموه ومعاه قداش من حبة المرقازة الحمراء كان ناوي يبيعهم.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
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
            {"term": "الكريستالة", "sentence": "المهلوسات هادوك تاع الكريستالة راهي تخرب خلايا المخ بسرعة.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
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
            {"term": "دوبل سينياتور", "sentence": "يحوسو على أوردونونس دوبل سينياتور باش يخرجو بيها الدوا من لافارماسي.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
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
            {"term": "المارطو", "sentence": "المارطو لي شربو خلاه دايخ وما قدرش ينوض من الفراش.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S30-0035"},
            {"term": "marto", "sentence": "bl3at habat marto w bdaw ybano 3liha a3rad l'intikasa.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S35-0012"},
            {"term": "marteau", "sentence": "cette pilule frappe comme un marteau sur la tête.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "مارطو", "sentence": "جيبلي المارطو والمسامر باش نخدم هاد الطابلة لي تكسرت.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "marto", "sentence": "lazem marto shih باش نهرسو بيه هاد البيدون القديم.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 25. G-038: الناموسة / ناموسة (pills)
    {
        "term": "الناموسة", "canon": "ناموسة", "drug": "pills",
        "rows": [
            {"term": "الناموسة", "sentence": "حبة الناموسة هاديك تتباع بالسرقة بين الشباب في الكوانات.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S35-0013"},
            {"term": "namousa", "sentence": "chrab namousa w raho yched f rasso men l'7riq.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S35-0002"},
            {"term": "namousa", "sentence": "le dealer avait plusieurs comprimés de namousa sur lui.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "ناموسة", "sentence": "قرصتني ناموسة البارح في يدي وحكمتني حكة كبيرة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "namousa", "sentence": "ch3el l'appareil ta3 l'namousa f lil ma khallatnach norgdo.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 26. G-039: الدومينو / دومينو (pills)
    {
        "term": "الدومينو", "canon": "دومينو", "drug": "pills",
        "rows": [
            {"term": "الدومينو", "sentence": "كان يتعاطى أقراص الدومينو حتى فقد السيطرة على تصرفاتو.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "invented"},
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
            {"term": "روج", "sentence": "الروج والكاشيات هادو هما لي راهم مخرجين الشباب على عقلهم.", "script": "arabic", "sense": "drug", "drug": "pills", "origin": "M-S25-0002"},
            {"term": "rouge", "sentence": "rah ykhlat rouge m3a l'alcool kol weekend w halto صعيبة.", "script": "arabizi", "sense": "drug", "drug": "pills", "origin": "M-S25-0003"},
            {"term": "rouge", "sentence": "il a pris une pilule rouge avec son verre de vin.", "script": "mixed-fr", "sense": "drug", "drug": "pills", "origin": "invented"},
            {"term": "روج", "sentence": "شرات روج شافي وماكياج جديد من لافوار للعرس.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "rouge", "sentence": "daret veste rouge chaba li lbestha f la soutenance.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 28. G-046: 9ar3a / قرعة (pills / alcohol)
    {
        "term": "قرعة", "canon": "قرعة", "drug": "alcohol",
        "rows": [
            {"term": "قرعة", "sentence": "سنة يخدم بقرعة بيرة فلاريسبسيون كي تلحق العشية.", "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0007"},
            {"term": "قرعة", "sentence": "طاحو على قرعة شراب وشربوها كاملة حتى سكروا.", "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0005"},
            {"term": "9ar3a", "sentence": "chra 9ar3a ta3 whisky m3a shabo w rahom ysekro barra.", "script": "arabizi", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0006"},
            {"term": "قرعة", "sentence": "عطيني قرعة ما باردة راني عطشان بزاف من السخانة.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "9ar3a", "sentence": "chrina 9ar3a kawkaw w chrab gazouz f l'ghaba.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 29. G-047: شراب / شراب (alcohol)
    {
        "term": "شراب", "canon": "شراب", "drug": "alcohol",
        "rows": [
            {"term": "شراب", "sentence": "شراب الويسكي لي ضحكاته هاد لقطة يدير جام ويكف عن البلية.", "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0019"},
            {"term": "شراب", "sentence": "الشراب هذا راه مرض في الكبدة ويخرب ديار العائلات.", "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0038"},
            {"term": "chrab", "sentence": "rah ybghi yhabes chrab w ma qderch wahdo khasou tbib.", "script": "arabizi", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0041"},
            {"term": "شراب", "sentence": "عطاني الطبيب شراب تاع السعلة نشرب منو مغرف في الليل.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "chrab", "sentence": "dirli chrab ta3 jus citron bared m3a l'ghda.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 30. G-049: l'alcool / لالكول (alcohol)
    {
        "term": "لالكول", "canon": "لالكول", "drug": "alcohol",
        "rows": [
            {"term": "لالكول", "sentence": "يا دقيوس مقيوس تاع زمر اعلاش تلعبو زعمى خمر و لالكول عيب عليكم.", "script": "arabic", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0016"},
            {"term": "l'alcool", "sentence": "bghit nhabes l'alcool win nlqa centre d'aide f wahren?", "script": "arabizi", "sense": "drug", "drug": "alcohol", "origin": "M-S30-0040"},
            {"term": "l'alcool", "sentence": "il mélange les psychotropes et l'alcool ce qui est très toxique.", "script": "mixed-fr", "sense": "drug", "drug": "alcohol", "origin": "invented"},
            {"term": "لالكول", "sentence": "نقي الجرح بشوية قطن و لالكول طبي باش ما يتعفنش.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "l'alcool", "sentence": "chrit l'alcool 70 degrés men l'pharmacie باش نعقم بيه الدوزان.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 31. G-052: الغبرة / غبرة (cocaine)
    {
        "term": "الغبرة", "canon": "غبرة", "drug": "cocaine",
        "rows": [
            {"term": "الغبرة", "sentence": "الغبرة البيضاء هاديك راهي سم قاتل يخرب القلب والعروق.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0032"},
            {"term": "ghabra", "sentence": "dreb ghabra f la fête w wlla qelbo yakhbet bzaf.", "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "M-S33-0067"},
            {"term": "ghabra", "sentence": "la police a intercepté un trafic de ghabra dans la capitale.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "M-S33-0068"},
            {"term": "غبرة", "sentence": "الريح والجاج عَمرو الدار كاملة بالغبرة ولازم نسيقوها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "ghabra", "sentence": "khelat l'ghabra ta3 l'hlib m3a l'ma dافي باش يشرب الصغير.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 32. G-053: beida / بيضاء (cocaine)
    {
        "term": "بيضاء", "canon": "بيضاء", "drug": "cocaine",
        "rows": [
            {"term": "البيضاء", "sentence": "السموم البيضاء هادي راهي تهلك في ولادنا ولازم وقفة حقيقية.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S37-0005"},
            {"term": "beida", "sentence": "chra gramme beida m3a sahbo w dakhlo f l'addiction.", "script": "arabizi", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "blanche", "sentence": "il consomme de la blanche et il ne mange plus rien.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "invented"},
            {"term": "بيضاء", "sentence": "كليت حبة بيضاء مغلية مع الصباح قبل ما نروح نقرا.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "beida", "sentence": "lbest qamija beida nqiya l'salat l'djoumou3a.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 33. G-054: coke / كوك (cocaine)
    {
        "term": "كوك", "canon": "كوك", "drug": "cocaine",
        "rows": [
            {"term": "كوكايين", "sentence": "الكوكايين هادي راهي تدخل بطرق غير شرعية وتدمر الشباب.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S34-0008"},
            {"term": "كوكاين", "sentence": "شحال من واحد تلف حياتو بسبايب الكوكاين والفلوس الحرام.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0048"},
            {"term": "coke", "sentence": "il a sniffé de la coke dans les toilettes de la boîte.", "script": "mixed-fr", "sense": "drug", "drug": "cocaine", "origin": "M-S30-0047"},
            {"term": "كوكا", "sentence": "اشريلي قرعة كوكا كولا باردة نشربوها مع البيتزا في الليل.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "coke", "sentence": "jib m3ak canette coke zero men l'hanout stp.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 34. G-055: crack / كراك (cocaine)
    {
        "term": "كراك", "canon": "كراك", "drug": "cocaine",
        "rows": [
            {"term": "كراك", "sentence": "الكراك مخدر خطير بزاف يخلي الواحد يدمن من أول استعمال.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "invented"},
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
            {"term": "خيط", "sentence": "لقاو عندو خيط غبرة كوكايين مسربي فوق الطابلة.", "script": "arabic", "sense": "drug", "drug": "cocaine", "origin": "invented"},
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
            {"term": "حقنة", "sentence": "نتا راك متأثر بفيديوهاتو و ماتعرفش النفاق لي يدير فيه حقنة هيروين تهرد صحتك.", "script": "arabic", "sense": "drug", "drug": "heroin", "origin": "M-S30-0003"},
            {"term": "7oqna", "sentence": "yesta3mlou nafs l'7oqna ta3 l'heroin binathoum w hada khatar kbir.", "script": "arabizi", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "seringue", "sentence": "partager une seringue pour injecter la drogue transmet les virus.", "script": "mixed-fr", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "حقنة", "sentence": "حيياك يا خويا فعلا شخصية إيجابية بإمتياز حقنة تحفيز جيدة لجميع الشباب.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "M-S30-0004"},
            {"term": "7oqna", "sentence": "darouli 7oqna ta3 l'vaccin f sbitar w ma wj3atnich bezzaf.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
    # 37. G-064: héroïne / هيروين (heroin)
    {
        "term": "هيروين", "canon": "هيروين", "drug": "heroin",
        "rows": [
            {"term": "هيروين", "sentence": "الهيروين أخطر سم يدخل للجسم وأعراض الانسحاب تاعو صعيبة بزاف.", "script": "arabic", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "heroine", "sentence": "sahbi wlla y7qan l'heroine w drouk rah f sbitar mrid.", "script": "arabizi", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "héroïne", "sentence": "la surdose d'héroïne peut provoquer un arrêt respiratoire immédiat.", "script": "mixed-fr", "sense": "drug", "drug": "heroin", "origin": "invented"},
            {"term": "هيروين", "sentence": "البطلة في الرواية هاديك كانت هيروين حقيقية أنقذت شعبها.", "script": "arabic", "sense": "not-drug", "drug": "", "origin": "invented"},
            {"term": "héroïne", "sentence": "l'actrice l3bat rôle ta3 héroïne f l'film l'djedid li khrej.", "script": "arabizi", "sense": "not-drug", "drug": "", "origin": "invented"},
        ]
    },
]

print(f"Defined {len(DATA)} terms, each with 5 rows. Total rows = {len(DATA) * 5}.")
