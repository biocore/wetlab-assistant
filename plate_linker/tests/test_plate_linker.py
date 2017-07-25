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
    """Tests for plate_mapper.py."""

    def setUp(self):
        """Create working directory."""
        self.wkdir = mkdtemp()

    def tearDown(self):
        """Delete working directory."""
        rmtree(self.wkdir)

    def test_plate_linker(self):
        """Test plate_linker."""
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


if __name__ == '__main__':
    main()
