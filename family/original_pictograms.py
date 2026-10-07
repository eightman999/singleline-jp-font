"""64 original single-line pictograms, inspired by small monochrome displays.

This project-authored set is NOT a copy of any mobile carrier's glyph designs,
NOT an implementation of DoCoMo emoji, and NOT compatible with any carrier's
private-use mapping. PUA U+E000..U+E03F is a NEW project mapping. Standard Unicode
aliases are provided only where the pictured object has the same meaning.
Geometry was authored here, without external font/bitmap/outline references.
All contours, including faces and small details, remain stroked outlines.
"""
from copy import deepcopy

SOURCE = {
    'kind': 'original project-authored geometric pictograms',
    'file': 'family/original_pictograms.py',
    'external_glyph_inputs': [],
    'design': 'Original retro mobile-inspired single-line pictograms on a 24-unit em',
    'private_use_mapping': 'New project mapping U+E000–U+E03F; no carrier compatibility',
    'license': 'AGPL-3.0-only; see repository LICENSE and NOTICE.md',
}
FILLED = set()
PUA_GLYPHS = {}
ALIASES = {}  # Standard Unicode character -> project PUA character.
PICTOGRAM_NAMES = {}
PICTOGRAM_LABELS_JA = {}
NAME_TO_PUA = {}


def s(*points):
    return [[tuple(map(float,p)) for p in points]]


def dot(x,y):
    return s((x-.35,y),(x+.35,y))


def box(left,top,right,bottom,corner=0):
    c = corner
    if not c:
        return s((left,top),(right,top),(right,bottom),(left,bottom),(left,top))
    return s((left+c,top),(right-c,top),(right,top+c),(right,bottom-c),
             (right-c,bottom),(left+c,bottom),(left,bottom-c),(left,top+c),(left+c,top))


def circle(x,y,r,ry=None):
    ry = r if ry is None else ry
    q=.7
    return s((x-r*q,y-ry),(x+r*q,y-ry),(x+r,y-ry*q),(x+r,y+ry*q),
             (x+r*q,y+ry),(x-r*q,y+ry),(x-r,y+ry*q),(x-r,y-ry*q),(x-r*q,y-ry))


def moved(paths,dx=0,dy=0,sx=1,sy=1):
    return [[(x*sx+dx,y*sy+dy) for x,y in p] for p in paths]


def define(index,name,japanese,paths,*aliases):
    char=chr(0xE000+index)
    if not 0<=index<64 or char in PUA_GLYPHS or name in NAME_TO_PUA:
        raise ValueError(f'duplicate or invalid pictogram {name}')
    PUA_GLYPHS[char]=deepcopy(paths)
    PICTOGRAM_NAMES[char]=name
    PICTOGRAM_LABELS_JA[char]=japanese
    NAME_TO_PUA[name]=char
    for alias in aliases:
        if alias in ALIASES or len(alias)!=1:
            raise ValueError(f'duplicate or non-scalar alias {alias!r}')
        ALIASES[alias]=char
        PICTOGRAM_NAMES[alias]=name
        PICTOGRAM_LABELS_JA[alias]=japanese


