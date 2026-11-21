import struct, sys, collections
w = open(sys.argv[1], 'rb').read()
words = struct.unpack('<%dI' % (len(w) // 4), w)
names = {1:'OpUndef',5:'OpName',43:'OpConstant',44:'OpConstantComposite',54:'OpFunction',55:'OpFunctionParameter',56:'OpFunctionEnd',57:'OpFunctionCall',59:'OpVariable',61:'OpLoad',62:'OpStore',65:'OpAccessChain',71:'OpDecorate',79:'OpVectorShuffle',80:'OpCompositeConstruct',81:'OpCompositeExtract',82:'OpCompositeInsert',95:'OpImageSampleImplicitLod',87:'OpSampledImage',98:'OpImageSampleExplicitLod',96:'OpImageFetch',98:'OpImageFetch?',124:'OpBitcast',128:'OpIAdd',130:'OpISub',132:'OpIMul',129:'OpFAdd',133:'OpFMul',137:'OpUDiv',151:'OpFMod',170:'OpIEqual',171:'OpINotEqual',172:'OpUGreaterThan',176:'OpULessThan',180:'OpFOrdEqual',169:'OpSelect',194:'OpShiftRightLogical',196:'OpShiftLeftLogical',197:'OpBitwiseOr',199:'OpBitwiseAnd',198:'OpBitwiseXor',200:'OpNot',201:'OpBitFieldInsert',202:'OpBitFieldSExtract',203:'OpBitFieldUExtract',245:'OpPhi',246:'OpLoopMerge',247:'OpSelectionMerge',248:'OpLabel',249:'OpBranch',250:'OpBranchConditional',251:'OpSwitch',253:'OpReturn',254:'OpReturnValue',12:'OpExtInst',95:'OpImageRead?',98:'OpImageRead',99:'OpImageWrite',100:'OpImage',104:'OpImageQuerySize',227:'OpAtomicIAdd',229:'OpAtomicCompareExchange',234:'OpAtomicOr',366:'OpGroupNonUniformBallot',338:'OpGroupNonUniformElect',345:'OpGroupNonUniformBroadcast',346:'OpGroupNonUniformBroadcastFirst',224:'OpControlBarrier',225:'OpMemoryBarrier',124:'OpBitcast',112:'OpConvertUToF',109:'OpConvertFToU',110:'OpConvertFToS',111:'OpConvertSToF',113:'OpUConvert',114:'OpSConvert',115:'OpFConvert',4472:'OpGroupNonUniform?'}
i = 5; cnt = collections.Counter(); wc = collections.Counter(); funcs = []; cur = None
while i < len(words):
    op = words[i] & 0xffff; n = words[i] >> 16
    if n == 0: break
    cnt[op] += 1; wc[op] += n
    if op == 54: cur = [words[i + 2], 0, 0]
    if cur is not None: cur[1] += n; cur[2] += (op == 57)
    if op == 56 and cur: funcs.append(tuple(cur)); cur = None
    i += n
tot = len(words)
print("total words", tot, "functions", len(funcs))
for op, c in wc.most_common(25): print("%-28s %8d words %6.1f%%  %7d instrs" % (names.get(op, str(op)), c, 100 * c / tot, cnt[op]))
print("largest functions (id, words, calls):", sorted(funcs, key=lambda f: -f[1])[:8])
