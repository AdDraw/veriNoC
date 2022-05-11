import pathlib
import pandas
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path
from pprint import pprint as pp

def extract_rows(df, regex):
    tmp_dict = {}
    for row in df.iterrows():
        if regex in row[1]["name"]:
            tmp_dict.update({f"{row[0]}": row[1]})
    tmp_df = pandas.DataFrame.from_dict(tmp_dict)
    return tmp_df.transpose()


def plot_df(df, x="name", y=None, xlabel="testcases",
            ylabel=None, title=None, fig_name=None, fig_size=(6.4, 4.8), create_fig=True, logy=False,
            ylim=None, xlim=None, ncol=1):
    df.plot(x=x, y=y, kind='line', figsize=fig_size, grid=True, logy=logy, marker='o')
    plt.xlabel(xlabel)
    plt.xticks(rotation='horizontal')

    plt.ylabel(ylabel)
 
    if (ylim or xlim) is not None:
      x1, x2, y1, y2 = plt.axis()
      if ylim is not None:
        y1, y2 = ylim
      if xlim is not None:
        x1, x2 = xlim
      plt.axis((x1, x2, y1, y2))

    plt.tight_layout()
    plt.margins(0.1)
    plt.legend(loc='best', ncol=ncol)
    plt.savefig(fig_name)
    print(f"Wrote {fig_name}")
    if create_fig:
        plt.close()


def plot_hist(df, title, fig_size=(6.4, 4.8), plot_path=None):
    assert plot_path is not None, "Path has to be set"
    for cid, col in enumerate(df):
        if col != "name":
            plt.figure(figsize=fig_size)
            df[col].plot.hist()
            plt.grid()
            plt.xlabel(col)
            # plt.xticks(rotation='horizontal')
            plt.ylabel("Testcase N")
            # plt.title(title, loc='left')
            plt.tight_layout()
            plt.margins(0.1)
            plt.savefig(f"{plot_path}/hist_{col}")
            print(f"Wrote {plot_path}/hist_{col}.png")
            plt.close()


def plot_multi_traffic_patterns(x, y, testcase_names, df_src, title, path_to_save, xlabel, ylabel,
                                fig_size=(6.4, 4.8), ylim=None, yticks=None, logy=False, xlim=None, ncol=2):
    ax = None
    for name in testcase_names:
        df = extract_rows(df_src, str(name))
        df = df.rename(columns={f"{y}": f"{name}"})
        if ax is None:
            ax = df.plot(x=str(x), y=[f"{name}"], figsize=fig_size, grid=True, marker='o', logy=logy)
        else:
            df.plot(x=str(x), y=[f"{name}"], ax=ax, grid=True, marker='o', logy=logy)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
      
        if (ylim or xlim) is not None:
          x1, x2, y1, y2 = plt.axis()
          if ylim is not None:
            y1, y2 = ylim
          if xlim is not None:
            x1, x2 = xlim
          plt.axis((x1, x2, y1, y2))

        plt.tight_layout()
        plt.margins(0.1)
        plt.legend(loc='best', ncol=ncol)

    plt.savefig(f"{path_to_save}")
    print(f"Wrote {path_to_save}")
    plt.close()


def parse(json_file):
    # Open and load JSON metrics data
    if not (json_file.exists()):
        print(f"ERROR: {json_file} doesn't exits!")
        return 0

    with open(json_file, 'r') as fp:
        dict_json = json.load(fp)
    json_no_suffix = json_file.name.rstrip(json_file.suffix)

    if not (Path(json_no_suffix).exists()):
        pp(f"Created {json_no_suffix} directory")
        Path.mkdir(Path(json_no_suffix))

    assert 'noc_type' in dict_json.keys(), f"noc_type not in {json_file}"
    assert 'ps' in dict_json.keys(), f"ps not in {json_file}"
    assert 'row_n' in dict_json.keys(), f"row_n not in {json_file}"
    assert 'col_m' in dict_json.keys(), f"col_m not in {json_file}"
    assert 'channel_w' in dict_json.keys(), f"channel_w not in {json_file}"
    assert 'testcases' in dict_json.keys(), f"testcases not in {json_file}"

    return dict_json, json_no_suffix


