pure_system_prompt = """
You are a helpful assistant. You will follow the user's instructions to complete the task.
"""

instr_formatting_prompt = """
You are tasked to convert the following custom extended instruction description into a standardized instruction format.
Please follow the format guidelines below:
1. The instruction should be in the following format:
The instruction should be in the following format:
{{
    name: <name of the instruction>,
    description: <description of the instruction>,
    syntax: <syntax of the instruction>,
    operation: <operation of the instruction>,
    arguments: <arguments of the instruction>,
    encodings: <encodings of the instruction>,
    classification: <classification of the instruction>,
    examples: <examples of the instruction>
}}
2. Ensure that the instruction is correctly formatted and all the fields are filled.
3. Pay attention to the classification of the instruction. You only need to tell if it is a base instruction, an extension instruction, or a custom instruction. For extension and custom instructions, specify the extension name.
{task}
"""
            
tablegen_extraction_prompt = """
You are tasked with extracting the implementation of the following instruction and all its inheretent classes from the LLVM RISC-V TableGen code.
Let's do it step by step:
1. Focus only on the specific instruction named in the provided information. Do not extract information for similar or related instructions.
2. Extract the instruction's definition TableGen code in the TableGen files provided.
3. Extract the class of instruction's definition, its parent class, parent's parent class, and so on up the inheritance hierarchy.
Please observe the principles below: 
1. Only output TableGen code.
2. Do not include any other information or comments in the output.
2. Add the filename before the TableGen code in this format: // ------ RISCV.td ------ //.
3. Pay attention to the code structure and indentation. Ensure the extracted code is complete and accurate.
4. Only use the provided TableGen files to extract the code.
Here is an example to guide you:
** example **
Information of the target instruction:
name: add
description: ADD adds two registers and places the result in a third register.

The TableGen code you need to extract:
// ------ RISCVInstrInfo.td ------ //
def ADD  : ALU_rr<0b0000000, 0b000, "add", Commutable=1>,
           Sched<[WriteIALU, ReadIALU, ReadIALU]>;

let hasSideEffects = 0, mayLoad = 0, mayStore = 0 in
class ALU_rr<bits<7> funct7, bits<3> funct3, string opcodestr,
            bit Commutable = 0>
    : RVInstR<funct7, funct3, OPC_OP, (outs GPR:$rd), (ins GPR:$rs1, GPR:$rs2),
            opcodestr, "$rd, $rs1, $rs2"> {{
let isCommutable = Commutable;
}}

// ------ RISCVInstrFormats.td ------ //
class RVInstR<bits<7> funct7, bits<3> funct3, RISCVOpcode opcode, dag outs,
            dag ins, string opcodestr, string argstr>
    : RVInstRBase<funct3, opcode, outs, ins, opcodestr, argstr> {{
let Inst{{31-25}} = funct7;
}}

class RVInstRBase<bits<3> funct3, RISCVOpcode opcode, dag outs,
                dag ins, string opcodestr, string argstr>
    : RVInst<outs, ins, opcodestr, argstr, [], InstFormatR> {{
bits<5> rs2;
bits<5> rs1;
bits<5> rd;

let Inst{{24-20}} = rs2;
let Inst{{19-15}} = rs1;
let Inst{{14-12}} = funct3;
let Inst{{11-7}} = rd;
let Inst{{6-0}} = opcode.Value;
}}

class RVInst<dag outs, dag ins, string opcodestr, string argstr,
             list<dag> pattern, InstFormat format>
    : RVInstCommon<outs, ins, opcodestr, argstr, pattern, format> {{
  field bits<32> Inst;
  // SoftFail is a field the disassembler can use to provide a way for
  // instructions to not match without killing the whole decode process. It is
  // mainly used for ARM, but Tablegen expects this field to exist or it fails
  // to build the decode table.
  field bits<32> SoftFail = 0;
  let Size = 4;
}}

class RVInstCommon<dag outs, dag ins, string opcodestr, string argstr,
                   list<dag> pattern, InstFormat format> : Instruction {{
  let Namespace = "RISCV";

  dag OutOperandList = outs;
  dag InOperandList = ins;
  let AsmString = opcodestr # !if(!empty(argstr), "", "\t" # argstr);
  let Pattern = pattern;

  let TSFlags{{4-0}} = format.Value;

  // Defaults
  RISCVVConstraint RVVConstraint = NoConstraint;
  let TSFlags{{7-5}} = RVVConstraint.Value;

  bits<3> VLMul = 0;
  let TSFlags{{10-8}} = VLMul;

  bit ForceTailAgnostic = false;
  let TSFlags{{11}} = ForceTailAgnostic;

  bit IsTiedPseudo = 0;
  let TSFlags{{12}} = IsTiedPseudo;

  bit HasSEWOp = 0;
  let TSFlags{{13}} = HasSEWOp;

  bit HasVLOp = 0;
  let TSFlags{{14}} = HasVLOp;

  bit HasVecPolicyOp = 0;
  let TSFlags{{15}} = HasVecPolicyOp;

  bit IsRVVWideningReduction = 0;
  let TSFlags{{16}} = IsRVVWideningReduction;

  bit UsesMaskPolicy = 0;
  let TSFlags{{17}} = UsesMaskPolicy;

  // Indicates that the result can be considered sign extended from bit 31. Some
  // instructions with this flag aren't W instructions, but are either sign
  // extended from a smaller size, always outputs a small integer, or put zeros
  // in bits 63:31. Used by the SExtWRemoval pass.
  bit IsSignExtendingOpW = 0;
  let TSFlags{{18}} = IsSignExtendingOpW;

  bit HasRoundModeOp = 0;
  let TSFlags{{19}} =  HasRoundModeOp;

  // This is only valid when HasRoundModeOp is set to 1. HasRoundModeOp is set
  // to 1 for vector fixed-point or floating-point intrinsics. This bit is
  // processed under pass 'RISCVInsertReadWriteCSR' pass to distinguish between
  // fixed-point / floating-point instructions and emit appropriate read/write
  // to the correct CSR.
  bit UsesVXRM = 0;
  let TSFlags{{20}} =  UsesVXRM;

  // Indicates whther these instructions can partially overlap between source
  // registers and destination registers according to the vector spec.
  // 0 -> not a vector pseudo
  // 1 -> default value for vector pseudos. not widening or narrowing.
  // 2 -> narrowing case
  // 3 -> widening case
  bits<2> TargetOverlapConstraintType = 0;
  let TSFlags{{22-21}} = TargetOverlapConstraintType;
}}
** end of example **
This is the name and description of the target instruction:
{instr.name}
{instr.description}
The following is LLVM RISC-V TableGen code:
{file_content}
"""

