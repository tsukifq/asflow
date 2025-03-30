
Load and store instructions transfer a value between the registers and memory. Loads are encoded in
the I-type format and stores are S-type. The effective address is obtained by adding register rs1 to the
sign-extended 12-bit offset. Loads copy a value from memory to register rd. Stores copy the value in
register rs2 to memory. LHU loads a 16-bit value from memory but then zero extends to 32-bits before storing in rd.

Here is the extracted TableGen code for the `LHU` instruction:

```tablegen
// ------ RISCVInstrInfo.td ------ //
let IsSignExtendingOpW = 1 in {
def LHU : Load_ri<0b101, "lhu">, Sched<[WriteLDH, ReadMemBase]>;
}

let hasSideEffects = 0, mayLoad = 1, mayStore = 0 in {
    class Load_ri<bits<3> funct3, string opcodestr>
        : RVInstI<funct3, OPC_LOAD, (outs GPR:$rd), (ins GPRMem:$rs1, simm12:$imm12),
                  opcodestr, "$rd, ${imm12}(${rs1})">;
}

// ------ RISCVInstrFormats.td ------ //
class RVInstI<bits<3> funct3, RISCVOpcode opcode, dag outs, dag ins,
              string opcodestr, string argstr>
    : RVInstIBase<funct3, opcode, outs, ins, opcodestr, argstr> {
  bits<12> imm12;

  let Inst{31-20} = imm12;
}

class RVInstIBase<bits<3> funct3, RISCVOpcode opcode, dag outs, dag ins,
                  string opcodestr, string argstr>
    : RVInst<outs, ins, opcodestr, argstr, [], InstFormatI> {
  bits<5> rs1;
  bits<5> rd;

  let Inst{19-15} = rs1;
  let Inst{14-12} = funct3;
  let Inst{11-7} = rd;
  let Inst{6-0} = opcode.Value;
}

class RVInst<dag outs, dag ins, string opcodestr, string argstr,
             list<dag> pattern, InstFormat format>
    : RVInstCommon<outs, ins, opcodestr, argstr, pattern, format> {
  field bits<32> Inst;
  // SoftFail is a field the disassembler can use to provide a way for
  // instructions to not match without killing the whole decode process. It is
  // mainly used for ARM, but Tablegen expects this field to exist or it fails
  // to build the decode table.
  field bits<32> SoftFail = 0;
  let Size = 4;
}

class RVInstCommon<dag outs, dag ins, string opcodestr, string argstr,
                   list<dag> pattern, InstFormat format> : Instruction {
  let Namespace = "RISCV";

  dag OutOperandList = outs;
  dag InOperandList = ins;
  let AsmString = opcodestr # !if(!empty(argstr), "", "\t" # argstr);
  let Pattern = pattern;

  let TSFlags{4-0} = format.Value;

  // Defaults
  RISCVVConstraint RVVConstraint = NoConstraint;
  let TSFlags{7-5} = RVVConstraint.Value;

  bits<3> VLMul = 0;
  let TSFlags{10-8} = VLMul;

  bit ForceTailAgnostic = false;
  let TSFlags{11} = ForceTailAgnostic;

  bit IsTiedPseudo = 0;
  let TSFlags{12} = IsTiedPseudo;

  bit HasSEWOp = 0;
  let TSFlags{13} = HasSEWOp;

  bit HasVLOp = 0;
  let TSFlags{14} = HasVLOp;

  bit HasVecPolicyOp = 0;
  let TSFlags{15} = HasVecPolicyOp;

  bit IsRVVWideningReduction = 0;
  let TSFlags{16} = IsRVVWideningReduction;

  bit UsesMaskPolicy = 0;
  let TSFlags{17} = UsesMaskPolicy;

  // Indicates that the result can be considered sign extended from bit 31. Some
  // instructions with this flag aren't W instructions, but are either sign
  // extended from a smaller size, always outputs a small integer, or put zeros
  // in bits 63:31. Used by the SExtWRemoval pass.
  bit IsSignExtendingOpW = 0;
  let TSFlags{18} = IsSignExtendingOpW;

  bit HasRoundModeOp = 0;
  let TSFlags{19} =  HasRoundModeOp;

  // This is only valid when HasRoundModeOp is set to 1. HasRoundModeOp is set
  // to 1 for vector fixed-point or floating-point intrinsics. This bit is
  // processed under pass 'RISCVInsertReadWriteCSR' pass to distinguish between
  // fixed-point / floating-point instructions and emit appropriate read/write
  // to the correct CSR.
  bit UsesVXRM = 0;
  let TSFlags{20} =  UsesVXRM;

  // Indicates whther these instructions can partially overlap between source
  // registers and destination registers according to the vector spec.
  // 0 -> not a vector pseudo
  // 1 -> default value for vector pseudos. not widening or narrowing.
  // 2 -> narrowing case
  // 3 -> widening case
  bits<2> TargetOverlapConstraintType = 0;
  let TSFlags{22-21} = TargetOverlapConstraintType;
}
```

This code includes the definition of the `LHU` instruction and its parent classes up the inheritance hierarchy. The `LHU` instruction is defined in the `RISCVInstrInfo.td` file, and its parent classes are defined in `RISCVInstrFormats.td`. The `LHU` instruction is part of the I-type format and is used to load a 16-bit value from memory and zero-extend it to 32 bits before storing it in the destination register.