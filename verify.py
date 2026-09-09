import hashlib,json
from pathlib import Path
from dot_font import DotFont
from joyo_repertoire import JOYO
root=Path(__file__).parent/'assets/fonts'
for size in (18,24):
 f=DotFont(f'custom-jp-{size}',f'custom-ascii-{size}')
 assert not f.missing(JOYO+'寿帝差弔彙挿忌憶懐拳泰港熊戴期栄栽熱瓶魔鬱')
 assert len({f.mask(c).tobytes() for c in JOYO})==2136
 chars=set()
 for kind in ('jp','ascii'):
  m=json.loads((root/f'custom-{kind}-{size}.json').read_text())
  assert hashlib.sha256((root/m['image']).read_bytes()).hexdigest()==m['sha256']
  chars.update(m['glyphs'])
 assert len(chars)==2584
 assert f.mask('日本語 ABC 123 ★').any()
print('PASS: both sizes, 2584 characters, all Joyo, unique Joyo bitmaps, image hashes and rendering')
