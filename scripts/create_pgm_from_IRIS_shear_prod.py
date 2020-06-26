"""Create PGM images from IRIS SHEAR products.

Creates PGM images from IRIS SHEAR products. The products consist of a
header of 640 characters and the actual data in a table. In addition to
the raw data, a header info given by productx is required in a text file,
with the base of filename equal to raw product name with the extension
".txt". All files in the input directory matching the IRIS naming
protocol are processed.
"""
import os
import re
import numpy as np
from datetime import datetime, timedelta
import argparse


def convert(tude):
    # From https://stackoverflow.com/a/21304164
    multiplier = 1 if tude[-1] in ['N', 'E'] else -1
    multiplier *= sum(float(x) / 60 ** n
                      for n, x in enumerate(re.split("\s+|\.", tude[:-2])))
    return multiplier


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    argparser.add_argument(
        "raw_dir", type=str, help="directory for raw input")
    argparser.add_argument(
        "hdr_dir", type=str, help="directory for header input")
    argparser.add_argument(
        "output_dir", type=str, help="output directory")
    args = argparser.parse_args()

    for fn in os.listdir(args.raw_dir):
        print(fn)
        if (not len(fn.split('.')) > 1 or
                fn.split('.')[1][:3] != "SHE"):
            continue
        fn_base = fn.split('.')[0]
        # Read header from a separate file
        par = {}
        with open(os.path.join(args.hdr_dir, fn_base + '.txt'), 'r') as file:
            line = file.readline().split(':')

            while line[0] != '':
                if line[0] == "PCO name":
                    par['product_name'] = line[1].split(',')[0].strip()
                    par["task"] = line[2].split(',')[0].strip()
                elif line[0] == "PRF":
                    par['nyquist'] = float(line[3].split(',')[0][:-6].strip())
                elif line[0] == "Size is":
                    ncols = int(line[1].strip().split('x')[0])
                    nrows = int(line[1].strip().split('x')[1])
                elif line[0] == "Scale is":
                    par["xscale"] = float(line[1].split('x')[0].strip())
                    par["yscale"] = float(line[1].split('x')[1].strip())
                elif line[0] == "Center Location":
                    par["lat_0"] = convert(line[1].split(',')[0].strip())
                    par["lon_0"] = convert(line[1].split(',')[1].strip())
                elif line[0] == "Maximum range":
                    par["max_range_E"] = float(line[1].split(',')[0][:-7].strip())
                    par["max_range_N"] = float(line[1].split(',')[1][:-9].strip())

                # +proj=aeqd +ellps=intl +lon_0=xxxxx +lat_0=yyyyy +no_defs
                line = file.readline().split(':')

        d = datetime.strptime(fn_base[3:], "%y%m%d%H%M%S")
        d5 = d - timedelta(minutes=d.minute % 5, seconds=d.second,
                           microseconds=d.microsecond)

        with open(os.path.join(args.raw_dir, fn), 'rb') as file:
            data = file.read()
            dt = np.dtype(('>u1', (nrows, ncols)))
            x = np.frombuffer(data[-(ncols * nrows):], dt)

        x = x[0, :, :]

        # Transform to real data
        S = np.empty((nrows, ncols), dtype=float)
        S = x.astype(float) - 128
        S *= 0.2

        nd = -128 * 0.2
        ns = (255 - 128) * 0.2

        S[S == nd] = -np.inf
        S[S == ns] = np.nan

        pgmHeader = (
            'P5' + '\n' +
            '# radar VAN 1 24.8730 60.2710' + '\n' +
            d.strftime('# obstime %Y%m%d%H%M') + '\n' +
            '# producttype SHEAR' + '\n' +
            '# productname ' + par["product_name"] + '\n' +
            '# task ' + par["task"] + '\n' +
            '# Nyquist ' + str(par["nyquist"]) + '\n' +
            '# no_data 0' + '\n' +
            '# not_scanned 0' + '\n' +
            '# +proj=aeqd ellps=intl +lon_0=%2.5f +lat_0=%2.5f + no_defs' % (par["lon_0"], par["lat_0"]) + '\n' +
            str(ncols) + ' ' +
            str(nrows) + '\n' +
            str(255) + '\n'
        )

        pgmfn = fn_base[0:3] + d5.strftime('%Y%m%d%H%M') + '.pgm'
        with open(os.path.join(args.output_dir, pgmfn), 'wb') as file:
            file.write(bytearray(pgmHeader, 'utf-8'))

            for j in range(nrows):
                bnd = list(x[j, :])
                file.write(bytearray(bnd))
