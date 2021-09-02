import pathlib
import pandas
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path
from pprint import pprint as pp
import numpy as np


def extract_rows(df, regex):
    tmp_dict = {}
    for row in df.iterrows():
        if regex in row[1]["name"]:
            tmp_dict.update({f"{row[0]}": row[1]})
    tmp_df = pandas.DataFrame.from_dict(tmp_dict)
    return tmp_df.transpose()


def plot_df(df, x="name", y=None, xlabel="testcases",
            ylabel=None, title=None, fig_name=None, fig_size=(19.2, 10.8), create_fig=True, logy=False,
            ylim=None):
    df.plot(x=x, y=y, kind='line', figsize=fig_size, grid=True, logy=logy, marker='o')
    plt.xlabel(xlabel)
    plt.xticks(rotation='horizontal')
    if "traffic" in x:
        plt.xticks(np.arange(0, max(df[str(x)])+0.05, step=0.05))
    plt.ylabel(ylabel)
    plt.title(title, loc='left')
    plt.tight_layout()
    if ylim is not None:
        x1, x2, y1, y2 = plt.axis()
        y1, y2 = ylim
        plt.axis((x1, x2, y1, y2))
    plt.margins(0.1)
    plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99), ncol=len(y))
    plt.savefig(fig_name)
    print(f"Wrote {fig_name}")
    if create_fig:
        plt.close()


def plot_hist(df, title, fig_size=(19.2, 10.8), plot_path=None):
    assert plot_path is not None, "Path has to be set"
    for cid, col in enumerate(df):
        if col != "name":
            plt.figure(figsize=fig_size)
            df[col].plot.hist()
            plt.grid()
            plt.xlabel(col)
            plt.xticks(rotation='horizontal')
            plt.ylabel("Testcase N")
            plt.title(title, loc='left')
            plt.tight_layout()
            plt.margins(0.1)
            plt.savefig(f"{plot_path}/hist_{col}")
            print(f"Wrote {plot_path}/hist_{col}.png")
            plt.close()


def plot_multi_traffic_patterns(x, y, testcase_names, df_src, title, path_to_save, xlabel, ylabel,
                                fig_size=(19.2, 10.8), ylim=None, yticks=None):
    ax = None
    for name in testcase_names:
        df = extract_rows(df_src, str(name))
        df = df.rename(columns={f"{y}": f"{name}"})
        if ax is None:
            ax = df.plot(x=str(x), y=[f"{name}"], figsize=fig_size, grid=True, marker='o')
        else:
            df.plot(x=str(x), y=[f"{name}"], ax=ax, grid=True, marker='o')

        plt.xlabel(xlabel)
        plt.xticks(rotation='horizontal')
        plt.xticks(np.arange(0, max(df[str(x)])+0.05, step=0.05))
        if yticks is not None:
            plt.yticks(yticks)

        plt.ylabel(ylabel)
        plt.title(title, loc='left')
        if ylim is not None:
            x1, x2, y1, y2 = plt.axis()
            y1, y2 = ylim
            plt.axis((x1, x2, y1, y2))
        plt.tight_layout()
        plt.margins(0.1)
        plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99))

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
    assert 'pckt_data_w' in dict_json.keys(), f"pckt_data_w not in {json_file}"
    assert 'testcases' in dict_json.keys(), f"testcases not in {json_file}"

    return dict_json, json_no_suffix


