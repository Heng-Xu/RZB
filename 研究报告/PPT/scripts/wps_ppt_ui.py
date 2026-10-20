"""Small X11 driver for the isolated PPT preview display; never targets the report desktop."""
import argparse,ctypes,os,time
from PIL import ImageGrab
p=argparse.ArgumentParser();p.add_argument('actions',nargs='*');a=p.parse_args()
display=os.environ.get('DISPLAY',':139')
if display!=':139':raise RuntimeError('This task helper only operates on display :139')
X=ctypes.CDLL('libX11.so.6');T=ctypes.CDLL('libXtst.so.6')
X.XOpenDisplay.argtypes=[ctypes.c_char_p];X.XOpenDisplay.restype=ctypes.c_void_p;d=X.XOpenDisplay(display.encode());assert d
X.XStringToKeysym.argtypes=[ctypes.c_char_p];X.XStringToKeysym.restype=ctypes.c_ulong
X.XKeysymToKeycode.argtypes=[ctypes.c_void_p,ctypes.c_ulong];X.XKeysymToKeycode.restype=ctypes.c_uint
X.XFlush.argtypes=[ctypes.c_void_p];T.XTestFakeKeyEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
T.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong];T.XTestFakeButtonEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]
def key(k,down):T.XTestFakeKeyEvent(d,X.XKeysymToKeycode(d,X.XStringToKeysym(k.encode())),down,0);X.XFlush(d)
def chord(s):
    ks=s.split('+')
    for k in ks:key(k,1)
    for k in ks[::-1]:key(k,0)
    time.sleep(.25)
def text(s):
    for ch in s:
        if not ch.isascii():raise ValueError('Use ASCII output aliases')
        shift=ch.isupper() or ch in '_:'
        if shift:key('Shift_L',1)
        k={'/':'slash','.':'period','_':'minus',':':'semicolon','-':'minus',' ':'space'}.get(ch,ch.lower());key(k,1);key(k,0)
        if shift:key('Shift_L',0)
    time.sleep(.2)
for s in a.actions:
    if s.startswith('key='):chord(s[4:])
    elif s.startswith('text='):text(s[5:])
    elif s.startswith('wait='):time.sleep(min(float(s[5:]),30))
    elif s.startswith('shot='):ImageGrab.grab(xdisplay=display).save(s[5:])
    elif s.startswith('click='):
        x,y=map(int,s[6:].split(','));T.XTestFakeMotionEvent(d,-1,x,y,0);T.XTestFakeButtonEvent(d,1,1,0);T.XTestFakeButtonEvent(d,1,0,0);X.XFlush(d);time.sleep(.3)
