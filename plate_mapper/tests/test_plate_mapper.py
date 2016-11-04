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
from os.path import join, isfile

from plate_mapper.plate_mapper import plate_mapper


class PlateMapperTests(TestCase):
    """ Tests for plate_mapper.py """

    def setUp(self):
        """ Set up working directory and test files
        """
        self.wkdir = mkdtemp()
        self.barseq_temp_fp = join(self.wkdir, "barseq_temp.tsv")
        with open(self.barseq_temp_fp, 'w') as tmp:
            tmp.write(barseq_temp)
        self.plate_map_fp = join(self.wkdir, "plate_map.tsv")
        with open(self.plate_map_fp, 'w') as tmp:
            tmp.write(plate_map)
        self.mapping_fp = join(self.wkdir, "mapping.tsv")
        self.plate_map_cherr_fp = join(self.wkdir, "plate_map_cherr.tsv")
        with open(self.plate_map_cherr_fp, 'w') as tmp:
            tmp.write(plate_map_col_header_err)
        self.plate_map_rherr_fp = join(self.wkdir, "plate_map_rherr.tsv")
        with open(self.plate_map_rherr_fp, 'w') as tmp:
            tmp.write(plate_map_row_header_err)
        # list of files to remove
        self.tmpfiles = [self.barseq_temp_fp,
                         self.plate_map_fp,
                         self.mapping_fp,
                         self.plate_map_cherr_fp,
                         self.plate_map_rherr_fp]

    def tearDown(self):
        for file in self.tmpfiles:
            if isfile(file):
                remove(file)
        rmtree(self.wkdir)

    def test__main(self):
        # test a successful conversion
        input_f = open(self.plate_map_fp, 'r')
        barseq_f = open(self.barseq_temp_fp, 'r')
        output_f = open(self.mapping_fp, 'w')
        plate_mapper(input_f, barseq_f, output_f)
        with open(self.mapping_fp, 'r') as input_f:
            obs = input_f.read()
        self.assertEqual(obs, exp_mapping)
        # test column header Error
        input_f = open(self.plate_map_cherr_fp, 'r')
        with self.assertRaises(ValueError) as context:
            plate_mapper(input_f, None, None)
        err = 'Error: column headers are not incremental integers.'
        self.assertEqual(str(context.exception), err)
        # test row header Error
        input_f = open(self.plate_map_rherr_fp, 'r')
        with self.assertRaises(ValueError) as context:
            plate_mapper(input_f, None, None)
        err = 'Error: row headers are not letters in alphabetical order.'
        self.assertEqual(str(context.exception), err)


# A simplified plate map file containing two plates, each having 4 columns x
# 3 rows + 2 property fields
plate_map = """
Plate#1	1	2	3	4	#	Who  When
A	sp001	sp004	sp006	blank4A	1	QZ	8/15/16
B	sp002	sp005	sp007	missing4B		a sample is missing
C	sp003	blank2C	blank3C	sp220

Plate#2	1	2	3	4	#	Who  When
A	sp012	sp015	sp018	blank4A	3	QZ	10/26/16
B	sp013	sp016	sp019
C
"""

# A simplified barcode sequence template file containing 4 plates
barseq_temp = """BarcodeSequence\tLinkerPrimerSequence\tPrimer_Plate\tWell_ID
AGCCTTCGTCGC	ATCG	1	A1
TCCATACCGGAA	ATCG	1	A2
AGCCCTGCTACA	ATCG	1	A3
CCTAACGGTCCA	ATCG	1	A4
CGTATAAATGCG	ATCG	1	B1
ATGCTGCAACAC	ATCG	1	B2
ACTCGCTCGCTG	ATCG	1	B3
TTCCTTAGTAGT	ATCG	1	B4
TGACTAATGGCC	ATCG	1	C1
CGGGACACCCGA	ATCG	1	C2
CTGTCTATACTA	ATCG	1	C3
TATGCCAGAGAT	ATCG	1	C4
CTACAGGGTCTC	ATCG	2	A1
CTTGGAGGCTTA	ATCG	2	A2
TATCATATTACG	ATCG	2	A3
CTATATTATCCG	ATCG	2	A4
GTTCATTAAACT	ATCG	2	B1
GTGCCGGCCGAC	ATCG	2	B2
CCTTGACCGATG	ATCG	2	B3
CAAACTGCGTTG	ATCG	2	B4
TTCGATGCCGCA	ATCG	2	C1
AGAGGGTGATCG	ATCG	2	C2
AGCTCTAGAAAC	ATCG	2	C3
CTGACACGAATA	ATCG	2	C4
CCTCGCATGACC	ATCG	3	A1
GGCGTAACGGCA	ATCG	3	A2
GCGAGGAAGTCC	ATCG	3	A3
CAAATTCGGGAT	ATCG	3	A4
CGCGCAAGTATT	ATCG	3	B1
AATACAGACCTG	ATCG	3	B2
GGACAAGTGCGA	ATCG	3	B3
TACGGTCTGGAT	ATCG	3	B4
AAGGCGCTCCTT	ATCG	3	C1
GATCTAATCGAG	ATCG	3	C2
CTGATGTACACG	ATCG	3	C3
ACGTATTCGAAG	ATCG	3	C4
TAGGACGGGAGT	ATCG	4	A1
AAGTCTTATCTC	ATCG	4	A2
TTGCACCGTCGA	ATCG	4	A3
CTCCGAACAACA	ATCG	4	A4
GTTTGGCCACAC	ATCG	4	B1
GTCCTACACAGC	ATCG	4	B2
ATTTACAATTGA	ATCG	4	B3
CCACTGCCCACC	ATCG	4	B4
TATATAGTATCC	ATCG	4	C1
ACTGTTTACTGT	ATCG	4	C2
GTCACGGACATT	ATCG	4	C3
GAATATACCTGG	ATCG	4	C4
"""

