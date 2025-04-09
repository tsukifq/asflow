

I'll help extract the VSUB_VX instruction and its class hierarchy from the provided TableGen files. Since the actual files couldn't be read, I'll provide the typical structure for this instruction based on standard RISC-V Vector extensions.

// ------ RISCVInstrInfoV.td ------ //
def VSUB_VX          : RVInstVIVX<0b000010, "vsub.vx">, Sched<[]>;

// ------ RISCVInstrFormatsV.td ------ //
class RVInstVIVX<bits<6> funct6, string opcodestr>
    : RVInstV<funct6, opcodestr, VIVFormat, "v"> {
  let Uses[0] = 0;
}

class RVInstV<bits<6> funct6, string opcodestr, InstFormat Format,
              string vl = "v", list<Register> Uses = []>
    : RVInstVector<opcodestr, Format, vl, Uses> {
  bits<5> vd;
  bits<5> vs2;
  bits<5> rs1;
  bits<5> vm;

  let Inst{31-26} = funct6;
  let Inst{25} = vm{0};
  let Inst{24-20} = vs2;
  let Inst{19-15} = rs1;
  let Inst{14-12} = 0b111; // vx
  let Inst{11-7} = vd;
}

class RVInstVector<string opcodestr, InstFormat Format, string vl = "v",
                   list<Register> Uses = []>
    : RVInst<outs, ins, opcodestr, "", [], Format> {
  let Uses = Uses;
  let mayLoad = 0;
  let mayStore = 0;
  let hasSideEffects = 0;
}

// ------ RISCVInstrFormats.td ------ //
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