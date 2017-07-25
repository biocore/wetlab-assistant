# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import argparse


def plate_linker(metadata_f, primer_f, output_f):
    """Transfer sample IDs to mapping file by well IDs.

    Parameters
    ----------
    metadata_f : file object
        Input metadata file
    primer_f : file object
        Input primer file
    output_f : file object
        Output mapping file

    Notes
    -----
    This function joins a metadata file and a primer file (barcode sequence
    template file) by well, into a complete mapping file.

    In the metadata file, the 1st column is the sample ID, the 2nd and 3rd
    columns are primer plate ID and well ID, and the remaining columns are
    metadata to be appended.

    In the primer file, the 2nd and 3rd columns are barcode and primer, while
    the 4th and 5th columns are primer plate ID and well ID.

    In the output file, columns are: sample ID, barcode, primer, primer plate
    ID, well ID, plus variable number of metadata columns.
    """
    # merge column headers of primer and metadata files
    primcols = primer_f.readline().strip('\r\n').split('\t')
    metacols = metadata_f.readline().strip('\r\n').split('\t')[3:]
    output_f.write('%s\n' % '\t'.join(primcols + metacols))
    # read sample ID and metadata associated with well
    well2sample, well2meta = {}, {}
    for line in metadata_f:
        l = line.rstrip('\r\n').split('\t')
        sample = l[0].replace('_', '.').replace('-', '.')
        well = '%s.%s' % (l[1], l[2])
        well2sample[well] = sample
        well2meta[well] = l[3:]
    # read primer by well and append sample ID and metadata
    for line in primer_f:
        l = line.rstrip('\r\n').split('\t')
        well = '%s.%s' % (l[3], l[4])
        if well in well2sample:
            l[0] = well2sample[well]
            l += well2meta[well]
            output_f.write('%s\n' % '\t'.join(l))
    print('Task completed.')


if __name__ == "__main__":
    # Welcome information
    print('Plate Linker: Transfer sample IDs to mapping file by well IDs.\n'
          'Last updated: Jun 22, 2017.')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metadata', type=argparse.FileType('r'),
                        help='input metadata file', required=True)
    parser.add_argument('-p', '--primer', type=argparse.FileType('r'),
                        help='input primer file', required=True)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        help='output mapping file', required=True)
    args = parser.parse_args()
    plate_linker(args.metadata, args.primer, args.output)
