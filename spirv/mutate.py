import struct, sys
src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
b = open(src, 'rb').read()
i = b.find(struct.pack('<I', 0x07230203)); n = struct.unpack_from('<I', b, i - 4)[0]
w = struct.unpack_from('<%dI' % n, b, i)
out = list(w[:5]); j = 5; dropped = 0
while j < len(w):
    k = w[j] >> 16; op = w[j] & 0xffff; ins = list(w[j:j + k]); j += k
    if mode == 'nocontraction' and op == 71 and k == 3 and ins[2] == 42: dropped += 1; continue
    if mode == 'switch1' and op == 251 and k > 5: ins = [(5 << 16) | 251] + ins[1:5]; dropped += 1
    out += ins
import os; os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, 'wb').write(b[:i - 4] + struct.pack('<I', len(out)) + struct.pack('<%dI' % len(out), *out) + b[i + 4 * n:])
print(mode, 'changed', dropped, 'words', n, '->', len(out))