def parse_and_plot(json_file, loop_json=False, change_param="buff_size"):
  if loop_json:
    buff_size = [2, 3, 4]
    # plen_size = [4, 8, 16]
    nxn_size = ["3_3", "4_4", "5_5"]
    dict_json = []
    df_l = []
    dir = change_param
    if not (Path(change_param).exists()):
      pp(f"Created '{change_param}' directory")
      Path.mkdir(Path(change_param))
    if change_param == "buff_size":
      for size in buff_size:
        tmp_file_path = pathlib.Path(f"mesh_noc_wh_xy_presynth_3_3_{size}_8_4.json")
        dict_json.append(parse(tmp_file_path))
        dicty, json_no_suffix = parse(tmp_file_path)
        df_l.append(pandas.DataFrame.from_dict(dicty["testcases"]))
    elif change_param == "net_size":
      for nxn in nxn_size:
        tmp_file_path = pathlib.Path(f"mesh_noc_wh_xy_presynth_{nxn}_2_8_4.json")
        dict_json.append(parse(tmp_file_path))
        dicty, json_no_suffix = parse(tmp_file_path)
        df_l.append(pandas.DataFrame.from_dict(dicty["testcases"]))
    else:
      raise ValueError(f"change param is not supported {change_param}")

    testcase_names = []
    for row in df_l[0].iterrows():
      if "_0" or "_1" in row[1]["name"]:
        if len(row[1]["name"].split("_")) == 1:
          name = row[1]["name"]
        elif len(row[1]["name"].split("_")) == 2:
          name = row[1]["name"].split("_")[0]
        else:
          name = row[1]["name"].split("_")[0] + "_" + row[1]["name"].split("_")[1]
        if name not in testcase_names:
          testcase_names.append(name)

    fig_size = (6.4, 4.8)
    x = "offered_traffic"
    metric_name = ["accepted_traffic", "avg_packet_latency"]
    for x_name in metric_name:
      for testcase in testcase_names:
        if testcase == "uniform_random":
          ax = None
          for did, df in enumerate(df_l):
            df = extract_rows(df, str(testcase))
            ff_depth = dict_json[did][0]['node_buffer_depth_w']
            row_n = dict_json[did][0]['row_n']
            col_m = dict_json[did][0]['col_m']
            name = f"k:{row_n}, buf: {ff_depth}"
            df = df.rename(columns={f"{x_name}": f"{name}"})

            if ax is None:
              ax = df.plot(x=str(x), y=[f"{name}"], figsize=fig_size, grid=True, marker='o')
            else:
              df.plot(x=str(x), y=[f"{name}"], ax=ax, grid=True, marker='o')

            plt.xlabel("Oferowany ruch")
            plt.xticks(rotation='horizontal')

            if x_name == "accepted_traffic":
              plt.ylabel(f"Akcpetowany ruch")
            else:
              plt.ylabel(f"Latencja [ns]")

            if x_name != "accepted_traffic":
              x1, x2, y1, y2 = plt.axis()
              y1, y2 = (0, 2000)
              x1, x2 = (0, .55)
              plt.axis((x1, x2, y1, y2))
            plt.tight_layout()
            plt.margins(0.1)
            plt.legend(loc='best')

          if change_param == "buff_size":
            file_name = f"{dir}/{row_n}x{col_m}_{testcase}_{x_name}_different_buffer_size.png"
          elif change_param == "net_size":
            file_name = f"{dir}/{ff_depth}_{testcase}_{x_name}_different_network_size.png"

          plt.savefig(file_name)
          print(f"Wrote {file_name}!")
          plt.close()
    print(f"Finished Plotting '{dir}'!")
    return 0

  else:
    print("ELSEVIER")
    dict_json, json_no_suffix = parse(json_file)
    # Gather info
    name = dict_json['noc_type']
    ps = dict_json['ps']
    row_n = dict_json['row_n']
    col_m = dict_json['col_m']
    buffer_w = dict_json['node_buffer_depth_w']
    channel_w = dict_json['channel_w']
    df_fp = pandas.DataFrame.from_dict(dict_json["testcases"])

    ps_dict = ["PRESYN", "POSTSYN"]
    title = f"noc: {name}, row_n: {row_n}, col_m: {col_m}, channel_w: {channel_w}, buffer_w: {buffer_w}"

    # Offered vs Accepted traffic
    testcase_names = []
    for row in df_fp.iterrows():
      if "_0" or "_1" in row[1]["name"]:
        if len(row[1]["name"].split("_")) == 1:
          name = row[1]["name"]
        elif len(row[1]["name"].split("_")) == 2:
          name = row[1]["name"].split("_")[0]
        else:
          name = row[1]["name"].split("_")[0] + "_" + row[1]["name"].split("_")[1]
        if name not in testcase_names:
          testcase_names.append(name)
      else:
        print("'_0' or '_1' was not found in the testcase name")

    for name in testcase_names:
      df = extract_rows(df_fp, str(name))
      plot_df(df, "offered_traffic", ["accepted_traffic", "min_accepted_traffic", "max_accepted_traffic"],
              f"Oferowany ruch", f"Akceptowany ruch",
              name + " | " + title, f'{json_no_suffix}/{name}_throughput.png')
      plot_df(df, "offered_traffic", ["min_packet_latency", "avg_packet_latency", "max_packet_latency"],
              f"Oferowany ruch", f"Latencja Pakietu [ns]", name + " | " + title,
              f'{json_no_suffix}/{name}_packet_latency.png', ylim=(0, 2000), xlim=(0,0.45))


    plot_multi_traffic_patterns("offered_traffic", "accepted_traffic", testcase_names, df_fp,
                                "Średnia przepustowość " + title, f"{json_no_suffix}/Avg_Accepted_Traffic.png",
                                "Oferowany ruch",
                                "Akceptowany ruch")#  yticks=np.arange(0, 1 + 0.05, step=0.05))

    plot_multi_traffic_patterns("offered_traffic", "avg_packet_latency", testcase_names, df_fp,
                                "Średnia latencja pakietu " + title, f"{json_no_suffix}/Avg_Packet_Latency.png",
                                "Oferowany ruch",
                                "Latencja pakietu [ns]", ylim=(0, 2000), xlim=(0,0.45), ncol=1)

    plot_multi_traffic_patterns("offered_traffic", "avg_packet_latency", testcase_names, df_fp,
                                "Średnia latencja pakietu", f"{json_no_suffix}/Avg_Packet_Latency_logy.png",
                                "Oferowany ruch",
                                "Latencja pakietu [ns]", logy=True, ncol=1)

    df_fp.to_csv(f"{json_no_suffix}/dumped.csv", float_format='%.2f')
    print(f"Finished Plotting '{json_file}'!")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-jf', default=None, help="Path to the JSON_FILE with MESH_NOC metrics "
                                                            "(default: metrics.json)")
    parser.add_argument('-all', default=False, help="Run every .json file in this directory")
    parser.add_argument('-json_loop', default=False, action='store_true', help="Run every .json file in this directory")
    parser.add_argument('-cp', default="buff_size", help="used when running 'json_loop'")
    args = parser.parse_args()

    if args.jf is not None:
      file_path = pathlib.Path(args.jf)
      if file_path.suffix != '.json':
          print(f"ERROR: Passed '-jf' file is not a JSON file (suffix of '{file_path}' != '.json')")
          exit(0)
    else:
      file_path = "metrics.json"

    if args.all:
        current_dir = Path('./')
        for path in current_dir.iterdir():
            if path.suffix == ".json":
                parse_and_plot(path)
    else:
        parse_and_plot(file_path, loop_json=args.json_loop, change_param=args.cp)
