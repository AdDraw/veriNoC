import os
import glob
import sys
import re
import pandas
import matplotlib.pyplot as plt
from pathlib import Path

def plot_rows(regex, data_frame, y, kind, filename,
              title, xlabel, ylabel, ncol=None, stacked=True, transpose=False,
              printy=False, x_rot_val='horizontal'):
  fig_size = (7.2, 4.8)
  regname = "_"
  for item in regex:
    if regname == "_":
      d_f = extract_rows(data_frame, item)
    else:
      d_f = extract_rows(d_f, item)
    regname += "_" + item

  if transpose:
    d_f = d_f.T
    d_f = extract_rows(d_f, y)
    if kind == "pie":
      d_f.plot(kind=kind, stacked=False, y=regex[0], grid=True, figsize=fig_size, pctdistance=.7, labeldistance=1.05, radius=1.05, startangle=-17, rotatelabels=True)
      # plt.legend([],[])
    else:
      # print(d_f)
      d_f.plot(kind=kind, stacked=stacked, y=d_f.keys(), grid=True, figsize=fig_size)
      # plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99), ncol=len(y))
  else:
    d_f.plot(kind=kind, stacked=stacked, y=y, grid=True, figsize=fig_size)
    if ncol is None:
      ncol = len(y)
    else:
      ncol = ncol
    # plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99), ncol=ncol)


  # if printy:
  #   print(d_f["Chip area"].to_csv())

  plt.xticks(rotation=x_rot_val)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  # plt.title(title, loc='center')
  plt.tight_layout()
  plt.margins(0.1)
  if Path("results").exists() is False:
    os.mkdir("results")
  print("Wrote results/" + filename + regname + ".png")
  plt.savefig("results/" + filename + regname + ".png")
  plt.close()


def extract_rows(df, regex):
  tmp_dict = {}
  if type(regex) is not str:
    for reg in regex:
      for row in df.iterrows():
        if reg in row[0]:
          tmp_dict.update({f"{row[0]}": row[1]})
    tmp_df = pandas.DataFrame.from_dict(tmp_dict)
    return tmp_df.transpose()
  else:
    for row in df.iterrows():
      if regex in row[0]:
        tmp_dict.update({f"{row[0]}": row[1]})
    tmp_df = pandas.DataFrame.from_dict(tmp_dict)
    return tmp_df.transpose()

def parse_file(file):
  values = {}
  rx_dict = ["Number of wires",
             "Number of public wires",
             "Number of wire bits",
             "Number of public wire bits",
             "Number of memories",
             "Number of memory bits",
             "Number of cells",
             "Number of processes",
             "AND2X1",
             "AOI21X1",
             "AOI22X1",
             "BUFX2",
             "DFFSR",
             "INVX1",
             "MUX2X1",
             "NOR2X1",
             "NAND2X1",
             "NAND3X1",
             "NOR3X1",
             "OAI21X1",
             "OAI22X1",
             "OR2X1",
             "XNOR2X1",
             "XOR2X1",
             "Chip area"
             ]
  with open(file, 'r', encoding='utf-8') as rfile:
    i = 0
    lines = rfile.readlines()
    for line in lines:
      for rx in rx_dict:
        if rx in line:
          rxx = re.compile(rx)
          match = rxx.search(line)
          p = re.compile("\d")
          match = p.findall(line[match.end():])
          v = ""
          for m in match:
            v += m
          values[rx] = v
  for rx in rx_dict:
    if rx not in values.keys():
      values[rx] = 0
  return values


