
REM provide the remainder of the corresponding division
operation. 

Here is the extracted TableGen code for the REM instruction and its inheritance hierarchy:

// ------ RISCVInstrInfoM.td ------ //
let Predicates = [HasStdExtM] in {
def REM     : ALU_rr<0b0000001, 0b110, "rem">,
              Sched<[WriteIRem, ReadIRem, ReadIRem]>;
} // Predicates = [HasStdExtM]

let Predicates = [HasStdExtM, IsRV64], IsSignExtendingOpW = 1 in {
def REMW    : ALUW_rr<0b0000001, 0b110, "remw">,
              Sched<[WriteIRem32, ReadIRem32, ReadIRem32]>;
} // Predicates = [HasStdExtM, IsRV64]

// ------ RISCVInstrFormats.td ------ //
let hasSideEffects = 0, mayLoad = 0, mayStore = 0 in
class ALU_rr<bits<7> funct7, bits<3> funct3, string opcodestr,
            bit Commutable = 0>
    : RVInstR<funct7, funct3, OPC_OP, (outs GPR:$rd), (ins GPR:$rs1, GPR:$rs2),
            opcodestr, "$rd, $rs1, $rs2"> {
let isCommutable = Commutable;
}

class RVInstR<bits<7> funct7, bits<3> funct3, RISCVOpcode opcode, dag outs,
            dag ins, string opcodestr, string argstr>
    : RVInstRBase<funct3, opcode, outs, ins, opcodestr, argstr> {
let Inst{31-25} = funct7;
}

class RVInstRBase<bits<3> funct3, RISCVOpcode opcode, dag outs,
                dag ins, string opcodestr, string argstr>
    : RVInst<outs, ins, opcodestr, argstr, [], InstFormatR> {
bits<5> rs2;
bits<5> rs1;
bits<5> rd;

let Inst{24-20} = rs2;
let Inst{19-15} = rs1;
let Inst{14-12} = funct3;
let Inst{11-7} = rd;
let Inst{6-0} = opcode.Value;
}

class RVInst<dag outs, dag ins, string opcodestr, string argstr,
             list<dag> pattern, InstFormat format>
    : RVInstCommon<outs, ins, opcodestr, argstr, pattern, format> {
  field bits<32> Inst;
  field bits<32> SoftFail = 0;
  let Size = 4;
}

class RVInstCommon<dag outs, dag ins, string opcodestr, string argstr,
                   list<dag> pattern, InstFormat format> : Instruction {
  let Namespace = "RISCV";

  dag OutOperandList = outs;
  dag InOperandList = ins;
  let AsmString = opcodestr # !if(!empty(argstr), "", "	" # argstr);
  let Pattern = pattern;

  let TSFlags{4-0} = format.Value;

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

  bit IsSignExtendingOpW = 0;
  let TSFlags{18} = IsSignExtendingOpW;

  bit HasRoundModeOp = 0;
  let TSFlags{19} =  HasRoundModeOp;

  bit UsesVXRM = 0;
  let TSFlags{20} =  UsesVXRM;

  bits<2> TargetOverlapConstraintType = 0;
  let TSFlags{22-21} = TargetOverlapConstraintType;
}