# WEATHER: broad silhouettes with limited interior detail stay legible at 18 px.
SUN = circle(12,12,5)+s((12,1),(12,4))+s((12,20),(12,23))+s((1,12),(4,12))+s((20,12),(23,12))+s((4,4),(6,6))+s((18,18),(20,20))+s((4,20),(6,18))+s((18,6),(20,4))
CLOUD = s((6,18),(3,17),(1,14),(2,11),(5,9),(7,9),(9,5),(13,4),(17,6),(18,10),(21,10),(23,13),(22,17),(19,18),(6,18))
define(0,'sun','晴れ・太陽',SUN,'☀')
define(1,'cloud','雲',CLOUD,'☁')
define(2,'rain-cloud','雨',moved(CLOUD,dy=-2,sy=.85)+s((6,17),(4,21))+s((12,17),(10,23))+s((18,17),(16,21)),'🌧')
define(3,'snowflake','雪',s((12,2),(12,22))+s((3,7),(21,17))+s((3,17),(21,7))+s((8,3),(12,7),(16,3))+s((8,21),(12,17),(16,21))+s((3,11),(7,10),(6,6))+s((18,18),(17,14),(21,13))+s((3,13),(7,14),(6,18))+s((18,6),(17,10),(21,11)),'❄')
define(4,'lightning','雷',s((14,1),(4,14),(11,14),(8,23),(21,9),(14,9),(14,1)),'⚡')
define(5,'umbrella','傘',s((2,12),(4,7),(8,3),(12,2),(16,3),(20,7),(22,12),(17,10),(12,12),(7,10),(2,12))+s((12,12),(12,20),(14,22),(17,22),(19,20))+s((12,0),(12,2)),'☂')
define(6,'crescent-moon','月',s((16,2),(9,3),(4,8),(3,14),(6,20),(12,23),(19,21),(22,16),(16,18),(10,15),(8,10),(10,5),(16,2)),'🌙')
define(7,'star','星',s((12,1),(15,8),(23,9),(17,14),(19,22),(12,18),(5,22),(7,14),(1,9),(9,8),(12,1)),'⭐')

# COMMUNICATION AND FEELINGS.
define(8,'telephone-receiver','受話器',s((5,2),(2,5),(3,10),(7,16),(13,21),(18,22),(22,19),(17,14),(14,17),(10,14),(7,10),(10,7),(5,2)),'📞')
define(9,'mobile-phone','携帯電話',box(6,2,18,22,2)+box(8,5,16,15)+s((10,18),(14,18))+dot(12,20),'📱')
define(10,'envelope','メール',box(2,5,22,20,1)+s((3,6),(12,13),(21,6))+s((3,19),(8,13))+s((21,19),(16,13)),'✉')
define(11,'camera','カメラ',s((2,8),(7,8),(9,4),(16,4),(18,8),(22,8),(22,21),(2,21),(2,8))+circle(13,14,5)+s((3,5),(6,5),(6,8))+dot(20,11),'📷')
define(12,'heart','ハート',s((12,22),(3,13),(1,8),(3,4),(7,3),(12,7),(17,3),(21,4),(23,8),(21,13),(12,22)),'♡','❤')
FACE = circle(12,12,10)
EYES = dot(8,9)+dot(16,9)
define(13,'smiling-face','笑顔',FACE+EYES+s((6,14),(9,18),(15,18),(18,14)),'☺')
define(14,'sad-face','悲しい顔',FACE+EYES+s((6,18),(9,14),(15,14),(18,18)),'☹')
define(15,'winking-face','ウインク',FACE+dot(8,9)+s((14,10),(16,8),(18,10))+s((6,14),(9,18),(15,18),(18,14)),'😉')

# TRANSPORT: train is front-on; bus and car are intentionally distinct profiles.
define(16,'train','電車',box(4,2,20,19,3)+box(7,5,17,11)+dot(8,15)+dot(16,15)+s((7,19),(3,23))+s((17,19),(21,23))+s((6,21),(18,21)),'🚆')
define(17,'bus','バス',s((2,17),(2,5),(5,3),(20,3),(22,6),(22,17),(20,17))+s((16,17),(8,17))+s((4,17),(2,17))+box(4,6,9,11)+box(12,6,17,11)+s((20,6),(22,6))+circle(6,18,2)+circle(18,18,2)+s((2,14),(22,14)),'🚌')
define(18,'car','自動車',s((2,17),(2,12),(6,10),(9,5),(16,5),(20,11),(23,13),(23,17),(21,17))+s((17,17),(8,17))+s((4,17),(2,17))+s((6,10),(20,11))+s((12,5),(12,10))+circle(6,18,2)+circle(19,18,2),'🚗')
define(19,'bicycle','自転車',circle(5,17,4)+circle(19,17,4)+s((5,17),(10,8),(15,17),(5,17),(12,12),(18,12),(19,17))+s((8,7),(12,7))+s((16,4),(19,4),(18,12))+s((15,17),(17,19)),'🚲')
define(20,'airplane','飛行機',s((12,1),(14,3),(14,9),(23,14),(23,17),(14,14),(14,20),(18,22),(18,24),(12,22),(6,24),(6,22),(10,20),(10,14),(1,17),(1,14),(10,9),(10,3),(12,1)),'✈')
define(21,'ship','船',s((2,14),(22,14),(19,20),(6,20),(2,14))+s((6,14),(6,9),(18,9),(18,14))+box(10,4,14,9)+s((3,23),(6,21),(10,23),(14,21),(18,23),(22,21))+s((15,4),(18,2),(21,3)),'🚢')

