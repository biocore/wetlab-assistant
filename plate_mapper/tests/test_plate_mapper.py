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
from os import remove
from os.path import join

from plate_mapper.plate_mapper import plate_mapper


class PlateMapperTests(TestCase):
    """ Tests for plate_mapper.py """

    def setUp(self):
        self.wkdir = mkdtemp()

    def tearDown(self):
        rmtree(self.wkdir)

    def test__main(self):
        # test a successful conversion
        input_f = open(join('.', 'data', 'input.tsv'), 'r')
        barseq_f = open(join('.', 'data', 'barseq.tsv'), 'r')
        output_fp = join(self.wkdir, 'output.tsv')
        output_f = open(output_fp, 'w')
        plate_mapper(input_f, barseq_f, output_f)
        with open(output_fp, 'r') as input_f:
            obs = input_f.read()
        with open(join('.', 'data', 'output.tsv'), 'r') as input_f:
            exp = input_f.read()
        self.assertEqual(obs, exp)
        remove(output_fp)


if __name__ == '__main__':
    main()
