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
    cols = 0  # number of columns of current plate
    letter = ''  # current row header (a letter)
    primer_plate_id = ''  # primer plate ID
    plates = {}  # plates (primer plate ID : well ID : sample ID)
    properties = {}  # properties
    # Read input plate map file
    print('Reading input plate map file...')
    for line in input_f:
        l = line.rstrip().split('\t')
        if l == ['']:  # skip empty lines
            continue
        if len(l) > 1 and l[1] == '1':  # plate head
            for cols, v in enumerate(l[1:]):
                if not v.isdigit():  # stop at first non-digit cell
                    break
                elif int(v) != cols+1:
                    raise ValueError('Error: column headers are not '
                                     'incremental integers.')
            letter = 'A'
        else:  # plate body
            if letter != l[0]:
                raise ValueError('Error: row headers are not letters in '
                                 'alphabetical order.')
            if letter == 'A':  # first row
                primer_plate_id = l[cols+1]
                plates[primer_plate_id] = {}
                # reading properties, which are in the columns after the plate
                properties[primer_plate_id] = l[cols+2:]
            letter = chr(ord(letter) + 1)
            # only read non-empty cells in column number range
            plates[primer_plate_id].update({'%s%d' % (l[0], i): l[i]
                                            for i in range(1, cols+1)
                                            if i < len(l) and l[i]})
    input_f.close()
    print('  Done.')
    # Read barcode sequence template file
    barseqs = []
    print('Reading barcode sequence template file...')
    next(barseq_f)  # skip header line
    for line in barseq_f:
        line = line.rstrip()
        if line:
            barseqs.append(line.split('\t'))
    barseq_f.close()
    print('  Done.')
    # Write output sequencing run file
    print('Writing output mapping file...')
    for x in barseqs:
        # [ barcode sequence, linker primer sequence, primer plate #, well ID ]
        if x[2] in plates and x[3] in plates[x[2]]:
            output_f.write('%s\t%s\t%s\n' % (plates[x[2]][x[3]], '\t'.join(x),
                           '\t'.join(properties[x[2]])))
        else:
            output_f.write('\t' + '\t'.join(x) + '\n')
    output_f.close()
    print('  Done. Task completed.')


if __name__ == "__main__":
    # Welcome information
    print('Plate Mapper: Convert a plate map file into a mapping file.\n'
          'Last updated: Oct 31, 2016.')
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
