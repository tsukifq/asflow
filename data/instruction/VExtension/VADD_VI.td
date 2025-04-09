

Here is the extracted TableGen code for the VADD_VI instruction and its inheritance hierarchy:

```tablegen
// ------ RISCVInstrInfoV.td ------ //
class VALUVI<bits<6> funct6, string opcodestr, Operand optype = simm5>
    : RVInstIVI<funct6, (outs VR:$vd),
                (ins VR:$vs2, optype:$imm, VMaskOp:$vm),
                opcodestr, "$vd, $vs2, $imm$vm">;

multiclass VALU_IV_I<string opcodestr, bits<6> funct6> {
  def I  : VALUVI<funct6, opcodestr # ".vi">,
           SchedUnaryMC<"WriteVIALUI", "ReadVIALUV">;
}

multiclass VALU_IV_V_X_I<string opcodestr, bits<6> funct6>
    : VALU_IV_V<opcodestr, funct6>,
      VALU_IV_X<opcodestr, funct6>,
      VALU_IV_I<opcodestr, funct6>;

defm VADD_V : VALU_IV_V_X_I<"vadd", 0b000000>;
```

The inheritance hierarchy is:
1. `VADD_VI` is defined in the `VALU_IV_I` multiclass
2. `VALU_IV_I` inherits from `VALUVI` class
3. `VALUVI` inherits from `RVInstIVI` class
4. `RVInstIVI` inherits from `RVInst` class (defined in RISCVInstrFormats.td)

The key components are:
- The `VADD_VI` instruction is generated through the `VALU_IV_I` multiclass
- It uses the `VALUVI` template class which defines the basic structure for vector immediate instructions
- The scheduling information is provided via `SchedUnaryMC`
- The instruction format is `RVInstIVI` which handles the immediate encoding