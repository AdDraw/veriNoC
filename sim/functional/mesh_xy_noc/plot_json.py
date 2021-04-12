import pathlib

import pandas
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path
from pprint import pprint as pp


def plot_df(df, x="name", y=None, xlabel="testcases",
            ylabel=None, title=None, fig_name=None, fig_size=(12.8, 7.2)):
    df.plot(x=x, y=y, kind='bar', figsize=fig_size, grid=True)
    plt.xlabel(xlabel)
    plt.xticks(rotation='horizontal')
    plt.ylabel(ylabel)
    plt.title(title, loc='left')
    plt.tight_layout()
    plt.margins(0.1)
    plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99), ncol=len(y))
    plt.savefig(fig_name)


def parse_and_plot(json_file):
    # Open and load JSON metrics data
    if not(json_file.exists()):
        print(f"ERROR: {json_file} doesn't exits!")
        return 0

    with open(json_file, 'r') as fp:
        dict_json = json.load(fp)
    json_no_suffix = json_file.name.rstrip(json_file.suffix)

    if not(Path(json_no_suffix).exists()):
        pp(f"Created {json_no_suffix} directory")
        Path.mkdir(Path(json_no_suffix))

    if 'noc_type' not in dict_json.keys():
        print(f"ERROR: No 'name' in the {json_file}")
        return 1

    if 'ps' not in dict_json.keys():
        print(f"ERROR: No 'ps' in the {json_file}")
        return 1

    if 'row_n' not in dict_json.keys():
        print(f"ERROR: No 'row_n' in the {json_file}")
        return 1

    if 'col_m' not in dict_json.keys():
        print(f"ERROR: No 'col_m' in the {json_file}")
        return 1

    if 'fifo_depth_w' not in dict_json.keys():
        print(f"ERROR: No 'fifo_depth_w' in the {json_file}")
        return 1

    if 'pckt_data_w' not in dict_json.keys():
        print(f"ERROR: No 'pckt_data_w' in the {json_file}")
        return 1

    if 'testcases' not in dict_json.keys():
        print(f"ERROR: There are no testcases in {json_file} file, plotting nothing!")
        pp(dict_json.keys())
        return 1

    # Gather info
    name = dict_json['noc_type']
    ps = dict_json['ps']
    row_n = dict_json['row_n']
    col_m = dict_json['col_m']
    ff_depth = dict_json['fifo_depth_w']
    pckt_data_w = dict_json['pckt_data_w']
    df_fp = pandas.DataFrame.from_dict(dict_json["testcases"])

    ps_dict = ["PRESYN", "POSTSYN"]
    title = f"{ps_dict[ps]}, noc: {name}, row_n: {row_n}, col_m: {col_m}, ff_depth_w: {ff_depth}, pckt_data_w: {pckt_data_w}"

    # Plot metrics
    # - Hops [N]
    plot_df(df_fp, "name", ["shortest_hop_path", "average_hop_path", "longest_hop_path"],
            f"testcase", f"Hops [N]", title, f'{json_no_suffix}/packet_hops.png')

    # - PACKET LIFETIME [ns]
    plt.figure(1)
    plot_df(df_fp, "name", ["min_packet_life_ns", "mean_packet_life_ns", "max_packet_life_ns"],
            f"testcase", f"time [ns]", title, f'{json_no_suffix}/packet_life.png')

    # - Packets Dropped [N]
    plt.figure(2)
    plot_df(df_fp, "name", ["packets_dropped"], f"testcase", f"packets [N]",
            title, f'{json_no_suffix}/packets_dropped.png')

    # Fin
    print(f"Finished Plotting '{json_file}'!")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-jf', default='metrics.json', help="Path to the JSON_FILE with MESH_NOC metrics "
                                                            "(default: metrics.json)")
    parser.add_argument('-all', default=False, help="Run every .json file in this directory")
    args = parser.parse_args()

    file_path = pathlib.Path(args.jf)
    if file_path.suffix != '.json':
        print(f"ERROR: Passed '-jf' file is not a JSON file (suffix of '{file_path}' != '.json')")
        exit(0)

    if args.all:
        current_dir = Path('./')
        for path in current_dir.iterdir():
            if path.suffix == ".json":
                parse_and_plot(path)
    else:

        parse_and_plot(file_path)
