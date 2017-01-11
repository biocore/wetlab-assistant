# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import argparse
import warnings
from collections import Counter


def _print_list(l):
    """ Print a list of strings in a human-friendly way

    Parameter
    ---------
    l : list of str
        Input list of strings

    Return
    ------
    str
        Output string

    Notes
    -----
    If the list has <= 10 items, the entire list will be printed.
    If the list has > 10 items, only the first three items will be printed,
    followed by "... (no._of_items in total)"
    """
    n = len(l)
    if n > 10:
        return(', '.join(l[:3]) + '... (' + str(n) + ' in total)')
    else:
        return(', '.join(l))


def plate_mapper(input_f, barseq_f, output_f, names_f=None, special_f=None):
    """ Convert a plate map file into a mapping file

    Parameters
    ----------
    input_f : file object
        Input plate map file
    barseq_f : file object
        Barcode sequence template file
    output_f : file object
        Output mapping file
    names_f : file object (optional)
        Sample name list file
    special_f : file object (optional)
        Special sample definition file
    """

    # Read input plate map file
    cols = 0  # number of columns of current plate
    letter = ''  # current row header (a letter)
    primer_plate_id = ''  # primer plate ID
    plates = {}  # plates (primer plate ID : well ID : sample ID)
    properties = {}  # properties
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

    # Read special sample definitions
    specs = {}
    if special_f:
        print('Reading special sample definitions...')
        next(special_f)  # skip header line
        for line in special_f:
            line = line.rstrip()
            l = line.split('\t')
            if len(l) < 4:
                raise ValueError('Error: invalid definition: %s.' % line)
            if l[0] in specs:
                raise ValueError('Error: Code %s has duplicates.' % repr(l[0]))
            if not l[1]:
                raise ValueError('Error: Code %s has no name.' % repr(l[0]))
            specs[l[0]] = {'name': l[1], 'note': l[2], 'property': l[3:]}
        special_f.close()
        print('  Done.')

    # Write output sequencing run file
    samples = []
    print('Writing output mapping file...')
    for x in barseqs:
        # [ barcode sequence, linker primer sequence, primer plate #, well ID ]
        sample, property = '', []
        if x[2] in plates:
            if x[3] in plates[x[2]]:
                sample, property = plates[x[2]][x[3]], properties[x[2]]
                if specs and sample in specs:
                    # replace with special sample definition
                    property = specs[sample]['property']
                    sample = '%s%s.%s' % (specs[sample]['name'], x[2], x[3])
                else:
                    # normal sample name
                    samples.append(sample)
            elif '' in specs:
                # empty well (if defined as a special sample)
                property = specs['']['property']
                sample = '%s%s.%s' % (specs['']['name'], x[2], x[3])
        output_f.write('%s\t%s\t%s\n' % (sample, '\t'.join(x),
                       '\t'.join(property)))
    output_f.close()
    print('  Done.')

    # Validate sample names
    if names_f:
        print('Validating sample names...')
        samples = Counter(samples)
        names = set()
        for line in names_f:
            l = line.rstrip().split('\t')
            if l[0]:  # skip empty names
                names.add(l[0])  # keep first field as name
        names_f.close()
        warning = ''
        if names:
            sample_set = set(samples)
            # samples in plate map but not in name list
            novel = sample_set - names
            # samples in name list but not in plate map
            missing = names - sample_set
            # samples that occur more than one times in plate map
            repeated = set()
            for name in names:
                if name in samples and samples[name] > 1:
                    repeated.add(name)
            if novel:
                warning += ('  Novel samples: %s.\n'
                            % _print_list(sorted(novel)))
            if missing:
                warning += ('  Missing samples: %s.\n'
                            % _print_list(sorted(missing)))
            if repeated:
                warning += ('  Repeated samples: %s.\n'
                            % _print_list(sorted(repeated)))
        print('  Done.')
        if warning:
            # display warning message
            warnings.formatwarning = lambda msg, *a: str(msg)
            warnings.warn('Warning:\n%s' % warning)
        print('Task completed.')


if __name__ == "__main__":
    # Welcome information
    print('Plate Mapper: Convert a plate map file into a mapping file.\n'
          'Last updated: Jan 4, 2016.')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=argparse.FileType('r'),
                        help='input plate map file', required=True)
    parser.add_argument('-t', '--barseq', type=argparse.FileType('r'),
                        help='barcode sequence template file', required=True)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        help='output mapping file', required=True)
    parser.add_argument('-n', '--names', type=argparse.FileType('r'),
                        help='(optional) sample name list file',
                        required=False, default=None)
    parser.add_argument('-s', '--special', type=argparse.FileType('r'),
                        help='(optional) special sample definition file',
                        required=False, default=None)
    args = parser.parse_args()
    plate_mapper(args.input, args.barseq, args.output, args.names,
                 args.special)
