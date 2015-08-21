_author__ = 'Karan Kumar'

import numpy as np
from collections import OrderedDict
import re
import argparse
import os
from fabric.api import local, settings
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import csv


cols = ['Site', 'First Visual Change', 'Last Visual Change', 'Speed Index', 'Speed Index Progress',
        'Perceptual Speed Index', 'Perceptual Speed Index Progress', 'Visual Progress']

parser = argparse.ArgumentParser()
# TODO: Pass direct input video file
parser.add_argument('--input_video_dir',
                    default="",
                    help="Path to Input video dir",
                    metavar="<Path to input video dir>")
parser.add_argument('--output_csv',
                    default="",
                    help="Output CSV file",
                    metavar="<Output CSV File>")
parser.add_argument('--visual_metric_file',
                    default="",
                    help="Path to visual metric file",
                    metavar="<Visual Metric File>")
parser.add_argument('--output_dir',
                    default="",
                    help="Path to Output Dir",
                    metavar="<Path to Output Dir>")
parser.add_argument('--generate_csv', dest="generate_csv", action='store_true')
parser.add_argument('--generate_graphs', dest="generate_graphs", action='store_true')

args = parser.parse_args()

pd.options.display.mpl_style = 'default'

if '__main__' == __name__:
    if args.generate_csv:
        if not os.path.isdir(args.input_video_dir):
            print "Input video Dir does not exists --input_video_dir"
            exit(1)
        data = []
        data.append(cols)
        tmp_dir = tempfile.mkdtemp()

        for subdir, dirs, files in os.walk(args.input_video_dir):
            for file in files:
                if not file.endswith('.mp4'):
                    continue
                video_file = os.path.join(subdir, file)
                print video_file
                # Get the PSI value
                try:
                    command = "python %s -i %s -d %s --viewport --force --perceptual --orange --progress" % \
                              (args.visual_metric_file, video_file, tmp_dir)
                    with settings(warn_only=True):
                        result = local(command, capture=True)
                    vals = result.splitlines()
                    tmp_data = ['%s' % video_file.split('/')[-1]]
                    for val in vals:
                        l = val.split(':')[-1].strip()
                        if re.search(' Progress:', val):
                            l = l.replace(',', ':')
                        tmp_data.append(l)
                    data.append(tmp_data)
                except Exception as e:
                    data += "ERROR" + ","
                    print "ERROR: %s" % e.message
                    # data += '\n'
        # print data
        # write to csv
        with open(args.output_csv, "wb") as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, quotechar='"')
            for line in data:
                writer.writerow(line)
        print "Output CSV saved @ %s" % args.output_csv
    if args.generate_graphs:
        if not os.path.exists(args.output_csv):
            print "Output CSV %s does not exists --output_csv" % args.output_csv
            exit(1)
        if not os.path.isdir(args.output_dir):
            print "Output Dir %s does not exists --output_dir" % args.output_dir
            exit(1)

        df = pd.read_csv(args.output_csv)
        # print df.columns
        # TODO: Check it proper df.columns do not exists in input csv
        x = len(df['Site'])
        data = OrderedDict()
        for i in range(x):
            site = df['Site'][i]
            data[site] = OrderedDict()
            si = df['Speed Index Progress'][i]
            final_si = df['Speed Index'][i]
            final_psi = df['Perceptual Speed Index'][i]
            psi = df['Perceptual Speed Index Progress'][i]
            vp = df['Visual Progress'][i]
            try:
                tmp_si = si.split(':')
                tmp_psi = psi.split(':')
                tmp_vp = vp.split(':')
                vals = len(tmp_vp)
                si_delta = filter(None, [x.split("=")[1] for x in tmp_si])
                time_diff = filter(None, [x.split("=")[1] for x in tmp_si if x != ''])
                psi_delta = filter(None, [x.split("=")[1] for x in tmp_psi])
                si_deltas = []
                psi_deltas = []
                times = []
                for k in range(len(si_delta)):
                    j = k + 1
                    if j != len(si_delta):
                        si_deltas.append(int(si_delta[j]) - int(si_delta[k]))
                        psi_deltas.append(int(psi_delta[j]) - int(psi_delta[k]))
                        times.append(time_diff[j])

                plt.gca().set_color_cycle(['red', 'green'])
                #TODO: Add legends to the graphs
                times_t = np.array(times)
                plt.plot(times_t[1:-1], si_deltas[1:-1])
                plt.plot(times_t[1:-1], psi_deltas[1:-1])
                fp = "%s_change" % site
                path = os.path.join(args.output_dir, fp)
                print path
                plt.xlabel("Time (ms)")
                plt.ylabel("Amount of Change")
                plt.title(site)
                plt.savefig("plot_%s.png" % path)
                plt.close()
            except Exception as e:
                print "Error generating graph for %s" % site
                print "ERROR: %s" % e.message
                continue
        print "Plot saved @ %s" % args.output_dir