# PLACES: each building has a unique identifying sign rather than a generic box.
BUILDING = box(4,8,20,22)
define(22,'house','家',s((1,11),(12,2),(23,11))+s((4,9),(4,22),(20,22),(20,9))+box(10,15,15,22)+box(6,12,8,15)+s((17,6),(17,2),(20,2),(20,8)),'🏠')
define(23,'hospital','病院',BUILDING+box(8,1,16,9)+s((12,3),(12,7))+s((10,5),(14,5))+box(10,16,14,22)+s((7,12),(7,14))+s((17,12),(17,14)),'🏥')
define(24,'bank','銀行',s((2,7),(12,1),(22,7),(2,7))+s((3,10),(21,10))+s((5,10),(5,19))+s((12,10),(12,19))+s((19,10),(19,19))+s((3,19),(21,19))+box(1,21,23,23),'🏦')
define(25,'japanese-post-office','郵便局',BUILDING+box(8,1,16,9)+s((10,3),(14,3))+s((10,5),(14,5))+s((12,5),(12,7))+box(10,17,14,22)+box(6,12,9,15)+box(15,12,18,15),'🏣')
define(26,'school','学校',s((2,22),(2,10),(8,10),(8,6),(12,2),(16,6),(16,10),(22,10),(22,22),(2,22))+circle(12,8,2)+s((12,6),(12,8),(13,8))+box(10,17,14,22)+s((5,13),(5,17))+s((19,13),(19,17))+s((12,0),(12,2)),'🏫')

