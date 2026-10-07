"""Lightweight SJPB v1 reader: NumPy only, no fontTools/OpenCV build runtime.

See docs/FAMILY.md for the little-endian binary format. Text identity is
preserved; lookup is longest-match and never normalizes compatibility Kanji.
"""
from pathlib import Path
import struct
import numpy as np

HEADER=struct.Struct('<4sHHIIIIII')
INDEX=struct.Struct('<IIHHhhhHII')


class BitmapFont:
    def __init__(self,path):
        self.data=Path(path).read_bytes()
        magic,version,flags,count,self.size,index,keys,pixels,self.baseline=HEADER.unpack_from(self.data)
        if (magic,version,flags)!=(b'SJPB',1,0):raise ValueError('Unsupported SJPB header')
        if not count or not self.size:raise ValueError('Empty SJPB font or invalid size')
        if not HEADER.size<=index<=keys<=pixels<=len(self.data):raise ValueError('Invalid SJPB offsets')
        if index+count*INDEX.size>keys:raise ValueError('Overlapping SJPB tables')
        self.glyphs={}
        for i in range(count):
            ko,kl,w,h,a,bx,by,fl,po,pl=INDEX.unpack_from(self.data,index+i*INDEX.size)
            if fl or not kl or not w or not h or a<0:raise ValueError('Invalid SJPB record')
            if keys+ko+kl>pixels or pixels+po+pl>len(self.data):raise ValueError('Truncated SJPB glyph')
            if pl!=((w+7)//8)*h:raise ValueError('Invalid SJPB bitmap length')
            c=self.data[keys+ko:keys+ko+kl].decode('utf-8')
            if c in self.glyphs:raise ValueError('Duplicate SJPB key')
            self.glyphs[c]=(w,h,a,bx,by,pixels+po,pl)
        self.max_sequence=max(map(len,self.glyphs))
        if self.baseline<max(g[4] for g in self.glyphs.values()):raise ValueError('Invalid SJPB baseline')
        self.height=max(self.baseline-g[4]+g[1] for g in self.glyphs.values())
        self.line_height=self.height

    def bitmap(self,text):
        w,h,a,bx,by,po,pl=self.glyphs[text]
        packed=np.frombuffer(self.data[po:po+pl],dtype=np.uint8).reshape(h,(w+7)//8)
        return np.unpackbits(packed,axis=1,bitorder='big')[:,:w].astype(bool)

    def units(self,text):
        i=0
        while i<len(text):
            for n in range(min(self.max_sequence,len(text)-i),0,-1):
                key=text[i:i+n]
                if key in self.glyphs:yield key;i+=n;break
            else:raise KeyError(f'Missing glyph U+{ord(text[i]):04X}')

    def mask(self,text):
        units=list(self.units(text))
        positions=[];pen=0
        for c in units:positions.append((c,pen));pen+=self.glyphs[c][2]
        # Position actual bitmap frames with both horizontal and vertical
        # bearings. Extra crop guards must not shift the writing baseline.
        left=min([0]+[x+self.glyphs[c][3] for c,x in positions])
        right=max([1,pen]+[x+self.glyphs[c][3]+self.glyphs[c][0] for c,x in positions])
        result=np.zeros((self.height,right-left),bool)
        for c,pen in positions:
            w,h,a,bx,by,_,_=self.glyphs[c];x=pen+bx-left;y=self.baseline-by
            result[y:y+h,x:x+w]|=self.bitmap(c)
        return result
