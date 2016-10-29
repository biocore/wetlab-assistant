# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import argparse


def plate_mapper(input_f, barseq_f, output_f):
    """ Convert a plate map file into a mapping file

    Parameters
    ---------
    input_f : file object
        Input plate map file
    barseq_f : file object
        Barcode sequence template file
    output_f : file object
        Output mapping file
    """
    idx = ''  # primer plate ID
    cols = 0  # number of columns
    plates = {}  # plates (primer plate index : well ID : sample ID)
    properties = {}  # properties
    # Read input plate map file
    print('Reading input plate map file...')
    for line in input_f:
        line = line.rstrip('\r\n')
        if not line:  # skip empty lines
            continue
        if not ''.join(line.split()):
            continue
        l = line.split('\t')
        if l[1] == '1':  # plate starts
            if not cols:  # count number of columns
                for x in l[1:]:
                    if not x.isdigit():  # stop at first non-digit cell
                        break
                    cols += 1
            continue
        if l[0] == 'A':  # first row
            idx = l[cols+1]
            plates[idx] = {}
            properties[idx] = l[cols+2:]
        for i in range(1, cols+1):
            if i < len(l) and l[i]:  # only read non-empty cells
                plates[idx][l[0] + str(i)] = l[i]
    input_f.close()
    print('  Done.')
    # Read barcode sequence template file
    barseqs = []
    print('Reading barcode sequence template file...')
    next(barseq_f)  # skip header line
    for line in barseq_f:
        line = line.rstrip('\r\n')
        if line:
            # [ barcode sequence, linker primer sequence, primer plate #,
            # well ID ]
            barseqs.append(line.split('\t'))
    barseq_f.close()
    print('  Done.')
    # Write output sequencing run file
    print('Writing output mapping file...')
    for x in barseqs:
        if x[2] in plates and x[3] in plates[x[2]]:
            output_f.write(plates[x[2]][x[3]] + '\t' + '\t'.join(x) +
                           '\t' + '\t'.join(properties[x[2]]) + '\n')
        else:
            output_f.write('\t' + '\t'.join(x) + '\n')
    output_f.close()
    print('  Done. Task completed.')


if __name__ == "__main__":
    # Welcome information
    print('Plate Mapper: Convert a plate map file into a mapping file.\n'
          'Last updated: Oct 28, 2016.')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=argparse.FileType('r'),
                        help='input plate map file', required=True)
    parser.add_argument('-t', '--barseq', type=argparse.FileType('r'),
                        help='barcode sequence template file', required=True)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        help='output mapping file', required=True)
    args = parser.parse_args()
    plate_mapper(args.input, args.barseq, args.output)