def parse_and_plot(json_file, loop_json=False, buff_size_en=False):

    if loop_json:
        buff_size = [1, 2, 3, 4]
        nxn_size = ["3_3", "4_4", "5_5"]
        dict_json = []
        df_l = []
        if buff_size_en:
            for size in buff_size:
                tmp_file_path = pathlib.Path(f"mesh_noc_xy_presynth_3_3_{size}_15.json")
                dict_json.append(parse(tmp_file_path))
                dicty, json_no_suffix = parse(tmp_file_path)
                df_l.append(pandas.DataFrame.from_dict(dicty["testcases"]))
        else:
            for nxn in nxn_size:
                tmp_file_path = pathlib.Path(f"mesh_noc_xy_presynth_{nxn}_2_15.json")
                dict_json.append(parse(tmp_file_path))
                dicty, json_no_suffix = parse(tmp_file_path)
                df_l.append(pandas.DataFrame.from_dict(dicty["testcases"]))

        testcase_names = []
        for row in df_l[0].iterrows():
            if "_0" or "_1" in row[1]["name"]:
                name = row[1]["name"].split("_")[0] + "_" + row[1]["name"].split("_")[1]
                if name not in testcase_names:
                    testcase_names.append(name)

        # print(testcase_names)
        x_name = "u_rand"
        assert x_name in testcase_names, "name not in testcase_names"
        fig_size = (19.2, 10.8)
        x = "offered_traffic"
        ax = None
        for did, df in enumerate(df_l):
            df = extract_rows(df, str(x_name))
            ff_depth = dict_json[did][0]['fifo_depth_w']
            row_n = dict_json[did][0]['row_n']
            col_m = dict_json[did][0]['col_m']
            name = f"{row_n}x{col_m}"
            df = df.rename(columns={f"avg_packet_latency_cyc": f"{name}"})

            if ax is None:
                ax = df.plot(x=str(x), y=[f"{name}"], figsize=fig_size, grid=True, marker='o')
            else:
                df.plot(x=str(x), y=[f"{name}"], ax=ax, grid=True, marker='o')

            plt.xlabel("Oferowany ruch [ułamek pojemności]")
            plt.xticks(rotation='horizontal')
            plt.xticks(np.arange(0.05, max(df[str(x)]), step=0.05))

            plt.ylabel("Latencja pakietu [cykle]")
            plt.title("Uniform Random | Wpływ zmiany wielkości sieci na latencję pakietu z buforami o głębokości 4", loc='left')
            plt.yticks(np.arange(0, 100 + 5, step=5))
            x1, x2, y1, y2 = plt.axis()
            y1, y2 = (0, 100)
            plt.axis((x1, x2, y1, y2))
            plt.tight_layout()
            plt.margins(0.1)
            plt.legend(loc='upper left', bbox_to_anchor=(0, 0.99))

        if buff_size_en:
            file_name = f"{row_n}x{col_m}_Avg_Traffic_different_buffor_size.png"
        else:
            file_name = f"Buf_2_Avg_Latency_different_network_size.png"
        plt.savefig(file_name)
        print(f"Wrote {file_name}")
        plt.close()

    else:
        dict_json, json_no_suffix = parse(json_file)
        # Gather info
        name = dict_json['noc_type']
        ps = dict_json['ps']
        row_n = dict_json['row_n']
        col_m = dict_json['col_m']
        ff_depth = dict_json['fifo_depth_w']
        pckt_data_w = dict_json['pckt_data_w']
        df_fp = pandas.DataFrame.from_dict(dict_json["testcases"])

        ps_dict = ["PRESYN", "POSTSYN"]
        title = f"noc: {name}, row_n: {row_n}, col_m: {col_m}, ff_depth_w: {ff_depth}, pckt_data_w: {pckt_data_w}"

    # Plot metrics
    # - Hops [N]
    # shortest
    # plot_df(df_fp, "name", ["shortest_hop_path"],
    #         f"testcase", f"Hops [N]", title, f'{json_no_suffix}/packet_hops_short.png')
    # plot_df(df_fp, "name", [ "average_hop_path"],
    #         f"testcase", f"Hops [N]", title, f'{json_no_suffix}/packet_hops_avg.png')
    # plot_df(df_fp, "name", ["longest_hop_path"],
    #         f"testcase", f"Hops [N]", title, f'{json_no_suffix}/packet_hops_long.png')
    #
    # plot_df(df_fp, "name", ["shortest_hop_path", "average_hop_path", "longest_hop_path"],
    #         f"testcase", f"Hops [N]", title, f'{json_no_suffix}/packet_hops_comp.png')
    #
    # # - PACKET LIFETIME [ns]
    # plot_df(df_fp, "name", ["min_packet_life_ns"],
    #         f"testcase", f"time [ns]", title, f'{json_no_suffix}/packet_life_min.png')
    # plot_df(df_fp, "name", ["mean_packet_life_ns"],
    #         f"testcase", f"time [ns]", title, f'{json_no_suffix}/packet_life_avg.png')
    # plot_df(df_fp, "name", ["max_packet_life_ns"],
    #         f"testcase", f"time [ns]", title, f'{json_no_suffix}/packet_life_max.png')
    # plot_df(df_fp, "name", ["min_packet_life_ns", "mean_packet_life_ns", "max_packet_life_ns"],
    #         f"testcase", f"time [ns]", title, f'{json_no_suffix}/packet_life_comp.png')

        # Offered vs Accepted traffic
        testcase_names = []
        for row in df_fp.iterrows():
            if "_0" or "_1" in row[1]["name"]:
                name = row[1]["name"].split("_")[0] + "_" + row[1]["name"].split("_")[1]
                if name not in testcase_names:
                    testcase_names.append(name)

        for name in testcase_names:
            df = extract_rows(df_fp, str(name))
            plot_df(df, "offered_traffic", ["accepted_traffic", "min_accepted_traffic", "max_accepted_traffic"],
                    f"Oferowany ruch [ułamek pojemności]", f"Przepustowość [ułamek pojemności]",
                    name + " | " + title, f'{json_no_suffix}/{name}_throughput.png')
            plot_df(df, "offered_traffic", ["min_packet_latency_ns", "avg_packet_latency_ns", "max_packet_latency_ns"],
                    f"Oferowany ruch [ułamek pojemności]", f"Latencja Pakietu [ns]", name + " | " + title,
                    f'{json_no_suffix}/{name}_packet_latency.png', ylim=(0, 1000))

        plot_multi_traffic_patterns("offered_traffic", "accepted_traffic", testcase_names, df_fp,
                                    "Średnia przepustowość " + title, f"{json_no_suffix}/Avg_Accepted_Traffic.png",
                                    "Oferowany ruch [ułamek pojemności]",
                                    "Przepustowość [ułamek pojemności]")

        plot_multi_traffic_patterns("offered_traffic", "avg_packet_latency_ns", testcase_names, df_fp,
                                    "Średnia latencja pakietu " + title, f"{json_no_suffix}/Avg_Packet_Latency_ns.png",
                                    "Oferowany ruch [ułamek pojemności]",
                                    "Latencja pakietu [ns]", ylim=(0, 1000), yticks=np.arange(0, 1000 + 50, step=50))

        plot_multi_traffic_patterns("offered_traffic", "avg_packet_latency_cyc", testcase_names, df_fp,
                                    "Średnia latencja pakietu " + title, f"{json_no_suffix}/Avg_Packet_Latency_cyc.png",
                                    "Oferowany ruch [ułamek pojemności]",
                                    "Latencja pakietu [cykle]", ylim=(0, 100), yticks=np.arange(0, 100 + 5, step=5))

        df_fp.to_csv(f"{json_no_suffix}/dumped.csv", float_format='%.2f')

        # Histograms
        # plot_hist(df_fp, title, plot_path=json_no_suffix)

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
