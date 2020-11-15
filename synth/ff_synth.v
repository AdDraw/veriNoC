/* Generated by Yosys 0.9 (git sha1 1979e0b) */

(* dynports =  1  *)
(* cells_not_processed =  1  *)
(* src = "../srcs/resource/fifo.v:7" *)
module fifo(clk_i, rst_ni, wr_en_i, rd_en_i, data_i, data_o, full_o, empty_o, overflow_o, underflow_o);
  (* src = "../srcs/resource/fifo.v:85" *)
  wire [7:0] _000_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire [7:0] _001_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire [7:0] _002_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire [7:0] _003_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire [7:0] _004_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire _005_;
  (* src = "../srcs/resource/fifo.v:85" *)
  wire [1:0] _006_;
  (* src = "../srcs/resource/fifo.v:85" *)
  wire _007_;
  (* src = "../srcs/resource/fifo.v:61" *)
  wire [1:0] _008_;
  (* src = "../srcs/resource/fifo.v:85" *)
  wire [7:0] _009_;
  (* src = "../srcs/resource/fifo.v:48" *)
  wire [1:0] _010_;
  (* src = "../srcs/resource/fifo.v:95" *)
  wire [1:0] _011_;
  wire [1:0] _012_;
  wire [1:0] _013_;
  wire [1:0] _014_;
  wire [1:0] _015_;
  wire [1:0] _016_;
  wire [1:0] _017_;
  wire [1:0] _018_;
  wire [1:0] _019_;
  wire [1:0] _020_;
  wire _021_;
  wire _022_;
  wire [1:0] _023_;
  wire [1:0] _024_;
  wire [1:0] _025_;
  wire [1:0] _026_;
  wire _027_;
  wire _028_;
  wire _029_;
  wire _030_;
  wire _031_;
  wire _032_;
  wire _033_;
  wire _034_;
  (* src = "../srcs/resource/fifo.v:71" *)
  wire _035_;
  wire [7:0] _036_;
  wire [7:0] _037_;
  wire [7:0] _038_;
  wire [7:0] _039_;
  wire [7:0] _040_;
  wire [7:0] _041_;
  wire [7:0] _042_;
  wire [7:0] _043_;
  wire _044_;
  wire [1:0] _045_;
  (* src = "../srcs/resource/fifo.v:7|<techmap.v>:432" *)
  wire [31:0] _046_;
  (* src = "../srcs/resource/fifo.v:7|<techmap.v>:428" *)
  wire [7:0] _047_;
  wire _048_;
  wire _049_;
  wire _050_;
  wire _051_;
  wire [1:0] _052_;
  wire [7:0] _053_;
  (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *)
  wire _054_;
  (* src = "../srcs/resource/fifo.v:17" *)
  input clk_i;
  (* src = "../srcs/resource/fifo.v:21" *)
  input [7:0] data_i;
  (* src = "../srcs/resource/fifo.v:22" *)
  output [7:0] data_o;
  (* src = "../srcs/resource/fifo.v:41" *)
  reg [7:0] data_v;
  (* src = "../srcs/resource/fifo.v:24" *)
  output empty_o;
  (* src = "../srcs/resource/fifo.v:47" *)
  wire empty_w;
  (* src = "../srcs/resource/fifo.v:7" *)
  reg [7:0] \fifo_v[0] ;
  (* src = "../srcs/resource/fifo.v:7" *)
  reg [7:0] \fifo_v[1] ;
  (* src = "../srcs/resource/fifo.v:7" *)
  reg [7:0] \fifo_v[2] ;
  (* src = "../srcs/resource/fifo.v:7" *)
  reg [7:0] \fifo_v[3] ;
  (* src = "../srcs/resource/fifo.v:23" *)
  output full_o;
  (* src = "../srcs/resource/fifo.v:47" *)
  wire full_w;
  (* src = "../srcs/resource/fifo.v:40" *)
  wire [31:0] i;
  (* src = "../srcs/resource/fifo.v:29" *)
  output overflow_o;
  (* src = "../srcs/resource/fifo.v:44" *)
  reg overflow_v;
  (* src = "../srcs/resource/fifo.v:20" *)
  input rd_en_i;
  (* src = "../srcs/resource/fifo.v:43" *)
  reg [1:0] rd_ptr_v;
  (* src = "../srcs/resource/fifo.v:18" *)
  input rst_ni;
  (* src = "../srcs/resource/fifo.v:30" *)
  output underflow_o;
  (* src = "../srcs/resource/fifo.v:44" *)
  reg underflow_v;
  (* src = "../srcs/resource/fifo.v:19" *)
  input wr_en_i;
  (* src = "../srcs/resource/fifo.v:43" *)
  reg [1:0] wr_ptr_v;
  assign _027_ = _023_[0] |(* src = "../srcs/resource/fifo.v:48" *)  _023_[1];
  assign _028_ = _024_[0] |(* src = "../srcs/resource/fifo.v:49" *)  _024_[1];
  assign _029_ = _011_[0] |(* src = "../srcs/resource/fifo.v:7" *)  _025_[1];
  assign _030_ = _011_[0] |(* src = "../srcs/resource/fifo.v:7" *)  rd_ptr_v[1];
  assign _031_ = rd_ptr_v[0] |(* src = "../srcs/resource/fifo.v:7" *)  _025_[1];
  assign _032_ = _010_[0] |(* src = "../srcs/resource/fifo.v:7" *)  _026_[1];
  assign _033_ = wr_ptr_v[0] |(* src = "../srcs/resource/fifo.v:7" *)  _026_[1];
  assign _034_ = _010_[0] |(* src = "../srcs/resource/fifo.v:7" *)  wr_ptr_v[1];
  assign _012_[0] = _046_[5] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[13];
  assign _012_[1] = _046_[21] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[29];
  assign _047_[5] = _012_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _012_[1];
  assign _013_[0] = _046_[7] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[15];
  assign _013_[1] = _046_[23] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[31];
  assign _047_[7] = _013_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _013_[1];
  assign _014_[0] = _046_[6] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[14];
  assign _014_[1] = _046_[22] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[30];
  assign _047_[6] = _014_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _014_[1];
  assign _015_[0] = _046_[4] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[12];
  assign _015_[1] = _046_[20] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[28];
  assign _047_[4] = _015_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _015_[1];
  assign _016_[0] = _046_[3] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[11];
  assign _016_[1] = _046_[19] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[27];
  assign _047_[3] = _016_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _016_[1];
  assign _017_[0] = _046_[2] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[10];
  assign _017_[1] = _046_[18] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[26];
  assign _047_[2] = _017_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _017_[1];
  assign _018_[0] = _046_[1] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[9];
  assign _018_[1] = _046_[17] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[25];
  assign _047_[1] = _018_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _018_[1];
  assign _019_[0] = _046_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[8];
  assign _019_[1] = _046_[16] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _046_[24];
  assign _047_[0] = _019_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:441" *)  _019_[1];
  assign _020_[0] = _048_ |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *)  _049_;
  assign _020_[1] = _050_ |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *)  _051_;
  assign _054_ = _020_[0] |(* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *)  _020_[1];
  assign _021_ = rd_ptr_v[0] |(* src = "../srcs/resource/fifo.v:7" *)  rd_ptr_v[1];
  assign _022_ = wr_ptr_v[0] |(* src = "../srcs/resource/fifo.v:7" *)  wr_ptr_v[1];
  assign full_o = ~(* src = "../srcs/resource/fifo.v:48" *) _027_;
  assign empty_o = ~(* src = "../srcs/resource/fifo.v:49" *) _028_;
  assign _048_ = ~(* src = "../srcs/resource/fifo.v:7" *) _029_;
  assign _050_ = ~(* src = "../srcs/resource/fifo.v:7" *) _030_;
  assign _049_ = ~(* src = "../srcs/resource/fifo.v:7" *) _031_;
  assign _051_ = ~(* src = "../srcs/resource/fifo.v:7" *) _021_;
  assign _035_ = _027_ |(* src = "../srcs/resource/fifo.v:71" *)  rd_en_i;
  assign _007_ = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) empty_o : underflow_v;
  assign _053_[0] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[0] : data_v[0];
  assign _053_[1] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[1] : data_v[1];
  assign _053_[2] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[2] : data_v[2];
  assign _053_[3] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[3] : data_v[3];
  assign _053_[4] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[4] : data_v[4];
  assign _053_[5] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[5] : data_v[5];
  assign _053_[6] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[6] : data_v[6];
  assign _053_[7] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _009_[7] : data_v[7];
  assign _052_[0] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _011_[0] : rd_ptr_v[0];
  assign _052_[1] = _028_ ? (* src = "../srcs/resource/fifo.v:93" *) _011_[1] : rd_ptr_v[1];
  assign _006_[0] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _052_[0] : rd_ptr_v[0];
  assign _006_[1] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _052_[1] : rd_ptr_v[1];
  assign _000_[0] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[0] : data_v[0];
  assign _000_[1] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[1] : data_v[1];
  assign _000_[2] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[2] : data_v[2];
  assign _000_[3] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[3] : data_v[3];
  assign _000_[4] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[4] : data_v[4];
  assign _000_[5] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[5] : data_v[5];
  assign _000_[6] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[6] : data_v[6];
  assign _000_[7] = rd_en_i ? (* src = "../srcs/resource/fifo.v:92" *) _053_[7] : data_v[7];
  assign _036_[0] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [0] : data_i[0];
  assign _036_[1] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [1] : data_i[1];
  assign _036_[2] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [2] : data_i[2];
  assign _036_[3] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [3] : data_i[3];
  assign _036_[4] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [4] : data_i[4];
  assign _036_[5] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [5] : data_i[5];
  assign _036_[6] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [6] : data_i[6];
  assign _036_[7] = _032_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[3] [7] : data_i[7];
  assign _037_[0] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[0] : \fifo_v[3] [0];
  assign _037_[1] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[1] : \fifo_v[3] [1];
  assign _037_[2] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[2] : \fifo_v[3] [2];
  assign _037_[3] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[3] : \fifo_v[3] [3];
  assign _037_[4] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[4] : \fifo_v[3] [4];
  assign _037_[5] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[5] : \fifo_v[3] [5];
  assign _037_[6] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[6] : \fifo_v[3] [6];
  assign _037_[7] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _036_[7] : \fifo_v[3] [7];
  assign _004_[0] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[0] : \fifo_v[3] [0];
  assign _004_[1] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[1] : \fifo_v[3] [1];
  assign _004_[2] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[2] : \fifo_v[3] [2];
  assign _004_[3] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[3] : \fifo_v[3] [3];
  assign _004_[4] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[4] : \fifo_v[3] [4];
  assign _004_[5] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[5] : \fifo_v[3] [5];
  assign _004_[6] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[6] : \fifo_v[3] [6];
  assign _004_[7] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _037_[7] : \fifo_v[3] [7];
  assign _038_[0] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [0] : data_i[0];
  assign _038_[1] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [1] : data_i[1];
  assign _038_[2] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [2] : data_i[2];
  assign _038_[3] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [3] : data_i[3];
  assign _038_[4] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [4] : data_i[4];
  assign _038_[5] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [5] : data_i[5];
  assign _038_[6] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [6] : data_i[6];
  assign _038_[7] = _033_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[2] [7] : data_i[7];
  assign _039_[0] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[0] : \fifo_v[2] [0];
  assign _039_[1] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[1] : \fifo_v[2] [1];
  assign _039_[2] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[2] : \fifo_v[2] [2];
  assign _039_[3] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[3] : \fifo_v[2] [3];
  assign _039_[4] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[4] : \fifo_v[2] [4];
  assign _039_[5] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[5] : \fifo_v[2] [5];
  assign _039_[6] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[6] : \fifo_v[2] [6];
  assign _039_[7] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _038_[7] : \fifo_v[2] [7];
  assign _003_[0] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[0] : \fifo_v[2] [0];
  assign _003_[1] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[1] : \fifo_v[2] [1];
  assign _003_[2] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[2] : \fifo_v[2] [2];
  assign _003_[3] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[3] : \fifo_v[2] [3];
  assign _003_[4] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[4] : \fifo_v[2] [4];
  assign _003_[5] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[5] : \fifo_v[2] [5];
  assign _003_[6] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[6] : \fifo_v[2] [6];
  assign _003_[7] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _039_[7] : \fifo_v[2] [7];
  assign _040_[0] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [0] : data_i[0];
  assign _040_[1] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [1] : data_i[1];
  assign _040_[2] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [2] : data_i[2];
  assign _040_[3] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [3] : data_i[3];
  assign _040_[4] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [4] : data_i[4];
  assign _040_[5] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [5] : data_i[5];
  assign _040_[6] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [6] : data_i[6];
  assign _040_[7] = _034_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[1] [7] : data_i[7];
  assign _041_[0] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[0] : \fifo_v[1] [0];
  assign _041_[1] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[1] : \fifo_v[1] [1];
  assign _041_[2] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[2] : \fifo_v[1] [2];
  assign _041_[3] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[3] : \fifo_v[1] [3];
  assign _041_[4] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[4] : \fifo_v[1] [4];
  assign _041_[5] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[5] : \fifo_v[1] [5];
  assign _041_[6] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[6] : \fifo_v[1] [6];
  assign _041_[7] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _040_[7] : \fifo_v[1] [7];
  assign _002_[0] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[0] : \fifo_v[1] [0];
  assign _002_[1] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[1] : \fifo_v[1] [1];
  assign _002_[2] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[2] : \fifo_v[1] [2];
  assign _002_[3] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[3] : \fifo_v[1] [3];
  assign _002_[4] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[4] : \fifo_v[1] [4];
  assign _002_[5] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[5] : \fifo_v[1] [5];
  assign _002_[6] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[6] : \fifo_v[1] [6];
  assign _002_[7] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _041_[7] : \fifo_v[1] [7];
  assign _042_[0] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [0] : data_i[0];
  assign _042_[1] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [1] : data_i[1];
  assign _042_[2] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [2] : data_i[2];
  assign _042_[3] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [3] : data_i[3];
  assign _042_[4] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [4] : data_i[4];
  assign _042_[5] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [5] : data_i[5];
  assign _042_[6] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [6] : data_i[6];
  assign _042_[7] = _022_ ? (* src = "../srcs/resource/fifo.v:7" *) \fifo_v[0] [7] : data_i[7];
  assign _043_[0] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[0] : \fifo_v[0] [0];
  assign _043_[1] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[1] : \fifo_v[0] [1];
  assign _043_[2] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[2] : \fifo_v[0] [2];
  assign _043_[3] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[3] : \fifo_v[0] [3];
  assign _043_[4] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[4] : \fifo_v[0] [4];
  assign _043_[5] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[5] : \fifo_v[0] [5];
  assign _043_[6] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[6] : \fifo_v[0] [6];
  assign _043_[7] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _042_[7] : \fifo_v[0] [7];
  assign _001_[0] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[0] : \fifo_v[0] [0];
  assign _001_[1] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[1] : \fifo_v[0] [1];
  assign _001_[2] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[2] : \fifo_v[0] [2];
  assign _001_[3] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[3] : \fifo_v[0] [3];
  assign _001_[4] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[4] : \fifo_v[0] [4];
  assign _001_[5] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[5] : \fifo_v[0] [5];
  assign _001_[6] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[6] : \fifo_v[0] [6];
  assign _001_[7] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _043_[7] : \fifo_v[0] [7];
  assign _045_[0] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _010_[0] : wr_ptr_v[0];
  assign _045_[1] = _035_ ? (* src = "../srcs/resource/fifo.v:71" *) _010_[1] : wr_ptr_v[1];
  assign _044_ = ~(* src = "../srcs/resource/fifo.v:71" *) _035_;
  assign _005_ = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _044_ : overflow_v;
  assign _008_[0] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _045_[0] : wr_ptr_v[0];
  assign _008_[1] = wr_en_i ? (* src = "../srcs/resource/fifo.v:70" *) _045_[1] : wr_ptr_v[1];
  assign _009_[0] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[0] : 1'hx;
  assign _009_[1] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[1] : 1'hx;
  assign _009_[2] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[2] : 1'hx;
  assign _009_[3] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[3] : 1'hx;
  assign _009_[4] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[4] : 1'hx;
  assign _009_[5] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[5] : 1'hx;
  assign _009_[6] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[6] : 1'hx;
  assign _009_[7] = _054_ ? (* src = "../srcs/resource/fifo.v:7|<techmap.v>:445" *) _047_[7] : 1'hx;
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[0] <= 0;
    else
      data_v[0] <= _000_[0];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[1] <= 0;
    else
      data_v[1] <= _000_[1];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[2] <= 0;
    else
      data_v[2] <= _000_[2];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[3] <= 0;
    else
      data_v[3] <= _000_[3];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[4] <= 0;
    else
      data_v[4] <= _000_[4];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[5] <= 0;
    else
      data_v[5] <= _000_[5];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[6] <= 0;
    else
      data_v[6] <= _000_[6];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      data_v[7] <= 0;
    else
      data_v[7] <= _000_[7];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      rd_ptr_v[0] <= 0;
    else
      rd_ptr_v[0] <= _006_[0];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      rd_ptr_v[1] <= 0;
    else
      rd_ptr_v[1] <= _006_[1];
  (* src = "../srcs/resource/fifo.v:85" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      underflow_v <= 0;
    else
      underflow_v <= _007_;
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      wr_ptr_v[0] <= 0;
    else
      wr_ptr_v[0] <= _008_[0];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      wr_ptr_v[1] <= 0;
    else
      wr_ptr_v[1] <= _008_[1];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      overflow_v <= 0;
    else
      overflow_v <= _005_;
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [0] <= 0;
    else
      \fifo_v[0] [0] <= _001_[0];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [1] <= 0;
    else
      \fifo_v[0] [1] <= _001_[1];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [2] <= 0;
    else
      \fifo_v[0] [2] <= _001_[2];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [3] <= 0;
    else
      \fifo_v[0] [3] <= _001_[3];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [4] <= 0;
    else
      \fifo_v[0] [4] <= _001_[4];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [5] <= 0;
    else
      \fifo_v[0] [5] <= _001_[5];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [6] <= 0;
    else
      \fifo_v[0] [6] <= _001_[6];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[0] [7] <= 0;
    else
      \fifo_v[0] [7] <= _001_[7];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [0] <= 0;
    else
      \fifo_v[1] [0] <= _002_[0];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [1] <= 0;
    else
      \fifo_v[1] [1] <= _002_[1];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [2] <= 0;
    else
      \fifo_v[1] [2] <= _002_[2];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [3] <= 0;
    else
      \fifo_v[1] [3] <= _002_[3];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [4] <= 0;
    else
      \fifo_v[1] [4] <= _002_[4];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [5] <= 0;
    else
      \fifo_v[1] [5] <= _002_[5];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [6] <= 0;
    else
      \fifo_v[1] [6] <= _002_[6];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[1] [7] <= 0;
    else
      \fifo_v[1] [7] <= _002_[7];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [0] <= 0;
    else
      \fifo_v[2] [0] <= _003_[0];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [1] <= 0;
    else
      \fifo_v[2] [1] <= _003_[1];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [2] <= 0;
    else
      \fifo_v[2] [2] <= _003_[2];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [3] <= 0;
    else
      \fifo_v[2] [3] <= _003_[3];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [4] <= 0;
    else
      \fifo_v[2] [4] <= _003_[4];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [5] <= 0;
    else
      \fifo_v[2] [5] <= _003_[5];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [6] <= 0;
    else
      \fifo_v[2] [6] <= _003_[6];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[2] [7] <= 0;
    else
      \fifo_v[2] [7] <= _003_[7];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [0] <= 0;
    else
      \fifo_v[3] [0] <= _004_[0];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [1] <= 0;
    else
      \fifo_v[3] [1] <= _004_[1];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [2] <= 0;
    else
      \fifo_v[3] [2] <= _004_[2];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [3] <= 0;
    else
      \fifo_v[3] [3] <= _004_[3];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [4] <= 0;
    else
      \fifo_v[3] [4] <= _004_[4];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [5] <= 0;
    else
      \fifo_v[3] [5] <= _004_[5];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [6] <= 0;
    else
      \fifo_v[3] [6] <= _004_[6];
  (* src = "../srcs/resource/fifo.v:61" *)
  always @(posedge clk_i or negedge rst_ni)
    if (!rst_ni)
      \fifo_v[3] [7] <= 0;
    else
      \fifo_v[3] [7] <= _004_[7];
  assign _023_[0] = _010_[0] ^(* src = "../srcs/resource/fifo.v:48" *)  rd_ptr_v[0];
  assign _023_[1] = _010_[1] ^(* src = "../srcs/resource/fifo.v:48" *)  rd_ptr_v[1];
  assign _024_[0] = wr_ptr_v[0] ^(* src = "../srcs/resource/fifo.v:49" *)  rd_ptr_v[0];
  assign _024_[1] = wr_ptr_v[1] ^(* src = "../srcs/resource/fifo.v:49" *)  rd_ptr_v[1];
  assign _025_[1] = rd_ptr_v[1] ^(* src = "../srcs/resource/fifo.v:7" *)  1'h1;
  assign _026_[1] = wr_ptr_v[1] ^(* src = "../srcs/resource/fifo.v:7" *)  1'h1;
  assign _010_[0] = wr_ptr_v[0] ^(* src = "../srcs/resource/fifo.v:7" *)  1'h1;
  assign _046_[24] = \fifo_v[0] [0] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[25] = \fifo_v[0] [1] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[26] = \fifo_v[0] [2] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[27] = \fifo_v[0] [3] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[28] = \fifo_v[0] [4] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[29] = \fifo_v[0] [5] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[30] = \fifo_v[0] [6] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[31] = \fifo_v[0] [7] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _051_;
  assign _046_[16] = \fifo_v[1] [0] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[17] = \fifo_v[1] [1] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[18] = \fifo_v[1] [2] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[19] = \fifo_v[1] [3] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[20] = \fifo_v[1] [4] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[21] = \fifo_v[1] [5] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[22] = \fifo_v[1] [6] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[23] = \fifo_v[1] [7] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _050_;
  assign _046_[8] = \fifo_v[2] [0] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[9] = \fifo_v[2] [1] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[10] = \fifo_v[2] [2] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[11] = \fifo_v[2] [3] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[12] = \fifo_v[2] [4] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[13] = \fifo_v[2] [5] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[14] = \fifo_v[2] [6] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[15] = \fifo_v[2] [7] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _049_;
  assign _046_[0] = \fifo_v[3] [0] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[1] = \fifo_v[3] [1] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[2] = \fifo_v[3] [2] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[3] = \fifo_v[3] [3] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[4] = \fifo_v[3] [4] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[5] = \fifo_v[3] [5] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[6] = \fifo_v[3] [6] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _046_[7] = \fifo_v[3] [7] &(* src = "../srcs/resource/fifo.v:7|<techmap.v>:434" *)  _048_;
  assign _010_[1] = wr_ptr_v[1] ^(* src = "../srcs/resource/fifo.v:73|<techmap.v>:263" *)  wr_ptr_v[0];
  assign _011_[1] = rd_ptr_v[1] ^(* src = "../srcs/resource/fifo.v:95|../srcs/resource/fifo.v:73|<techmap.v>:263" *)  rd_ptr_v[0];
  assign _011_[0] = 1'h1 ^(* src = "../srcs/resource/fifo.v:95|../srcs/resource/fifo.v:73|<techmap.v>:262" *)  rd_ptr_v[0];
  assign _025_[0] = _011_[0];
  assign _026_[0] = _010_[0];
  assign data_o = data_v;
  assign empty_w = empty_o;
  assign full_w = full_o;
  assign i = 32'd4;
  assign overflow_o = overflow_v;
  assign underflow_o = underflow_v;
endmodule