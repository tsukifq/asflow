Here is the extracted TableGen code for the VMUL_VX instruction and its inheritance hierarchy:

// ------ RISCVInstrInfoV.td ------ //
class VALUVX<bits<6> funct6, RISCVVFormat opv, string opcodestr>
    : RVInstVX<funct6, opv, (outs VR:$vd),
                (ins VR:$vs2, GPR:$rs1, VMaskOp:$vm),
                opcodestr, "$vd, $vs2, $rs1$vm">;

multiclass VALU_IV_X<string opcodestr, bits<6> funct6> {
  def X  : VALUVX<funct6, OPIVX, opcodestr # ".vx">,
           SchedBinaryMC<"WriteVIALUX", "ReadVIALUV", "ReadVIALUX">;
}

multiclass VMUL_MV_V_X<string opcodestr, bits<6> funct6> {
  def V  : VALUVV<funct6, OPMVV, opcodestr # ".vv">,
           SchedBinaryMC<"WriteVIMulV", "ReadVIMulV", "ReadVIMulV">;
  def X  : VALUVX<funct6, OPMVX, opcodestr # ".vx">,
           SchedBinaryMC<"WriteVIMulX", "ReadVIMulV", "ReadVIMulX">;
}

defm VMUL_V : VMUL_MV_V_X<"vmul", 0b100101>;

// ------ RISCVInstrFormatsV.td ------ //
class RVInstVX<bits<6> funct6, RISCVVFormat opv, dag outs, dag ins,
                string opcodestr, string argstr>
    : RVInst<outs, ins, opcodestr, argstr, [], InstFormatR> {
  bits<5> vs2;
  bits<5> rs1;
  bits<5> vd;
  bit vm;

  let Inst{31-26} = funct6;
  let Inst{25} = vm;
  let Inst{24-20} = vs2;
  let Inst{19-15} = rs1;
  let Inst{14-12} = opv.Value;
  let Inst{11-7} = vd;
  let Inst{6-0} = OPC_OP_V.Value;

  let Uses = [VTYPE, VL];
  let RVVConstraint = VMConstraint;
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