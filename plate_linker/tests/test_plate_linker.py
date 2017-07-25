# ----------------------------------------------------------------------------
# Copyright (c) 2016--, The Wetlab Assistant Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase, main
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join, dirname, realpath
from plate_linker.plate_linker import plate_linker


class PlateLinkerTests(TestCase):
    """Tests for plate_linker.py."""

    def setUp(self):
        """Create working directory."""
        self.wkdir = mkdtemp()

    def tearDown(self):
        """Delete working directory."""
        rmtree(self.wkdir)

    def test_plate_linker(self):
        """Test plate_linker."""
        # test a successful conversion
        # subdirectory "data", in which test data files are located
        datadir = join(dirname(realpath(__file__)), 'data')
        # a simplified metadata file containing 19 samples from two plates
        metadata_f = open(join(datadir, 'metadata.txt'), 'r')
        # a simplified primer file containing 12 primers x 3 plates
        primer_f = open(join(datadir, 'primer.txt'), 'r')
        # the output file to be written
        obs_output_fp = join(self.wkdir, 'obs_output.txt')
        output_f = open(obs_output_fp, 'w')
        # expected output mapping file
        exp_output_fp = join(datadir, 'exp_output.txt')
        # run plate_linker
        plate_linker(metadata_f, primer_f, output_f)
        # check output mapping file
        with open(obs_output_fp, 'r') as f:
            obs = f.read()
        with open(exp_output_fp, 'r') as f:
            exp = f.read()
        self.assertEqual(obs, exp)

        # test error when metadata table has inadequate columns
        metadata_fp = join(self.wkdir, 'metadata.txt')
        with open(metadata_fp, 'w') as f:
            f.write('Inadequate\tcolumns\n')
        metadata_f = open(metadata_fp, 'r')
        with self.assertRaises(ValueError) as context:
            plate_linker(metadata_f, None, None)
        err = 'Error: metadata table must have at least three columns.'
        self.assertEqual(str(context.exception), err)

        # test error when primer table has inadequate columns
        primer_fp = join(self.wkdir, 'primer.txt')
        with open(primer_fp, 'w') as f:
            f.write('Invalid\tcolumn\tnumber\n')
        primer_f = open(primer_fp, 'r')
        metadata_f = open(join(datadir, 'metadata.txt'), 'r')
        with self.assertRaises(ValueError) as context:
            plate_linker(metadata_f, primer_f, None)
        err = 'Error: primer table must have exactly five columns.'
        self.assertEqual(str(context.exception), err)

        # test error when metadata table contains an invalid well
        metadata_fp = join(self.wkdir, 'metadata.txt')
        with open(metadata_fp, 'w') as f:
            f.write('%s\n' % '\t'.join(('Sample', 'Plate', 'Well')))
            f.write('%s\n' % '\t'.join(('sp001', '1', 'A1')))
            f.write('%s\n' % '\t'.join(('sp002', 'not', 'valid')))
        metadata_f = open(metadata_fp, 'r')
        primer_f = open(join(datadir, 'primer.txt'), 'r')
        output_f = open(obs_output_fp, 'w')
        with self.assertRaises(ValueError) as context:
            plate_linker(metadata_f, primer_f, output_f)
        err = ('Error: invalid well identifier: not.valid.')
        self.assertEqual(str(context.exception), err)

        # test error when primer table contains an invalid well
        primer_fp = join(self.wkdir, 'primer.txt')
        with open(primer_fp, 'w') as f:
            f.write('%s\n' % '\t'.join(('Sample', 'Barcode', 'Primer', 'Plate',
                                        'Well')))
            f.write('%s\n' % '\t'.join(('', 'ATCGGCTA', 'ATCG', '1', 'A1')))
            f.write('%s\n' % '\t'.join(('', 'GCTAATCG', 'ATCG', 'in', 'val')))
        primer_f = open(primer_fp, 'r')
        metadata_f = open(join(datadir, 'metadata.txt'), 'r')
        output_f = open(obs_output_fp, 'w')
        with self.assertRaises(ValueError) as context:
            plate_linker(metadata_f, primer_f, output_f)
        err = ('Error: invalid well identifier: in.val.')
        self.assertEqual(str(context.exception), err)

        # test error when some samples correspond to non-existent primers
        metadata_fp = join(self.wkdir, 'metadata.txt')
        with open(metadata_fp, 'w') as f:
            f.write('%s\n' % '\t'.join(('Sample', 'Plate', 'Well', 'Date')))
            f.write('%s\n' % '\t'.join(('sp001', '1', 'A1', '1/1/2017')))
            f.write('%s\n' % '\t'.join(('sp002', '1', 'A2', '1/2/2017')))
            f.write('%s\n' % '\t'.join(('sp003', '1', 'F4', '1/3/2017')))
            f.write('%s\n' % '\t'.join(('sp004', '5', 'A1', '1/4/2017')))
        metadata_f = open(metadata_fp, 'r')
        primer_f = open(join(datadir, 'primer.txt'), 'r')
        output_f = open(obs_output_fp, 'w')
        with self.assertRaises(ValueError) as context:
            plate_linker(metadata_f, primer_f, output_f)
        err = ('Error: the following samples do not have matched primers: '
               'sp003, sp004.')
        self.assertEqual(str(context.exception), err)


if __name__ == '__main__':
    main()
