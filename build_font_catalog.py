"""Generate an exhaustive searchable catalogue from the active bitmap atlases."""
import base64
import html
import json
import unicodedata
from PIL import Image,ImageDraw
from dot_font import ROOT
from custom_japanese_strokes import EDUCATION_GRADES
from joyo_repertoire import JOYO, ALTERNATE_FORMS, SOURCE_URL

GRADE_BY_CHAR = {c: grade for grade, chars in EDUCATION_GRADES.items() for c in chars}
JOYO_SET = set(JOYO)


def group(c):
    n=ord(c)
    if 32<=n<=126: return 'ASCII'
    if 0x3041<=n<=0x3096: return 'ひらがな'
    if 0x30A1<=n<=0x30FA or 0x31F0<=n<=0x31FF: return 'カタカナ'
    if c in GRADE_BY_CHAR: return f'常用漢字・第{GRADE_BY_CHAR[c]}学年'
    if c in JOYO_SET: return '常用漢字・中学校以降'
    if c in ALTERNATE_FORMS: return '異体字コードポイント（常用字に対応）'
    if 0x4E00<=n<=0x9FFF: return '漢字・常用外'
    if 0xFF01<=n<=0xFF5E: return '全角英数字・記号'
    return 'その他の記号・空白'


def main():
    entries={}
    japanese_count=0
    for name in ('custom-ascii-24','custom-jp-24'):
        meta=json.loads((ROOT/f'{name}.json').read_text())
        if name=='custom-jp-24': japanese_count=len(meta['glyphs'])
        with Image.open(ROOT/meta['image']) as im:
            atlas=im.convert('L')
        for c,g in meta['glyphs'].items():
            crop=atlas.crop((g['x'],g['y'],g['x']+g['width'],g['y']+g['height']))
            entries.setdefault(c,(name,g,crop))
    chars=sorted(entries)
    lines=['# 全収録文字一覧', '', f'現行の独自単線フォント：**{len(chars)}文字**（重複なし）。',
           '', f'ASCII 95文字＋度記号、日本語側{japanese_count}文字。18px版・24px版は同じ収録範囲。',
           '旧Hershey／ChocoKanjiの保存用画像は集計に含めない。制御文字・半角カナ・任意の漢字全域は未収録。',
           '結合濁点・半濁点も1コードポイントとして記載。分解仮名は描画時に合成済み字形へ解決する。',
           '', '[検索可能な字形一覧](catalog.html) / [全字形画像](catalog.png)', '']
    missing=JOYO_SET-entries.keys()
    if missing:
        raise ValueError(f'Joyo glyphs missing: {sorted(missing)}')
    secondary=''.join(c for c in JOYO if c not in GRADE_BY_CHAR)
    lines += ['## 常用漢字の収録確認', '',
              f'[文化庁の代表音訓索引]({SOURCE_URL})の2,136字種を全収録。',
              f'教育漢字1,026字＋中学校以降{len(secondary):,}字。字種は索引の画像alt表記から取得。',
              '別コードポイントの「填・剥・頬・𠮟」も収録。入力本文を書き換えず個別に描画する。',
              '追加漢字の部品構成はCJKVI-IDS/CHISEを参照し、線分座標と配置調整は独自。',
              '★●▲▼■は塗りつぶし、その他は単線。[生成元・ライセンス](README.md#構成データと独自線分)。', '']
    for page,start in enumerate(range(0,len(secondary),192),1):
        subset=secondary[start:start+192]
        preview=Image.new('RGB',(16*72,((len(subset)+15)//16)*60),'#111111')
        pen=ImageDraw.Draw(preview)
        for index,c in enumerate(subset):
            crop=entries[c][2];x,y=index%16*72,index//16*60
            preview.paste(crop.convert('RGB'),(x+(72-crop.width)//2,y+4))
            pen.text((x+5,y+34),f'U+{ord(c):04X}',fill='white')
        preview.save(ROOT/f'joyo-secondary-{page}.png')
        lines.append(f'[中学校以降の見本 {page}](joyo-secondary-{page}.png)')
    lines.append('')
    lines += ['## 教育漢字の収録確認', '', '依頼本文の1,026字を対象とする。字形は独自の単線データ。', '',
              '| 学年 | 対象 | 収録 | 未収録 | 字形見本 |', '|---|---:|---:|---|---|']
    for grade, subset in sorted(EDUCATION_GRADES.items()):
        missing=set(subset)-entries.keys()
        lines.append(f'| 第{grade}学年 | {len(subset)} | {len(set(subset)-missing)} | {"".join(sorted(missing)) or "なし"} | [画像](education-grade-{grade}.png) |')
        if missing:
            raise ValueError(f'Grade {grade} missing glyphs: {sorted(missing)}')
        grade_sheet=Image.new('RGB',(16*72,((len(subset)+15)//16)*60),'#111111')
        grade_draw=ImageDraw.Draw(grade_sheet)
        for index,c in enumerate(subset):
            crop=entries[c][2];x,y=index%16*72,index//16*60
            grade_sheet.paste(crop.convert('RGB'),(x+(72-crop.width)//2,y+4))
            grade_draw.text((x+5,y+34),f'U+{ord(c):04X}',fill='white')
        grade_sheet.save(ROOT/f'education-grade-{grade}.png')
    lines.append('')
    cards=[]
    sheet=Image.new('RGB',(16*72,((len(chars)+15)//16)*60),'#111111')
    draw=ImageDraw.Draw(sheet)
    for index,c in enumerate(chars):
        name,g,crop=entries[c]
        category=group(c);cp=f'U+{ord(c):04X}'
        label='SPACE' if c==' ' else '全角空白' if c=='　' else c
        import io
        buffer=io.BytesIO();crop.save(buffer,format='PNG')
        encoded=base64.b64encode(buffer.getvalue()).decode()
        cards.append(f'<article data-search="{html.escape(c+" "+cp+" "+category+" "+unicodedata.name(c,"UNKNOWN"),quote=True)}"><img alt="{html.escape(label,quote=True)}" src="data:image/png;base64,{encoded}" width="{g["width"]*2}" height="{g["height"]*2}"><span>{html.escape(label)}</span><code>{cp}</code><small>{category}</small></article>')
        x,y=index%16*72,index//16*60
        sheet.paste(crop.convert('RGB'),(x+(72-crop.width)//2,y+4))
        draw.text((x+5,y+34),cp,fill='white')
    for category in dict.fromkeys(group(c) for c in chars):
        subset=[c for c in chars if group(c)==category]
        lines += [f'## {category}（{len(subset)}文字）','', '```text']
        for start in range(0,len(subset),32): lines.append(''.join(subset[start:start+32]))
        lines += ['```','', '| 文字 | Unicode | Unicode名称 |', '|---|---|---|']
        for c in subset:
            label='SPACE' if c==' ' else '全角空白' if c=='　' else c
            # HTML entities keep literal pipes/backticks safe in Markdown cells.
            label=''.join(f'&#{ord(x)};' for x in label)
            lines.append(f'| {label} | U+{ord(c):04X} | {unicodedata.name(c,"UNKNOWN")} |')
        lines.append('')
    (ROOT/'CHARACTERS.md').write_text('\n'.join(lines)+'\n')
    sheet.save(ROOT/'catalog.png')
    page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>全収録文字一覧</title><style>
body{background:#14171b;color:#eee;font:16px system-ui;margin:24px}h1{font-size:24px}input{font:inherit;padding:10px;width:min(90%,500px);margin:12px 0}#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px}article{background:#000;display:flex;align-items:center;flex-direction:column;gap:6px;padding:12px 4px;border:1px solid #353b43}article img{image-rendering:pixelated;height:48px;object-fit:contain}small{font-size:11px;color:#bac7d6}article[hidden]{display:none}p{max-width:850px}</style><h1>全収録文字一覧 — COUNT文字</h1><p>現行の独自単線フォント。画像は24px版を2倍で表示しています。常用漢字2,136字（教育漢字1,026字＋中学校以降1,110字）を含みます。★●▲▼■は塗りつぶしです。文字、学年、U+番号、分類、Unicode名称で検索できます。</p><input id="q" aria-label="文字を検索" placeholder="例：鬱 ／ 中学校以降 ／ 常用漢字 ／ ★ ／ U+3042"><p id="count"></p><main id="grid">CARDS</main><script>
const cards=[...document.querySelectorAll('article')];function filter(){const q=document.querySelector('#q').value.toLowerCase();let n=0;for(const c of cards){c.hidden=!c.dataset.search.toLowerCase().includes(q);if(!c.hidden)n++}document.querySelector('#count').textContent=n+' / '+cards.length+'文字';}document.querySelector('#q').addEventListener('input',filter);filter();</script></html>'''
    (ROOT/'catalog.html').write_text(page.replace('COUNT',str(len(chars))).replace('CARDS',''.join(cards)))
    print('catalog:',len(chars),'unique characters')


if __name__=='__main__':
    main()