files_searching_prompt = """
You are provided with a set of TableGen file names from the LLVM RISC-V backend and information about a target RISC-V instruction. 
Your task is to choose relevant files that contain instruction encoding and formats about the target instruction from the set. 
Critically evaluate the provided file names and generate a refined output.
Please observe the principles below:
1. Only output the names of the relevant files.
2. Do not include any other information or comments in the output.
3. Pay attention to the file names and ensure the extracted names are complete and accurate.
4. Add file RISCVInstrInfo.td and RISCVInstrFormats.td to the output.
The following is the list of TableGen files:
{files}
This is the description of target instruction:
{instr}
"""

shots_searching_prompt = """
You are provided with a set of file names. These files contain the implementation of RISC-V instructions and their related classes in the LLVM RISC-V TableGen code.
Your task is to choose 3 files that containe the implementation of instructions that are similar to the target instruction.
Please observe the principles below:
1. Only output the names of the relevant files.
2. Do not include any other information or comments in the output.
3. Pay attention to the file names and ensure the extracted names are complete and accurate.
The following is the list of TableGen files:
{shots}
This is the description of target instruction:
{instr}
"""

tablegen_generating_prompt = """
You are provided with the description of a custom-defined RISC-V instruction, the current relative TableGen files content, and the TableGen code of similar instructions.
Your task is to generate the TableGen code for the custom-defined instruction.
Please observe the principles below:
1. Only output TableGen code.
2. Do not include any other information or comments in the output.
3. Pay attention to the code structure and indentation. Ensure the generated code is complete and accurate.
The following is the description of the custom-defined instruction:
{instr}
The following is the current relative TableGen files content, you should add the generated code to the files:
{file_content}
The following is the TableGen code of similar instructions:
{similar_instr}
"""