# TIME, FOOD, CULTURE.
CLOCK_FACE = circle(12,12,9)+s((12,12),(12,5))+s((12,12),(6,12))
define(27,'nine-oclock','9時',CLOCK_FACE,'🕘')
define(28,'alarm-clock','目覚まし時計',moved(CLOCK_FACE,dy=2,sy=.85)+s((3,9),(1,6),(4,2),(8,3))+s((16,3),(20,2),(23,6),(21,9))+s((7,21),(5,24))+s((17,21),(19,24))+s((10,1),(14,1)),'⏰')
define(29,'hot-drink','温かい飲み物',s((3,10),(17,10),(17,18),(14,21),(7,21),(3,18),(3,10))+s((17,11),(21,11),(23,14),(21,17),(17,17))+s((2,23),(21,23))+s((7,7),(5,5),(7,2))+s((13,7),(11,5),(13,2)),'☕')
define(30,'fork-and-knife','食事',s((3,2),(3,8),(6,11),(9,8),(9,2))+s((6,2),(6,23))+s((19,23),(19,2),(16,6),(15,13),(19,13)),'🍴')
define(31,'music-note','音符',circle(7,19,4,3)+s((11,19),(11,2),(20,6),(19,10),(11,6)),'♪')
define(32,'music-notes','連桁付き音符',circle(5,20,3,2)+circle(18,17,3,2)+s((8,20),(8,5),(21,2),(21,17))+s((8,9),(21,6)),'♫')
define(33,'bell','ベル',s((3,19),(6,15),(6,9),(9,5),(15,5),(18,9),(18,15),(21,19),(3,19))+circle(12,3,2)+s((9,21),(10,23),(14,23),(15,21)),'🔔')
define(34,'open-book','本',s((12,5),(7,2),(1,2),(1,19),(7,19),(12,22),(17,19),(23,19),(23,2),(17,2),(12,5),(12,22))+s((4,7),(8,7))+s((4,11),(8,11))+s((16,7),(20,7))+s((16,11),(20,11)),'📖')
define(35,'pencil','鉛筆',s((2,22),(4,14),(17,1),(23,7),(10,20),(2,22))+s((4,14),(10,20))+s((14,4),(20,10))+s((7,17),(17,7)),'✎')
define(36,'magnifying-glass','虫眼鏡',circle(9,9,7)+s((14,14),(23,23))+s((16,14),(24,22)),'🔍')
define(37,'key','鍵',circle(7,7,5)+circle(7,7,1.5)+s((11,11),(21,21),(23,19),(21,17),(23,15),(20,12),(18,14),(14,10)),'🔑')
define(38,'locked','施錠',box(4,11,20,23,1)+s((7,11),(7,6),(9,2),(15,2),(17,6),(17,11))+circle(12,16,2)+s((12,18),(12,20)),'🔒')
define(39,'unlocked','解錠',box(4,11,20,23,1)+s((7,11),(7,6),(9,2),(15,2),(17,6))+circle(12,16,2)+s((12,18),(12,20)),'🔓')
define(40,'scissors','はさみ',circle(5,19,3)+circle(19,19,3)+s((7,16),(21,2))+s((17,16),(3,2))+dot(12,11),'✂')
define(41,'gift','プレゼント',box(3,11,21,23)+box(1,7,23,11)+s((12,7),(12,23))+s((12,7),(6,7),(3,4),(4,1),(8,1),(12,7),(16,1),(20,1),(21,4),(18,7),(12,7)),'🎁')
define(42,'shopping-cart','買い物',s((1,3),(4,3),(7,17),(20,17))+s((5,6),(23,6),(20,13),(6,13))+circle(8,21,2)+circle(19,21,2)+s((11,6),(12,13))+s((17,6),(17,13)),'🛒')
define(43,'flag','旗',s((5,23),(5,1))+s((5,2),(10,2),(14,5),(21,5),(21,15),(14,15),(10,12),(5,12)),'⚐')
define(44,'check-mark','チェック',s((2,12),(8,20),(22,3)),'✓')
define(45,'warning','注意',s((12,1),(23,22),(1,22),(12,1))+s((12,8),(12,15))+dot(12,19),'⚠')
define(46,'information','案内',circle(12,12,10)+dot(12,6)+s((9,10),(12,10),(12,18))+s((8,18),(16,18)))

# DEVICES.
define(47,'battery','電池',box(7,4,17,23,1)+box(10,1,14,4)+s((10,9),(14,9))+s((12,7),(12,11))+s((10,18),(14,18)),'🔋')
define(48,'electric-plug','電源プラグ',s((6,8),(18,8),(18,13),(15,17),(9,17),(6,13),(6,8))+s((8,8),(8,2))+s((16,8),(16,2))+s((12,17),(12,21),(15,23),(20,23)),'🔌')
define(49,'wireless-signal','無線通信',s((1,8),(6,4),(12,2),(18,4),(23,8))+s((5,12),(8,9),(12,8),(16,9),(19,12))+s((9,16),(12,14),(15,16))+dot(12,20))
define(50,'satellite-antenna','衛星アンテナ',s((3,7),(8,7),(14,11),(17,17),(17,22),(11,22),(5,17),(3,11),(3,7))+s((6,10),(14,18))+s((10,14),(19,5))+circle(20,4,1.5)+s((17,1),(22,1),(23,6))+s((14,3),(17,3))+s((20,9),(20,12)),'📡')
define(51,'laptop-computer','ノートパソコン',box(4,2,20,16,1)+box(6,4,18,13)+s((4,16),(1,22),(23,22),(20,16))+s((9,19),(15,19)),'💻')
define(52,'printer','プリンター',box(6,1,18,8)+box(2,8,22,18,2)+box(6,14,18,23)+s((9,17),(15,17))+s((9,20),(15,20))+dot(19,11),'🖨')
define(53,'television','テレビ',box(2,7,22,22,2)+box(4,9,17,19,1)+dot(20,11)+dot(20,16)+s((12,7),(7,1))+s((12,7),(17,2)),'📺')
define(54,'game-controller','ゲームパッド',s((5,7),(19,7),(22,11),(23,19),(20,21),(16,17),(8,17),(4,21),(1,19),(2,11),(5,7))+s((7,10),(7,16))+s((4,13),(10,13))+dot(17,11)+dot(20,14)+s((11,9),(13,9)),'🎮')

