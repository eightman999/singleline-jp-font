"""Exhaustive delivered-artifact inventory and assignable visual proof pages.

Automatic geometry/pixel checks NEVER certify Japanese letterforms. Each review
starts pending. TTF sequence images use a temporary in-memory cmap pointing to
one exact delivered glyph; this is not a claim that GSUB shaping was tested.
"""
import argparse
from collections import defaultdict
from dataclasses import asdict
import gzip
import hashlib
import html
from io import BytesIO
import json
import math
from pathlib import Path
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont, TTCollection
from family.bitmap_reader import BitmapFont
from family.data_loader import load_glyphs
from family.model import glyph_name
from family.styles import STYLES
from family.tools.priority_glyph_qa import pixel_signature

SIZES = (16, 18, 24, 32)
REF = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(text):
    return '+'.join(f'U+{ord(c):04X}' for c in text)


def expected_blank(text, glyph):
    # Empty source geometry alone is NOT evidence that a blank is intended.
    return glyph.category == 'space' or all(c.isspace() for c in text)


def source_inventory(glyphs):
    return [{"text": t, "id": identity(t), "kind": 'scalar' if len(t) == 1 else 'sequence',
             "glyph_name": glyph_name(t), "source_sha256": digest(asdict(g)),
             "source": g.source, "source_status": g.status, "category": g.category,
             "expected_blank": expected_blank(t, g), "visual_review": 'pending'}
            for t, g in sorted(glyphs.items(), key=lambda x: tuple(map(ord, x[0])))]


class DirectFont:
    """FreeType rasterization of an exact glyph, via ephemeral PUA cmap.

    No outline, metric, hint or variation-table changes. This intentionally
    bypasses shaping; GSUB/application shaping remains a separate review.
    """
    def __init__(self, font, mapping):
        from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
        self.mapping = {t: chr(0xF0000 + i) for i, t in enumerate(mapping)}
        cmap = CmapSubtable.newSubtable(12)
        cmap.platformID, cmap.platEncID, cmap.language = 3, 10, 0
        cmap.cmap = {ord(self.mapping[t]): n for t, n in mapping.items()}
        font['cmap'].tables = [cmap]
        stream = BytesIO()
        font.save(stream)
        self.data = stream.getvalue()
        self.fonts = {}

    def mask(self, text, size):
        if text not in self.mapping:
            return None
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(BytesIO(self.data), size, layout_engine=ImageFont.Layout.BASIC)
        font = self.fonts[size]
        char = self.mapping[text]
        mask, offset = font.getmask2(char, mode='L', anchor='ls')
        image = Image.frombytes('L', mask.size, bytes(mask))
        return image, offset, font.getlength(char)


