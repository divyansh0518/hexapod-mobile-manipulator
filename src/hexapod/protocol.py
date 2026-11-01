"""Explicit little-endian framing; matches firmware without platform-sized ints."""
import struct
import binascii
import numpy as np
HEADER=struct.Struct("<2sBBH24H")
FRAME_SIZE=HEADER.size+2

def encode(angles, seq=0, armed=False, stop=False):
    a=np.asarray(angles,dtype=float)
    if a.shape!=(24,) or not np.all(np.isfinite(a)) or np.any(a<0) or np.any(a>180):
        raise ValueError("24 finite servo angles in [0,180] required")
    raw=HEADER.pack(b"HX",1,int(armed)|(int(stop)<<1),seq%65536,*np.rint(a*10).astype(int))
    return raw+struct.pack("<H",binascii.crc_hqx(raw,0xffff))

def decode(data):
    if len(data)!=FRAME_SIZE: raise ValueError("Bad frame length")
    raw,crc=data[:-2],struct.unpack("<H",data[-2:])[0]
    if binascii.crc_hqx(raw,0xffff)!=crc: raise ValueError("Bad CRC")
    magic,version,flags,seq,*values=HEADER.unpack(raw)
    if magic!=b"HX" or version!=1 or flags&~3 or any(v>1800 for v in values): raise ValueError("Invalid frame")
    return {"seq":seq,"armed":bool(flags&1),"stop":bool(flags&2),"angles":np.array(values)/10}
