import struct, sys, zlib, os
def b2str(bytes):
    return "".join(map(chr, bytes))
    
def r32(data, pos):
    try:
        return struct.unpack('<I', data.encode('latin-1')[pos:pos+4])[0]
    except:
        return struct.unpack('<I', data[pos:pos+4])[0]
        
def insertreplace(data, to_insert, addr):
    try:
        return data[0:addr] + to_insert + data[addr+len(to_insert):]
    except:
        return data[0:addr] + bytes(to_insert, encoding='latin-1') + data[addr+len(to_insert):]

def readbytes(path):
    try:
        return open(path, 'r', encoding='latin-1', newline="").read().encode('latin-1')
    except TypeError:
        return open(path, 'rb').read()
        
rf_sig = b2str([0x02, 0x10, 0xD0, 0xE5, 0x04, 0x00, 0x51, 0xE3, 0x05, 0x00, 0x00, 0x3A, 0x0C, 0x10, 0x90, 0xE5, 0x04, 0x00, 0x90, 0xE5, 0x00, 0x10, 0x41, 0xE0])
rf_alloc_sig = b2str([0x1C, 0x00, 0x90, 0xE5, 0x7F, 0x00, 0x80, 0xE2, 0x7F, 0x10, 0xC0, 0xE3, 0xE8, 0x06, 0x9D, 0xE5])
thread_sig = b2str([0x08, 0xD0, 0x4D, 0xE2, 0x00, 0x60, 0xA0, 0xE1, 0x04, 0x00, 0x92, 0xE5])
decomp_sig = b2str([0xCC, 0xD0, 0x4D, 0xE2, 0x00, 0x40, 0xA0, 0xE1, 0xF0, 0x00, 0x8D, 0xE2])
norm_sig = b2str([0x05, 0x20, 0xA0, 0xE1, 0x07, 0x10, 0xA0, 0xE1, 0x06, 0x00, 0xA0, 0xE1, 0x03, 0x00, 0x00, 0x9A])
sdsound_sig = "%s/snd_bgm_%s.nus3bank"

#Make this compatible with Python 2 and 3
try:
    f = open(sys.argv[1], 'r', encoding='latin-1', newline="").read()
except TypeError:
    f = open(sys.argv[1], 'rb').read()

rf_alloc = readbytes("bin/incalloc.bin")
rf_hook = readbytes("bin/hookresource.bin")   
thread_hook = readbytes("bin/hookthread.bin")
decomp_hook = readbytes("bin/hookdecomp.bin")
norm_hook = readbytes("bin/hooknorm.bin")
rf_payload= readbytes("resource_mod/resource_mod.bin") 
thread_payload = readbytes("bin/threadload.bin")
decomp_payload = readbytes("bin/decompload.bin")
norm_payload = readbytes("bin/normload.bin")
sdsound = readbytes("bin/sdsound.bin")

sdsound_func_addr = f.find(sdsound_sig)-0x4

rf_hook_addr = f.find(rf_sig)
rf_alloc_addr = f.find(rf_alloc_sig)
thread_hook_addr = f.find(thread_sig)
norm_hook_addr = f.find(norm_sig)
decomp_hook_addr = f.find(decomp_sig)

# TODO: Scan for these
rf_payload_addr = 0xA42800-0x100000
thread_payload_addr = 0xA44800-0x100000
decomp_payload_addr = 0xA40800-0x100000
norm_payload_addr = 0xa41000-0x100000
sdsound_addr = 0xA3D800-0x100000

# Just convert f to bytes now that we're done searching things.
try:
    f = f.encode('latin-1')
except:
    f = f

w = open(os.path.splitext(sys.argv[1])[0]+"_saltysd.bin", 'w+b')
f = insertreplace(f,rf_hook,rf_hook_addr)
f = insertreplace(f,rf_alloc,rf_alloc_addr)
f = insertreplace(f,thread_hook,thread_hook_addr)
f = insertreplace(f,decomp_hook,decomp_hook_addr)
f = insertreplace(f,norm_hook,norm_hook_addr)

f = insertreplace(f,rf_payload,rf_payload_addr)
f = insertreplace(f,thread_payload,thread_payload_addr)
f = insertreplace(f,decomp_payload,decomp_payload_addr)
f = insertreplace(f,norm_payload,norm_payload_addr)
f = insertreplace(f,sdsound,sdsound_addr)

# This should be a pointer, if it isn't this is likely a pre-update version or Demo.
if(r32(f,sdsound_func_addr+0x1C) & 0xFF000000 != 0):
    print("This is likely a version of Smash which doesn't utilize update data (1.0.1, Demo)!\nSound override is not supported with these versions.")
    w.write(f)
    exit(0)
    
orig_ptr = r32(f,sdsound_func_addr)
f = insertreplace(f,struct.pack('<I', orig_ptr),sdsound_func_addr+0x1C)
f = insertreplace(f,struct.pack('<I', sdsound_addr+0x100000),sdsound_func_addr)
w.write(f)

