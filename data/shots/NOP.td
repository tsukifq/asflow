// ------ RISCVInstrInfo.td ------ //
def : InstAlias<"nop", (ADDI X0, X0, 0)>;