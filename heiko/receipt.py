
import escpos.printer
from escpos.image import EscposImage

### ND77 Printer ###
class ND77:
    ESC = b'\x1b'
    GS = b'\x1d'
    
    def __init__(self):
        self.p = escpos.printer.Serial(devfile="/dev/serial/by-id/usb-FTDI_usb_serial_converter_FTCEYI0H-if00-port0", baudrate=9600)

    def logo(self, fname, align="center"):
        img = EscposImage(fname)

        dat =  bytearray([0]*((img.height//8)*(img.width//8)*8))
        for x in range(0,img.width):
            for y in range(0,img.height):
                if img._im.getpixel((x,y)) > 0:
                    dat[y//8+x*img.height//8] |= 1<<(7-(y%8))

        self.p.set(align=align)  
        self.p._raw(b'\x1bE\x01')
        self.p._raw(b'\x1d*' + bytes([img.width//8, img.height//8]) + bytes(dat))
        self.p._raw(b'\x1d/\x00')       
        
    def feed(self, num):
        self.p._raw(self.ESC + b'd' + bytes([num]))
    
    def cut(self):
        self.p._raw(self.ESC + b'i')
        
    def emph(self, en=True):
        if en:
            self.p._raw(b'\x1bE\x01')
        else:
            self.p._raw(b'\x1bE\x00')
            
    def size(self, doubleHeight, doubleWidth):
        dat = 0
        if doubleHeight:
            dat |= 0x10
        if doubleWidth:
            dat |= 0x20
        self.p._raw(self.ESC + b'!' + bytes([dat]))
        
    def text(self, txt, journal=False):
        if journal:
            self.p._raw(self.ESC + b'c0' + bytes([0x01]))
            self.emph(False)
            self.size(False, False)
            self.p.set(align="left")
        self.p.text(txt)
        if journal:
            self.p._raw(self.ESC + b'c0' + bytes([0x02]))

    def ticket(self, name, nr):
        self.logo("logo.png")
        self.feed(2)
        self.size(True,True)
        self.emph(True)
        self.text(name + "\n\n")
        self.text("#%d\n" % nr)
        self.feed(16)
        self.cut()

    def inlay(self, nr):
        self.p.set(align="center")  
        self.size(True, True)
        self.emph(True)
        self.text("#%d\n" % nr)
        self.feed(0x18)
        self.cut()

def receipt_init():
    global nd77
    nd77 = ND77()

def receipt_journal(text):
    global nd77
    nd77.text(text, journal=True)