# SPORTS AND NATURE.
define(55,'soccer-ball','サッカーボール',circle(12,12,10)+s((12,7),(17,11),(15,17),(9,17),(7,11),(12,7))+s((12,7),(12,2))+s((17,11),(22,10))+s((15,17),(18,21))+s((9,17),(6,21))+s((7,11),(2,10)),'⚽')
define(56,'baseball','野球',circle(12,12,10)+s((5,4),(8,8),(9,12),(8,16),(5,20))+s((19,4),(16,8),(15,12),(16,16),(19,20))+s((5,7),(9,7))+s((7,12),(11,12))+s((5,17),(9,17))+s((15,7),(19,7))+s((13,12),(17,12))+s((15,17),(19,17)),'⚾')
define(57,'tennis','テニス',circle(9,8,6,7)+s((6,14),(9,18),(14,23),(17,20),(12,15))+s((6,4),(6,12))+s((10,2),(10,14))+s((3,6),(15,6))+s((3,10),(15,10))+circle(21,13,2),'🎾')
define(58,'leaf','葉',s((3,22),(5,16),(4,11),(8,5),(15,2),(22,2),(22,9),(18,16),(12,20),(7,19),(3,22))+s((5,20),(18,7))+s((9,15),(9,9))+s((13,11),(18,11)))
define(59,'flower','花',s((12,7),(8,3),(4,5),(3,9),(7,12),(3,15),(4,19),(8,21),(12,17),(16,21),(20,19),(21,15),(17,12),(21,9),(20,5),(16,3),(12,7))+circle(12,12,3),'❀')
define(60,'dog-face','犬の顔',s((7,5),(11,3),(16,4),(19,9),(19,18),(15,22),(9,22),(5,18),(5,9))+s((7,5),(3,3),(1,8),(2,16),(5,18))+s((17,5),(21,4),(23,9),(22,17),(19,18))+dot(9,11)+dot(15,11)+s((9,15),(15,15),(12,18),(9,15))+s((12,18),(12,20)),'🐶')
define(61,'cat-face','猫の顔',s((3,12),(3,2),(9,6),(15,6),(21,2),(21,12),(20,18),(16,22),(8,22),(4,18),(3,12))+dot(8,12)+dot(16,12)+s((10,15),(14,15),(12,17),(10,15))+s((12,17),(10,19))+s((12,17),(14,19))+s((0,14),(6,16))+s((0,19),(6,18))+s((18,16),(24,14))+s((18,18),(24,19)),'🐱')
define(62,'footprints','足跡',s((4,8),(7,7),(10,9),(10,14),(8,18),(5,18),(3,15),(3,11),(4,8))+s((16,13),(19,12),(22,14),(22,19),(20,23),(17,23),(15,20),(15,16),(16,13))+dot(4,4)+dot(8,3)+dot(11,5)+dot(16,9)+dot(20,8)+dot(23,10),'👣')
define(63,'wastebasket','ごみ箱',s((5,6),(7,23),(17,23),(19,6))+s((3,5),(21,5))+s((8,5),(8,2),(16,2),(16,5))+s((10,9),(10,19))+s((14,9),(14,19)),'🗑')

GLYPHS = deepcopy(PUA_GLYPHS)
for unicode_char,pua_char in ALIASES.items():
    GLYPHS[unicode_char]=deepcopy(PUA_GLYPHS[pua_char])
REPERTOIRE = ''.join(sorted(GLYPHS,key=ord))
PUA_REPERTOIRE = ''.join(sorted(PUA_GLYPHS,key=ord))
assert len(PUA_GLYPHS)==64
assert set(PUA_GLYPHS)==set(map(chr,range(0xE000,0xE040)))
