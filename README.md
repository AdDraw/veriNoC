# VeriNoC

![example workflow](https://github.com/AdDraw/magiament/actions/workflows/blank.yml/badge.svg)

## Master Thesis 2020/2022 Network on Chip

---
> results are kept in the `results` directory

This repo holds my attempts at implementing Network on Chips.\
Started as a simple Mesh NoC with Flow control based on 1 phit buffers and not packet splitting and XY routing.

**Topologies**:

- MESH

**Flow controls** supported:

- Store & Forward but only with 1 phit long packets
- Wormhole with N flit long packets

**Arbitration:**

- matrix based (strong)

**Routing algorithms** supported:

- dimension-routing(XY)

---

## Assumptions

- **Verilog** as a main hdl language
- **Verilator/IcarusVerilog + cocotb + gtkwave** used as a sim tool
- **Yosys** as a synth tool
- **SymbiYosys** as a formal verification tool
- Scripts should be written in Bash/Python/Tcl
- Verilator should be at least `v4.022` to work with cocotb
- IcarusVerilog has to be of version greater than `11.0`

> Cocotb Verilator support is experimental so for now it's not supported

## Directory format

- **docs** for documents
  - for now no specified subdirectories
- **srcs** for hdl files
  - files from different projects in the same directory
- **sim** for simulation files
  - **formal**
    - SymbiYosys scripts
  - **functional**
    - Cocotb Testbenches
    - each design with it's own subdir
- **synth** for synthesis scripts(in `.tcl`) and results

## Editor Setup

> Currenly I'm mostly using VSCode

- **Teros HDL** by Teros Technology (I like it a lot)(<https://terostechnology.github.io>)
- **Python** by Microsoft
- **json** by ZainChen (<https://github.com/ZainChen/vscode-json>)
- **Markdown All in One** by Yu Zhang

### Optionally

Atom editor. For syntax highlighting the following packages can be used:

- language-vhdl
- language-verilog
(both by Razer6)
For Python it is best to use PyCharm with Atom(for HDL), or just Atom for both
