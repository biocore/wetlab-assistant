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
from plate_mapper.plate_mapper import (plate_mapper,
                                       _print_list)


class PlateMapperTests(TestCase):
    """ Tests for plate_mapper.py """

    def setUp(self):
        """ Create working directory """
        self.wkdir = mkdtemp()

    def tearDown(self):
        """ Delete working directory """
        rmtree(self.wkdir)

    def test_plate_mapper(self):
        # test a successful conversion
        # subdirectory "data", in which test data files are located
        datadir = join(dirname(realpath(__file__)), 'data')
        # a simplified plate map file containing two plates, each having
        # 4 columns x 3 rows + 2 property fields
        input_f = open(join(datadir, 'plate_map.txt'), 'r')
        # a simplified barcode sequence template file containing 4 plates
        barseq_f = open(join(datadir, 'barseq_temp.txt'), 'r')
        # the mapping file to be written
        obs_output_fp = join(self.wkdir, 'obs_mapping.txt')
        output_f = open(obs_output_fp, 'w')
        # expected output mapping file
        exp_output_fp = join(datadir, 'exp_mapping.txt')
        # sample name list
        names_f = open(join(datadir, 'sample_list.txt'), 'r')
        with self.assertRaises(SystemExit) as context:
            plate_mapper(input_f, barseq_f, output_f, names_f)
        # check output mapping file
        with open(obs_output_fp, 'r') as f:
            obs = f.read()
        with open(exp_output_fp, 'r') as f:
            exp = f.read()
        self.assertEqual(obs, exp)
        # check screen warning message
        exp = ('Warning:\n'
               '  Novel samples: missing4B, sp220.\n'
               '  Missing samples: sp014, sp017.\n'
               '  Repeated samples: blank4A.\n')
        self.assertEqual(str(context.exception), exp)
        # test error when column headers are not incremental integers
        input_f = open(join(datadir, 'plate_map_cherr.txt'), 'r')
        with self.assertRaises(ValueError) as context:
            plate_mapper(input_f, None, None)
        err = 'Error: column headers are not incremental integers.'
        self.assertEqual(str(context.exception), err)
        # test error when row headers are not in alphabetical order
        input_f = open(join(datadir, 'plate_map_rherr.txt'), 'r')
        with self.assertRaises(ValueError) as context:
            plate_mapper(input_f, None, None)
        err = 'Error: row headers are not letters in alphabetical order.'
        self.assertEqual(str(context.exception), err)

    def test__print_list(self):
        l = ['1', '2', '3', '4', '5']
        obs = _print_list(l)
        exp = '1, 2, 3, 4, 5'
        self.assertEqual(obs, exp)
        l += ['6', '7', '8', '9', '10', '11', '12']
        obs = _print_list(l)
        exp = '1, 2, 3... (12 in total)'
        self.assertEqual(obs, exp)


if __name__ == '__main__':
    main()
