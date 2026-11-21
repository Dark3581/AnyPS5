import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DecompileAt extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (int i = 1; i < args.length; i++) {
            Address entry = toAddr(Long.parseUnsignedLong(args[i].replace("0x", ""), 16));
            Function f = getFunctionAt(entry);
            if (f == null) {
                new DisassembleCommand(entry, null, true).applyTo(currentProgram, monitor);
                new CreateFunctionCmd(entry).applyTo(currentProgram, monitor);
                f = getFunctionAt(entry);
            }
            out.println("//==== " + args[i]);
            if (f == null) { out.println("// no function"); continue; }
            for (Function callee : f.getCalledFunctions(monitor)) {
                if (callee.getBody().getNumAddresses() <= 1) {
                    new DisassembleCommand(callee.getEntryPoint(), null, true).applyTo(currentProgram, monitor);
                }
            }
            DecompileResults r = decomp.decompileFunction(f, 120, monitor);
            out.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// failed: " + r.getErrorMessage());
            out.flush();
        }
        out.close();
    }
}
