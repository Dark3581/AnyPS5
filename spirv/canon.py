import struct, sys
def load(d):
    b=open(d+'/capture.aps5cp','rb').read()
    i=b.find(struct.pack('<I',0x07230203)); n=struct.unpack_from('<I',b,i-4)[0]
    w=struct.unpack_from('<%dI'%n,b,i); ins=[]; j=5
    while j<len(w):
        k=w[j]>>16; ins.append(list(w[j:j+k])); j+=k
    return ins
# result id position per opcode (simplified): ops with result type+result: id at [2]; ops with only result: [1]
RES1={19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,248,11,8,5}
def canon(ins):
    m={}; out=[]
    def mp(x):
        if x not in m: m[x]=len(m)+1
        return m[x]
    for t in ins:
        op=t[0]&0xffff
        if op in (5,6,71,72): out.append(None); continue
        out.append(t)
    # second pass: map all operand words that look like ids by order of appearance (heuristic: map every word > 0 that is < bound in operand positions)
    return out
a=load(sys.argv[1]); b=load(sys.argv[2])
fa=[t for t in a if (t[0]&0xffff) not in (5,6,71,72)]; fb=[t for t in b if (t[0]&0xffff) not in (5,6,71,72)]
print('non-debug/decor instrs', len(fa), len(fb))
from collections import Counter
ca=Counter(t[0] for t in fa); cb=Counter(t[0] for t in fb)
diff={k:(ca[k],cb[k]) for k in set(ca)|set(cb) if ca[k]!=cb[k]}
print('opcode/len count diffs:', {('op%d/len%d'%(k&0xffff,k>>16)):v for k,v in list(diff.items())[:30]})
