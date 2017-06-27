# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import re
import argparse
import warnings
from collections import Counter


def _print_list(l):
    """Print a list of strings in a human-friendly way.

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


def plate_mapper(input_f, barseq_f, output_f, names_f=None, special_f=None,
                 empty=False):
    """Convert a plate map file into a mapping file.

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
    empty : bool (optional)
        Whether to keep empty lines in mapping file (default: false)
    """
    # Read input plate map file
    cols = 0  # number of columns of current plate
    letter = ''  # current row header (a letter)
    plate_id = ''  # plate ID
    primer_plate_id = ''  # primer plate ID
    plates = {}  # plates (primer plate ID : well ID : sample ID)
    metadata = {}  # metadata
    primer2plate = {}  # primer plate ID => plate ID
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
            # get plate ID (trailing numeric part)
            m = re.search(r'(\d+)$', l[0])
            if m:
                plate_id = m.group(1)
            letter = 'A'
        else:  # plate body
            if letter != l[0]:
                raise ValueError('Error: row headers are not letters in '
                                 'alphabetical order.')
            if letter == 'A':  # first row
                primer_plate_id = l[cols+1]
                primer2plate[primer_plate_id] = plate_id
                plates[primer_plate_id] = {}
                # reading metadata, which are in the columns after the plate
                metadata[primer_plate_id] = l[cols+2:]
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
            # a valid definition must have code, name and description, while
            # metadatum is optional
            if len(l) < 3:
                raise ValueError('Error: invalid definition: %s.' % line)
            if l[0] in specs:
                raise ValueError('Error: Code %s has duplicates.' % repr(l[0]))
            if not l[1]:
                raise ValueError('Error: Code %s has no name.' % repr(l[0]))
            specs[l[0]] = {'name': l[1], 'note': l[2], 'metadatum': l[3:]}
        special_f.close()
        print('  Done.')

    # Write output sequencing run file
    samples = []
    print('Writing output mapping file...')
    for barcode, primer, plate, well in barseqs:
        # [ barcode sequence, linker primer sequence, primer plate #, well ID ]
        sample, metadatum = '', []
        if plate in plates:
            pid = primer2plate[plate]
            if well in plates[plate]:
                sample, metadatum = plates[plate][well], metadata[plate]
                if specs and sample in specs:
                    # replace with special sample definition
                    if specs[sample]['metadatum']:
                        # replace metadatum if available
                        metadatum = specs[sample]['metadatum']
                    sample = '%s%s.%s' % (specs[sample]['name'], pid, well)
                else:
                    # normal sample name
                    samples.append(sample)
            elif '' in specs:
                # empty well (if defined as a special sample)
                metadatum = specs['']['metadatum']
                sample = '%s%s.%s' % (specs['']['name'], pid, well)
        if sample or empty:
            # replace underscore and dash with dot in sample name
            sample_dot = sample.replace('_', '.').replace('-', '.')
            output_f.write('%s\t%s\n' % (
                '\t'.join((sample_dot, barcode, primer, plate, well)),
                '\t'.join(metadatum)))
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
          'Last updated: Jun 22, 2017.')
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
    parser.add_argument('-e', '--empty', action='store_true',
                        help='keep empty lines in mapping file')
    args = parser.parse_args()
    plate_mapper(args.input, args.barseq, args.output, args.names,
                 args.special, args.empty)
