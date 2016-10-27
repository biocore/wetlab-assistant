# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import os
import sys


def _main(args):
    """ Convert a plate map file into a mapping file

    Arguments
    ---------
    -i <file_path>
        Input plate map file
    -t <file_path>
        Barcode sequence template file
    -o <file_path>
        Output mapping file
    """

    # Welcome information
    print('Plate Mapper: Convert a plate map file into a mapping file.\n'
          'Last updated: Oct 25, 2016.')

    # Command-line arguments
    # argument : [ file path, short description, long description ]
    files = {'i': ['', 'input', 'input plate map file'],
             't': ['', 'barseq', 'barcode sequence template file'],
             'o': ['', 'output', 'output mapping file']}

    # Print usage information
    if len(args) < 3:
        sys.exit('Usage:\n' +
                 '  python plate_mapper.py ' +
                 ' '.join(['-' + x + ' <' + files[x][1] + '>'
                           for x in files]) + '\n' + 'Notes:\n' +
                 '\n'.join(['  ' + files[x][1] + ': ' + files[x][2] + '.'
                            for x in files]) + '\n' +
                 '  These files should be in tab-delimited (tsv) format.')

    # Read arguments
    for i in range(1, len(args)-1):
        if args[i].startswith('-') and not args[i+1].startswith('-'):
            for x in files:
                if args[i][1:] == x:
                    files[x][0] = args[i+1]
                    break

    # Validate arguments
    for x in (('i', 't', 'o')):
        if not files[x][0]:
            sys.exit('Error: ' + files[x][2] + ' (-' + x + ') is not '
                     'specified.')
    for x in (('i', 't')):
        if not os.path.isfile(files[x][0]):
            sys.exit('Error: ' + files[x][2] + ' (' + files[x][0] + ') is not '
                     'a valid file.')
    if os.path.exists(files['o'][0]):
        sys.exit('Error: ' + files['o'][2] + ' (' + files['o'][0] + ') '
                 'already exists.')


if __name__ == "__main__":
    _main(sys.argv)