def main() -> None:
  glob_log_files = glob.glob(f'*.log')
  glob_log_files = sorted(glob_log_files, key=len)
  sorted_files = []
  for file in glob_log_files:
    file_no_log = file.rstrip(".log")

    file_no_log_inted = []
    for part in file_no_log.split("-"):
      try:
        file_no_log_inted.append(int(part))
      except:
        file_no_log_inted.append(part)
        pass
    sorted_files.append(file_no_log_inted)
  sorted_files.sort()

  sorted_f = []
  for blap in sorted_files:
    tmp = ""
    for crap in blap:
      if type(crap) == int:
        tmp += "-" + str(crap)
      else:
        tmp += crap
    sorted_f.append(tmp)

  results = {}
  for file in sorted_f:
    results[file] = parse_file(file + ".log")

  dataframe = pandas.DataFrame.from_dict(results).T
  csv = dataframe.to_csv()
  print(csv)
  dataframe = dataframe.astype(float)

  print(dataframe)
 
  y = ["AND2X1", "AOI21X1", "AOI22X1", "BUFX2", "DFFSR", "INVX1",
       "MUX2X1", "NOR2X1", "NAND2X1", "NAND3X1", "NOR3X1", "OAI21X1", "OAI22X1",
      "OR2X1", "XNOR2X1", "XOR2X1",]
  plot_rows(["prototyp-3-3-8-2"], dataframe, y, "bar", "ilosc_elementow_sieci_dla_pojedynczej_konfiguracji", "Prototypowa", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["wormhole-3-3-8-2"], dataframe, y, "bar", "ilosc_elementow_sieci_dla_pojedynczej_konfiguracji", "Wormhole", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["3-3-8-2"], dataframe, y, "bar", "wplyw_typu_sieci_na_ilosc_komorek", "Wpływ typu sieci na ilość komórek", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)

  plot_rows(["3-3-8", "wormhole"], dataframe, y, "bar", "wplyw_wielkosci_bufora_na_ilosc_komorek_sieci", "Wormhole | Wpływ wielkości bufora sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["3-3-8", "prototyp"], dataframe, y, "bar", "wplyw_wielkosci_bufora_na_ilosc_komorek_sieci", "Prototypowa | Wpływ wielkości bufora sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["3-3-8"], dataframe, y, "bar", "wplyw_wielkosci_bufora_na_ilosc_komorek_sieci", "Wpływ wielkości bufora sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)

  plot_rows(["8-2", "prototyp"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Prototypowa | Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["8-2", "wormhole"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Wormhole | Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["8-2"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)

  plot_rows(["3-3", "2", "wormhole"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Wormhole | Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["3-3", "2", "prototyp"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Prototypowa | Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)
  plot_rows(["3-3", "2"], dataframe, y, "bar", "wplyw_k_sieci_na_ilosc_komorek_sieci", "Wpływ k sieci na ilość komórek w sieci", "Typ elementu", "Liczba komórek", stacked=False, transpose=True, x_rot_val=45)

  y = ["Chip area"]
  plot_rows(["3-3-8-2"], dataframe, y, "bar", "wplyw_typu_sieci_na_powierzchnie", "Wpływ typu sieci na powierzchnię sieci", "Konfiguracja", "Powierzchnia [λ^2]", stacked=False, printy=True)
  plot_rows(["prototyp", "3-3-8"], dataframe, y, "bar", "wplyw_rozmiaru_bufora_na_powierzchnie", "Prototypowa | Wpływ rozmiaru bufora na powierzchnię sieci", "Typ elementu", "Liczba komórek", stacked=False)
  plot_rows(["wormhole", "3-3-8"], dataframe, y, "bar", "wplyw_rozmiaru_bufora_na_powierzchnie", "Wormhole | Wpływ rozmiaru bufora na powierzchnię sieci", "Typ elementu", "Liczba komórek", stacked=False)
  plot_rows(["8-2"], dataframe, y, "bar", "wplyw_typu_i_k_sieci_na_powierchnie", "Wpływ typu sieci i k na powierzchnię sieci", "Konfiguracja", "Powierzchnia [λ^2]", stacked=False, printy=True, transpose=True)

  y = ["Number of cells", "Number of wires"]
  plot_rows(["prototyp", "8-2"], dataframe, y, "bar", "wplyw_k_na_ilosc_elementow", "Prototypowa | Wpływ k na ilość elementów", "Konfiguracja", "Liczba komórek", stacked=False)
  plot_rows(["wormhole", "8-2"], dataframe, y, "bar", "wplyw_k_na_ilosc_elementow", "Wormhole | Wpływ k na ilość elementów", "Konfiguracja", "Liczba komórek", stacked=False)

  plot_rows(["prototyp", "3-3-8"], dataframe, y, "bar", "wplyw_rozmiaru_bufora_na_ilosc_elementow", "Prototypowa | Wpływ rozmiaru bufora na ilość elementów", "Typ elementu", "Ilość", stacked=False)
  plot_rows(["wormhole", "3-3-8"], dataframe, y, "bar", "wplyw_rozmiaru_bufora_na_ilosc_elementow", "Wormhole | Wpływ rozmiaru bufora na ilość elementów", "Typ elementu", "Ilość", stacked=False)

  plot_rows(["3-3", "2"], dataframe, y, "bar", "wplyw_typu_i_pckt_w_na_ilosc_elementow", "Wpływ typu sieci i szerokości części informacyjnej phit'a na ilość elementów", "Typ elementu", "Ilość", stacked=False, transpose=True)
  plot_rows(["3-3", "8"], dataframe, y, "bar", "wplyw_typu_i_rozmiaru_bufora_na_ilosc_elementow", "Wpływ typu sieci i rozmiaru bufora na ilość elementów", "Typ elementu", "Ilość", stacked=False, transpose=True)

  print("Finished Plotting!")
  sys.exit(0)

if __name__ == '__main__':
  main()
