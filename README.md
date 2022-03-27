## VeriNoC
![example workflow](https://github.com/AdDraw/magiament/actions/workflows/blank.yml/badge.svg)
### Master Thesis 2020/2022 Network on Chip

---
> results are kept in the `results` directory

---
## Assumptions:
- **Verilog** as a main hdl language
- **Verilator/IcarusVerilog + cocotb + gtkwave** used as a sim tool
- **Yosys** as a synth tool
- **SymbiYosys** as a formal verification tool
- Scripts should be written in Bash/Python/Tcl
- Verilator should be at least `v4.022` to work with cocotb
- IcarusVerilog has to be of version `11.0`

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

## Verilog codestyle
The Codestyle that will be used is straight from Freescale's Verilog Codestyle.
Everything other than code that is specified there will be ommitted.
Additionally these changes should be implemented to Freescale's Codestyle:

#### Linter
It's suggested that we use ***Verilator as our linter for Verilog RTL***.\
It can be used both inline and integerated into a code editor(like Atom).\
Verilator has many configuration option, many checks, rigorous but it's possible to selectively disable warnings with inline comments.  
Verilator with `-Wall` switch seems to catch quite a nice share of potential issues.

#### Files:
- At most 1 module per file
- names should be meaningful
  - name.v has the rtl of the module
  - name_task/function/defines.v for the files that are used by a module
- Header ( w/copyright warning) should be present in every code and constraints file, **it should contain**:
  - Short description about the module that specifies the key features/modes/functionality
  - Keyword section with Abbreviation descriptions

#### Comments:
 - Comments are required to describe the functionality of HDL code. In particular, comments must supply context information that is not seen locally.

#### Signal Naming:
- The only **snake_case_naming** is used. Ex: few_words_as_1_var.
- Signals declaration **[MSB : LSB]**
- Use useful short names - **signal_purpose instead of a, b, c | cnt instead of counter**
- Clocks should have `clk_` or `_clk` in them
- Abbreviations must be documented  in the Keyword Section of the Header e.g. `GALS -Globally Asynch Locally Sync`

| Signal name | Signal category | Description | Signal type |
| ------ | ------ | ------ | ------ |
| NAME | PAD | External Signal | ALL |
| name_i[#] | Digital | Digital input | Input |
| name_o[#] | Digital | Digital output | Output |
| name_ni[#] | Digital | Negative input | Input |
| name_no[#] | Digital | Negative output | Output |
| name_io[#] | Digital | Bidirectional port | Inout |
| name_x[#] | Digital | Gated clock | Wire |
| name_w[#] | Digital | Wire Function | Wire |
| name_v[#] | Digital | Blocking variable | reg |
| NAME | Parameter | Local or Global | parameter/localparam |
| name_v_#c[#]| Digital | Delayed signal by N cycles| Reg |


#### Parameters:
- Default values should always be defined. Some tools need them.

#### Editor Setup
Atom editor. For syntax highlighting the following packages can be used:
- language-vhdl
- language-verilog
(both by Razer6)
For Python it is best to use PyCharm with Atom(for HDL), or just Atom for both

#### Formating style
- no **tabs**, only spaces,
- **indents should be 2 spaces wide**
- no trailing whitespace
- no space before `,` or `;`
- additional spaces are allowed before `<=`, `:` or identifiers for alignment purposes
- Inversion only with `~`, not with `!`
- 1 verilog statement per line
- 1 port declaration per line

- Port declaration/instantiation.
It is much more readable to keep port names and connected signals aligned in two clearly visible columns: \
```verilog
  .mem_a_addr_i     (mem_a_addr_i),
  .mem_a_byte_sel_i (mem_a_byte_sel_i),
  .mem_a_we_i       (mem_a_we_i),
  .mem_a_re_i       (mem_a_re_i),
```

#### Code organisation Style
- You assign values/logic to a wire when you initialize it
```verilog
  wire [(WORD_WIDTH>>2)-1 : 0] 	   mult_res_w = weight_i[MAC_WORD_WIDTH-1 : 0] * activation_i[MAC_WORD_WIDTH-1 : 0];
```
- when you want to assign the data to the output port of the module you do it through a wire and all the output ports assignments should be at the end of the file, nicely grouped
  ```verilog
     assign nab_data_o = acc;
  endmodule
  ```
- every statement that could be in `begin...end` block should be in it
- **No Hardcoded** values when defining the width of a signal, only params/defines/localparams should be used