def reference_font(path, items):
    collection = TTCollection(path, lazy=True)
    faces = []
    index = None
    for i, font in enumerate(collection.fonts):
        names = sorted({n.toUnicode() for n in font['name'].names if n.nameID in (1, 4, 6)})
        faces.append({'index': i, 'names': names})
        if any('NotoSansCJKjp-Regular' == n for n in names):
            index = i
    collection.close()
    if index is None:
        raise ValueError('Could not verify Japanese face in reference collection')
    font = TTFont(path, fontNumber=index)
    cmap = font.getBestCmap()
    mapping = {r['text']: cmap[ord(r['text'])] for r in items if len(r['text']) == 1 and ord(r['text']) in cmap}
    # Exact ligature lookups only; do not pretend independent scalar rendering
    # or NFC-normalization proves an explicit multiscalar reference glyph.
    ligatures = {}
    if 'GSUB' in font:
        for lookup in font['GSUB'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                if lookup.LookupType == 7:
                    sub = sub.ExtSubTable
                for first, entries in getattr(sub, 'ligatures', {}).items():
                    for entry in entries:
                        ligatures[(first, *entry.Component)] = entry.LigGlyph
    for r in items:
        t = r['text']
        if len(t) > 1 and all(ord(c) in cmap for c in t):
            name = ligatures.get(tuple(cmap[ord(c)] for c in t))
            if name:
                mapping[t] = name
    info = {'path': str(path), 'sha256': file_sha(path), 'jp_face_index': index,
            'faces': faces, 'present': len(mapping), 'missing': len(items)-len(mapping),
            'sequence_reference_policy': 'exact GSUB ligature only; no NFC substitution or concatenated text fallback'}
    return DirectFont(font, mapping), info



class FallbackReference:
    """Exact JP glyphs, then explicitly labelled canonical-scalar fallbacks."""
    def __init__(self, primary, mappings, faces):
        self.primary, self.mappings, self.faces = primary, mappings, faces
        self.fonts = {}

    def mask(self, text, size):
        if text in self.primary.mapping:
            return self.primary.mask(text, size)
        if text not in self.mappings:
            return None
        face, char = self.mappings[text]
        path, index = self.faces[face]
        emoji = 'ColorEmoji' in str(path)
        native_size = 109 if emoji else size
        key = (face, native_size)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(str(path), native_size, index=index, layout_engine=ImageFont.Layout.BASIC)
        font = self.fonts[key]
        if emoji:
            tile = Image.new('RGBA', (160,160))
            ImageDraw.Draw(tile).text((0,120),char,font=font,anchor='ls',embedded_color=True)
            # Reference silhouette only; delivered font is monochrome.
            alpha = tile.getchannel('A').resize((round(160*size/109),round(160*size/109)),Image.Resampling.LANCZOS)
            return alpha, (0,-round(120*size/109)), font.getlength(char)*size/109
        mask, offset = font.getmask2(char,mode='L',anchor='ls')
        return Image.frombytes('L',mask.size,bytes(mask)),offset,font.getlength(char)


def complete_reference(path, items):
    primary, info = reference_font(path, items)
    faces = [(Path(path),info['jp_face_index'])]
    faces += [(Path('/usr/share/fonts/truetype/noto')/name,0) for name in (
        'NotoSans-Regular.ttf','NotoSansMath-Regular.ttf','NotoSansSymbols-Regular.ttf',
        'NotoSansSymbols2-Regular.ttf','NotoColorEmoji.ttf')
        if (Path('/usr/share/fonts/truetype/noto')/name).exists()]
    cmaps = []
    for file,index in faces:
        with TTFont(file,fontNumber=index) as font:
            cmaps.append(set(font.getBestCmap()))
    mappings, records = {}, []
    for item in items:
        text = item['text']
        entry = {'id':item['id'], 'reference':None, 'method':'missing'}
        if text in primary.mapping:
            entry.update(reference=str(path), face_index=info['jp_face_index'], method='exact glyph')
        else:
            normalized = unicodedata.normalize('NFC',text)
            if len(normalized)==1:
                for i,cmap in enumerate(cmaps):
                    if ord(normalized) in cmap:
                        mappings[text] = (i,normalized)
                        entry.update(reference=str(faces[i][0]),face_index=faces[i][1],reference_text=normalized,
                                     method='NFC-equivalent scalar reference' if normalized!=text else 'fallback scalar reference')
                        break
        records.append(entry)
    info['reference_records'] = records
    info['fallback_faces'] = [{'path':str(p),'face_index':i,'sha256':file_sha(p)} for p,i in faces]
    info['present_with_fallback'] = sum(r['reference'] is not None for r in records)
    info['missing_with_fallback'] = sum(r['reference'] is None for r in records)
    return FallbackReference(primary,mappings,faces),info

def collision_groups(records, field):
    groups = defaultdict(list)
    for r in records:
        if r.get('exists') and not r.get('empty') and r.get(field):
            groups[r[field]].append(r['id'])
    return {k: v for k, v in groups.items() if len(v) > 1}


def write_records(path, records):
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n')


def inspect_ttf(path, items, output):
    font = TTFont(path)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    names = set(font.getGlyphOrder())
    sha = file_sha(path)
    records, mapping = [], {}
    for item in items:
        t = item['text']
        name = cmap.get(ord(t)) if len(t) == 1 else item['glyph_name']
        exists = name in names
        r = dict(item, artifact_sha256=sha, exists=exists, delivered_glyph_name=name,
                 review_scope='variable-default' if 'fvar' in font else 'static',
                 mapping_method='cmap' if len(t) == 1 else 'explicit glyph name; GSUB not certified')
        if exists:
            mapping[t] = name
            pen = DecomposingRecordingPen(gs)
            gs[name].draw(pen)
            bounds = BoundsPen(gs)
            gs[name].draw(bounds)
            advance = font['hmtx'][name][0]
            r.update(bbox=bounds.bounds, advance=advance, empty=bounds.bounds is None,
                     outline_sha256=digest([pen.value, advance]))
            r['unexpected_blank'] = r['empty'] and not item['expected_blank']
            r['unexpected_ink'] = not r['empty'] and item['expected_blank']
        records.append(r)
    collisions = collision_groups(records, 'outline_sha256')
    for r in records:
        r['collision_group'] = r.get('outline_sha256') if r.get('outline_sha256') in collisions else None
    write_records(output / (path.stem + '.jsonl.gz'), records)
    (output / (path.stem + '-collisions.json')).write_text(json.dumps(collisions, ensure_ascii=False))
    summary = {'artifact': str(path), 'sha256': sha, 'kind': 'ttf', 'records': len(records),
               'missing': sum(not r['exists'] for r in records),
               'unexpected_blank': sum(r.get('unexpected_blank', False) for r in records),
               'unexpected_ink': sum(r.get('unexpected_ink', False) for r in records),
               'collision_groups': len(collisions), 'visual_review': 'pending',
               'ledger': path.stem + '.jsonl.gz'}
    if 'fvar' in font:
        summary['variation_axes'] = {a.axisTag: [a.minValue, a.defaultValue, a.maxValue] for a in font['fvar'].axes}
        summary['variation_coverage'] = 'default instance only; axis extremes/intermediates pending'
    return DirectFont(font, mapping), summary


def inspect_bitmap(path, items, output):
    font = BitmapFont(path)
    sha = file_sha(path)
    records = []
    for item in items:
        t = item['text']
        r = dict(item, artifact_sha256=sha, exists=t in font.glyphs)
        if r['exists']:
            mask = font.bitmap(t)
            w, h, advance, bx, by, _, _ = font.glyphs[t]
            ys, xs = np.nonzero(mask)
            bbox = [int(xs.min())+bx, int(ys.min())-by, int(xs.max())+1+bx, int(ys.max())+1-by] if len(xs) else None
            r.update(bbox=bbox, advance=advance, bearing=[bx, by], frame=[w, h], empty=not len(xs),
                     pixel_sha256=pixel_signature(mask, bx, by, advance))
            r['unexpected_blank'] = r['empty'] and not item['expected_blank']
            r['unexpected_ink'] = not r['empty'] and item['expected_blank']
        records.append(r)
    collisions = collision_groups(records, 'pixel_sha256')
    for r in records:
        r['collision_group'] = r.get('pixel_sha256') if r.get('pixel_sha256') in collisions else None
    write_records(output / (path.stem + '.jsonl.gz'), records)
    (output / (path.stem + '-collisions.json')).write_text(json.dumps(collisions, ensure_ascii=False))
    return font, {'artifact': str(path), 'sha256': sha, 'kind': 'sjpb', 'records': len(records),
                  'missing': sum(not r['exists'] for r in records),
                  'unexpected_blank': sum(r.get('unexpected_blank', False) for r in records),
               'unexpected_ink': sum(r.get('unexpected_ink', False) for r in records),
                  'collision_groups': len(collisions), 'visual_review': 'pending', 'ledger': path.stem + '.jsonl.gz'}


def paste_mask(canvas, result, x, y, scale=1):
    if result is None:
        ImageDraw.Draw(canvas).text((x, y+20), 'MISSING', fill='red')
        return
    mask, offset, _ = result
    if mask.width and mask.height:
        mask = mask.resize((mask.width*scale, mask.height*scale), Image.Resampling.NEAREST)
        canvas.paste('black', (x+round(offset[0]*scale), y+round(offset[1]*scale)), mask)


def render_pages(items, name, direct, reference, bitmaps, output, max_pages=None):
    directory = output / 'pages' / name
    directory.mkdir(parents=True, exist_ok=True)
    pages = []
    chunks = [items[i:i+80] for i in range(0, len(items), 80)]
    for number, chunk in enumerate(chunks[:max_pages] if max_pages else chunks, 1):
        # Four columns x twenty rows, each glyph cell shows reference and both
        # delivered TTF sizes, plus all four exact SJPB sizes for this style.
        image = Image.new('RGB', (1840, 80+20*164), 'white')
        draw = ImageDraw.Draw(image)
        draw.text((12, 10), f'{name} | page {number}/{len(chunks)} | VISUAL REVIEW PENDING', fill='black')
        draw.text((12, 28), 'Noto JP/fallback/NFC 64 | TTF 64 | TTF 32 (2x) | SJPB 16/18/24/32 (2x). Direct glyph render; shaping not certified.', fill='black')
        for i, item in enumerate(chunk):
            x, y = (i%4)*460, 80+(i//4)*164
            t = item['text']
            draw.rectangle((x,y,x+459,y+163), outline='#cccccc')
            draw.text((x+4,y+3), item['id'], fill='black')
            draw.text((x+4,y+16), item['kind']+(' BLANK EXPECTED' if item['expected_blank'] else ''), fill='black')
            paste_mask(image, reference.mask(t,64), x+6,y+94)
            paste_mask(image, direct.mask(t,64), x+88,y+94)
            paste_mask(image, direct.mask(t,32), x+170,y+94,2)
            for j, size in enumerate(SIZES):
                bx = x+252+j*50
                bitmap = bitmaps.get(size)
                if bitmap is None or t not in bitmap.glyphs:
                    draw.text((bx,y+60), 'N/A', fill='red')
                    continue
                mask = Image.fromarray(bitmap.bitmap(t).astype('uint8')*255)
                # 32px tile spans 64px; overlapping columns are avoided by
                # splitting bitmap tiles over two rows.
                bx = x+256+(j%2)*90
                baseline = y+96+(j//2)*61
                _, _, advance, bearing_x, bearing_y, _, _ = bitmap.glyphs[t]
                paste_mask(image, (mask,(bearing_x,-bearing_y),advance), bx,baseline,2)
                draw.text((bx+66, baseline-12), str(size), fill='black')
        path = directory / f'{number:04d}.png'
        image.save(path, compress_level=1)
        pages.append({'page': str(path.relative_to(output)), 'style': name, 'page_number': number,
                      'first': chunk[0]['id'], 'last': chunk[-1]['id'], 'count': len(chunk),
                      'glyph_ids': [r['id'] for r in chunk], 'assigned_to': None, 'artifact_sha256': getattr(direct,'artifact_sha256',None),
                      'visual_review': 'pending', 'review_notes': None})
        if number == 1 or number % 20 == 0:
            print(f'PAGE {name} {number}/{len(chunks)}', flush=True)
    return pages



def inspect_supplementary(path, glyphs, output):
    """Track all declared SVS and subs/sups identities independently."""
    from family.font_builder import feature_glyphs, standard_variants
    font = TTFont(path)
    gs = font.getGlyphSet()
    sha = file_sha(path)
    variations = {}
    for table in font['cmap'].tables:
        if table.format == 14:
            for selector, entries in table.uvsDict.items():
                for base, name in entries:
                    variations[(base, selector)] = name or font.getBestCmap().get(base)
    substitutions = {}
    if 'GSUB' in font:
        table = font['GSUB'].table
        for feature in table.FeatureList.FeatureRecord:
            if feature.FeatureTag not in ('subs', 'sups'):
                continue
            mapping = substitutions.setdefault(feature.FeatureTag, {})
            for index in feature.Feature.LookupListIndex:
                for sub in table.LookupList.Lookup[index].SubTable:
                    mapping.update(getattr(sub, 'mapping', {}))
    targets = []
    for sequence, target in standard_variants(glyphs):
        actual = variations.get(tuple(map(ord, sequence)))
        targets.append((identity(sequence), sequence, 'svs', glyph_name(target), actual, target))
    for tag in ('subs', 'sups'):
        for char in feature_glyphs(glyphs):
            actual = substitutions.get(tag, {}).get(glyph_name(char))
            targets.append((identity(char)+'/'+tag, char, tag, glyph_name(char)+'.'+tag, actual, char))
    records = []
    for ident, text, kind, expected, actual, source in targets:
        r = dict(id=ident, text=text, kind=kind, expected_glyph_name=expected,
                 actual_glyph_name=actual, mapping_correct=actual==expected,
                 exists=actual in gs if actual else False, source_sha256=digest(asdict(glyphs[source])),
                 artifact_sha256=sha, visual_review='pending', visual_page='pending',
                 bitmap_scope='not independent SJPB identities; not certified')
        if r['exists']:
            pen = BoundsPen(gs)
            gs[actual].draw(pen)
            r.update(bbox=pen.bounds, advance=font['hmtx'][actual][0], empty=pen.bounds is None)
        records.append(r)
    write_records(output/(path.stem+'-supplementary.jsonl.gz'),records)
    font.close()
    return {'svs': sum(r['kind']=='svs' for r in records),
            'feature_forms': sum(r['kind']!='svs' for r in records),
            'mapping_errors': sum(not r['mapping_correct'] for r in records),
            'visual_review': 'pending', 'ledger': path.stem+'-supplementary.jsonl.gz'}


class ReferenceAliases:
    def __init__(self, reference, aliases):
        self.reference, self.aliases = reference, aliases

    def mask(self, text, size):
        return self.reference.mask(self.aliases[text], size)


def supplementary_pages(path, glyphs, reference, output, max_pages=None):
    """Show SVS target reference and feature BASE reference, clearly labelled.

    Feature base comparisons check recognizability, not intended scale/rise.
    Independent feature/SVS bitmap strikes are not part of SJPB's repertoire.
    """
    from family.font_builder import standard_variants
    ledger = output/'ledgers'/(path.stem+'-supplementary.jsonl.gz')
    with gzip.open(ledger,'rt') as f:
        rows = [json.loads(line) for line in f]
    variants = dict(standard_variants(glyphs))
    mapping, aliases, items = {}, {}, []
    for row in rows:
        key = row['id']
        if row['exists']:
            mapping[key] = row['actual_glyph_name']
        aliases[key] = variants[row['text']] if row['kind']=='svs' else row['text']
        items.append(dict(id=key,text=key,kind='SVS target ref' if row['kind']=='svs' else row['kind']+' BASE REF ONLY',expected_blank=False))
    direct = DirectFont(TTFont(path),mapping)
    direct.artifact_sha256 = file_sha(path)
    name = path.stem.replace('SinglelineJPLab-','')+'-supplementary'
    pages = render_pages(items,name,direct,ReferenceAliases(reference,aliases),{},output,max_pages)
    locations = {ident: page['page'] for page in pages for ident in page['glyph_ids']}
    for row in rows:
        row['visual_page'] = locations.get(row['id'],'pending')
    write_records(ledger,rows)
    return pages


VARIABLE_GRID = tuple({'wght':wght,'slnt':slnt} for wght in (200,400,700) for slnt in (0,-6,-12))


def outline_issues(commands, bounds, advance, upem):
    """Detect numeric/path failures, not Japanese form correctness.

    A very large bounding box is a review flag, not proof of a bad glyph.
    Self intersections, aesthetic quality and raster hinting are not checked.
    """
    def finite(value):
        if isinstance(value,(int,float)):
            return math.isfinite(value)
        if isinstance(value,(list,tuple)):
            return all(finite(v) for v in value)
        return True
    issues=[]
    if not finite([commands,bounds,advance]):
        issues.append('non-finite-coordinate-or-metric')
    if advance is not None and advance<0:
        issues.append('negative-advance')
    if bounds is not None:
        x0,y0,x1,y1=bounds
        if x1<=x0 or y1<=y0:
            issues.append('zero-or-negative-ink-bbox-area')
        if max(abs(x0),abs(y0),abs(x1),abs(y1))>8*upem:
            issues.append('bbox-beyond-8-em-review-flag')
    return issues


def inspect_variable_grid(path, items, output):
    """Audit 9 discrete wght/slnt points; no continuous-space certification."""
    output=Path(output)/'variable-grid'
    output.mkdir(parents=True,exist_ok=True)
    font=TTFont(path)
    if 'fvar' not in font:
        raise ValueError('Variable grid requires fvar: '+str(path))
    axes={a.axisTag:(a.minValue,a.maxValue) for a in font['fvar'].axes}
    artifact_sha=file_sha(path)
    cmap=font.getBestCmap()
    upem=font['head'].unitsPerEm
    summaries=[]
    for location in VARIABLE_GRID:
        if any(tag not in axes or not axes[tag][0]<=value<=axes[tag][1] for tag,value in location.items()):
            raise ValueError('Requested representative point outside declared axes: '+str(location))
        # fontTools applies gvar/HVAR at this discrete user-space location.
        gs=font.getGlyphSet(location=location,normalized=False)
        records=[]
        for item in items:
            text=item['text']
            name=cmap.get(ord(text)) if len(text)==1 else item['glyph_name']
            exists=name in gs if name else False
            record=dict(item,artifact_sha256=artifact_sha,location=location,exists=exists,
                        delivered_glyph_name=name,visual_review='pending',
                        automatic_scope='discrete variable outline/metric checks; not raster or continuous-axis certification')
            if exists:
                try:
                    pen=DecomposingRecordingPen(gs);gs[name].draw(pen)
                    bounds=BoundsPen(gs);pen.replay(bounds)
                    advance=gs[name].width
                    issues=outline_issues(pen.value,bounds.bounds,advance,upem)
                    empty=bounds.bounds is None
                    record.update(bbox=bounds.bounds,advance=advance,empty=empty,
                                  unexpected_blank=empty and not item['expected_blank'],
                                  unexpected_ink=not empty and item['expected_blank'],
                                  outline_sha256=digest([pen.value,advance]),outline_issues=issues)
                except Exception as exc:
                    record.update(outline_issues=['outline-evaluation-error'],error=type(exc).__name__+': '+str(exc))
            else:
                record['outline_issues']=['missing-glyph']
            records.append(record)
        filename=Path(path).stem+f'-wght{location["wght"]}-slnt{location["slnt"]}.jsonl.gz'
        write_records(output/filename,records)
        summary={'location':location,'records':len(records),'artifact_sha256':artifact_sha,
                 'missing':sum(not r['exists'] for r in records),
                 'unexpected_blank':sum(r.get('unexpected_blank',False) for r in records),
                 'unexpected_ink':sum(r.get('unexpected_ink',False) for r in records),
                 'outline_issue_records':sum(bool(r.get('outline_issues')) for r in records),
                 'ledger':'variable-grid/'+filename,'visual_review':'pending'}
        summaries.append(summary)
        print('VARIABLE GRID',Path(path).name,location,summary['outline_issue_records'],flush=True)
    font.close()
    return {'representative_points':len(summaries),'records':sum(s['records'] for s in summaries),
            'method':'fontTools getGlyphSet user-space location; gvar/HVAR outline and metric evaluation',
            'continuous_axis_space':'not-certified','rasterization':'not-tested-by-grid',
            'visual_review':'pending','instances':summaries}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, default=ROOT/'build/family')
    parser.add_argument('--output', type=Path, default=ROOT/'build/full-proofread')
    parser.add_argument('--reference', type=Path, default=REF)
    parser.add_argument('--pages', choices=('none','singleline','all'), default='all')
    parser.add_argument('--max-pages', type=int)
    parser.add_argument('--variable-grid', action='store_true', help='Also audit wght 200/400/700 x slnt 0/-6/-12 on both variable fonts; visual review remains pending')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    ledger = args.output/'ledgers'
    ledger.mkdir(exist_ok=True)
    glyphs = load_glyphs()[0]
    items = source_inventory(glyphs)
    write_records(args.output/'source-inventory.jsonl.gz', items)
    reference, ref_info = complete_reference(args.reference, items)
    manifest = {'schema_version': 1, 'scalars': sum(r['kind']=='scalar' for r in items),
                'sequences': sum(r['kind']=='sequence' for r in items), 'total': len(items),
                'generator_sha256': file_sha(__file__), 'reference': ref_info,
                'visual_review': 'pending', 'japanese_proofreading_certified': False,
                'source_linkage': 'Source hashes describe load_glyphs at audit time; byte-identical rebuild provenance is not established by this audit.',
                'collision_policy': 'same outline/pixels and advance; semantic aliases require human classification, not automatic failure',
                'rendering': 'FreeType via Pillow BASIC; temporary in-memory cmap selects exact delivered glyph. No shaping certification.',
                'artifacts': [], 'pages': []}
    expected = [args.artifacts/'static'/f'SinglelineJPLab-{style}.ttf' for style in STYLES]
    expected += [args.artifacts/'variable'/f'SinglelineJPLab-{style}-VF.ttf' for style in ('gothic','serif')]
    expected += [args.artifacts/'bitmaps'/f'{style}-{size}.sjpb' for style in STYLES for size in SIZES]
    manifest['expected_artifact_count'] = len(expected)
    manifest['missing_artifacts'] = [str(p) for p in expected if not p.exists()]
    manifest['expected_primary_glyph_style_cases'] = len(items)*10
    manifest['expected_supplementary_glyph_style_cases'] = 339*10
    paths = sorted((args.artifacts/'static').glob('*.ttf'))+sorted((args.artifacts/'variable').glob('*.ttf'))
    bitmaps = {}
    for path in sorted((args.artifacts/'bitmaps').glob('*.sjpb')):
        bitmap, summary = inspect_bitmap(path, items, ledger)
        style, size = path.stem.rsplit('-',1)
        bitmaps.setdefault(style,{})[int(size)] = bitmap
        manifest['artifacts'].append(summary)
        print('AUDIT',path.name,flush=True)
    for path in paths:
        direct, summary = inspect_ttf(path, items, ledger)
        direct.artifact_sha256 = summary['sha256']
        summary['supplementary'] = inspect_supplementary(path, glyphs, ledger)
        if args.variable_grid and 'variation_axes' in summary:
            summary['variable_grid'] = inspect_variable_grid(path,items,ledger)
        manifest['artifacts'].append(summary)
        style = path.stem.replace('SinglelineJPLab-','')
        print('AUDIT',path.name,flush=True)
        if args.pages == 'all' or (args.pages == 'singleline' and style == 'singleline'):
            pages = render_pages(items,style,direct,reference,bitmaps.get(style,{}),args.output,args.max_pages)
            manifest['pages'].extend(pages)
            extra_pages = supplementary_pages(path,glyphs,reference,args.output,args.max_pages)
            manifest['pages'].extend(extra_pages)
        (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    for page in manifest['pages']:
        page_path = args.output/page['page']
        with Image.open(page_path) as image:
            image.verify()
        page['page_sha256'] = file_sha(page_path)
    manifest['automatic_records'] = sum(a['records'] for a in manifest['artifacts'])
    manifest['variable_grid_records'] = sum(a.get('variable_grid',{}).get('records',0) for a in manifest['artifacts'])
    manifest['supplementary_records'] = sum(a.get('supplementary',{}).get('svs',0)+a.get('supplementary',{}).get('feature_forms',0) for a in manifest['artifacts'])
    manifest['rendered_glyph_style_cases'] = sum(p['count'] for p in manifest['pages'])
    manifest['rendered_primary_glyph_style_cases'] = sum(p['count'] for p in manifest['pages'] if not p['style'].endswith('-supplementary'))
    manifest['rendered_supplementary_glyph_style_cases'] = sum(p['count'] for p in manifest['pages'] if p['style'].endswith('-supplementary'))
    manifest['visually_reviewed_glyph_style_cases'] = 0
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    (args.output/'reference-coverage.json').write_text(json.dumps(ref_info,ensure_ascii=False,indent=2))
    (args.output/'page-assignments.json').write_text(json.dumps(manifest['pages'],ensure_ascii=False,indent=2))
    links = '\n'.join(f'<li><a href="{html.escape(p["page"])}">{html.escape(p["style"])} {p["page_number"]}: {p["first"]} — {p["last"]}</a> pending</li>' for p in manifest['pages'])
    (args.output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Full glyph proof sheets</title><h1>Full glyph proof sheets</h1><p>All reviews pending. Automatic checks do not certify Japanese letterforms. Reference missing means no exact reference glyph; variable fonts show default instance only.</p><ul>'+links+'</ul>')
    print(json.dumps({k:manifest[k] for k in ('scalars','sequences','total','automatic_records','rendered_glyph_style_cases')}),flush=True)


if __name__ == '__main__':
    main()