# sample output file
exp_mapping = """sp001	AGCCTTCGTCGC	ATCG	1	A1	QZ	8/15/16
sp004	TCCATACCGGAA	ATCG	1	A2	QZ	8/15/16
sp006	AGCCCTGCTACA	ATCG	1	A3	QZ	8/15/16
blank4A	CCTAACGGTCCA	ATCG	1	A4	QZ	8/15/16
sp002	CGTATAAATGCG	ATCG	1	B1	QZ	8/15/16
sp005	ATGCTGCAACAC	ATCG	1	B2	QZ	8/15/16
sp007	ACTCGCTCGCTG	ATCG	1	B3	QZ	8/15/16
missing4B	TTCCTTAGTAGT	ATCG	1	B4	QZ	8/15/16
sp003	TGACTAATGGCC	ATCG	1	C1	QZ	8/15/16
blank2C	CGGGACACCCGA	ATCG	1	C2	QZ	8/15/16
blank3C	CTGTCTATACTA	ATCG	1	C3	QZ	8/15/16
sp220	TATGCCAGAGAT	ATCG	1	C4	QZ	8/15/16
\tCTACAGGGTCTC	ATCG	2	A1
\tCTTGGAGGCTTA	ATCG	2	A2
\tTATCATATTACG	ATCG	2	A3
\tCTATATTATCCG	ATCG	2	A4
\tGTTCATTAAACT	ATCG	2	B1
\tGTGCCGGCCGAC	ATCG	2	B2
\tCCTTGACCGATG	ATCG	2	B3
\tCAAACTGCGTTG	ATCG	2	B4
\tTTCGATGCCGCA	ATCG	2	C1
\tAGAGGGTGATCG	ATCG	2	C2
\tAGCTCTAGAAAC	ATCG	2	C3
\tCTGACACGAATA	ATCG	2	C4
sp012	CCTCGCATGACC	ATCG	3	A1	QZ	10/26/16
sp015	GGCGTAACGGCA	ATCG	3	A2	QZ	10/26/16
sp018	GCGAGGAAGTCC	ATCG	3	A3	QZ	10/26/16
blank4A	CAAATTCGGGAT	ATCG	3	A4	QZ	10/26/16
sp013	CGCGCAAGTATT	ATCG	3	B1	QZ	10/26/16
sp016	AATACAGACCTG	ATCG	3	B2	QZ	10/26/16
sp019	GGACAAGTGCGA	ATCG	3	B3	QZ	10/26/16
\tTACGGTCTGGAT	ATCG	3	B4
\tAAGGCGCTCCTT	ATCG	3	C1
\tGATCTAATCGAG	ATCG	3	C2
\tCTGATGTACACG	ATCG	3	C3
\tACGTATTCGAAG	ATCG	3	C4
\tTAGGACGGGAGT	ATCG	4	A1
\tAAGTCTTATCTC	ATCG	4	A2
\tTTGCACCGTCGA	ATCG	4	A3
\tCTCCGAACAACA	ATCG	4	A4
\tGTTTGGCCACAC	ATCG	4	B1
\tGTCCTACACAGC	ATCG	4	B2
\tATTTACAATTGA	ATCG	4	B3
\tCCACTGCCCACC	ATCG	4	B4
\tTATATAGTATCC	ATCG	4	C1
\tACTGTTTACTGT	ATCG	4	C2
\tGTCACGGACATT	ATCG	4	C3
\tGAATATACCTGG	ATCG	4	C4
"""

# Column headers are not incremental integers
plate_map_col_header_err = """
Plate#3	1	2	3	5	#	Who  When
A	sp001	sp004	sp006	blank4A	1	QZ	8/15/16
B	sp002	sp005	sp007	missing4B		a sample is missing
C	sp003	blank2C	blank3C	sp220
"""

# Row headers are not in alphabetical order
plate_map_row_header_err = """
Plate#4	1	2	3	4	#	Who  When
A	sp001	sp004	sp006	blank4A	1	QZ	8/15/16
B	sp002	sp005	sp007	missing4B		a sample is missing
D	sp003	blank2C	blank3C	sp220
"""

if __name__ == '__main__':
    main()
