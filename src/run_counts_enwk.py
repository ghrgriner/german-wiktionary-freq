#    Count selected words in February 2022 Wikipedia.
#    Copyright (C) 2025, 2026 Ray Griner (rgriner_fwd@outlook.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

'''Count selected words in February 2022 Wikipedia.
'''

import csv
import os

import pandas as pd

from count_regexes import count_regexes

#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
# number of sentences in each file to process, set to 'None' for all
#NROWS = 160000
NROWS = None
IDIOM_START = 1
IDIOM_STOP = None
CHUNKSIZE = 10000
IDIOM_FILE = os.path.join('../data/int_output', 'enwk_german_lemmas_reformat.txt')
OUTPUT_FILE = os.path.join('../data/int_output', 'enwk_counts_raw.txt')
CORPUS_DIR = 'sentences'
file1 = os.path.join(CORPUS_DIR, 'dewiki-20220201-clean-notblank.txt')
CORPUS_FILES = (file1,)
#PVS_OUTPUT_FILE = os.path.join('tmp_output', 'prob_verb_stems.txt')
N_CORES = None

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def line_generator():
    all_file_ctr = 0
    #for file_index, file in enumerate(CORPUS_FILES):
    for file in CORPUS_FILES:
        with open(file, encoding='utf-8') as f:
            for ctr, line in enumerate(f):
                if NROWS is not None and ctr >= NROWS: break
                if all_file_ctr % 10000 == 0:
                    print(f"Input line: {all_file_ctr}")
                all_file_ctr += 1
                #yield file_index, line.rstrip()
                yield line.rstrip()

#------------------------------------------------------------------------------
# Main entry point
#------------------------------------------------------------------------------
if IDIOM_STOP is None:
    idiom_rows = None
else:
    idiom_rows = IDIOM_STOP - IDIOM_START
idiom_df = pd.read_csv(IDIOM_FILE, sep='\t', na_filter=False,
                       keep_default_na=False,
                       quoting=csv.QUOTE_NONE, nrows=idiom_rows)

#vf_df = pd.read_csv('input/endehw_verb_forms.txt', sep='\t',
#                    quoting=csv.QUOTE_NONE)
#vf_df['replacement'] = vf_df.replacement.fillna('')
#verb_forms = {}
#for row in vf_df[['placeholder','replacement']].values:
#    verb_forms[row[0]] = row[1]

# passing a line_generator is a bit faster than using the default
# constructed by passing `corpus_files` and `max_rows_per_file`.
count_regexes(df=idiom_df, n_cores=N_CORES, chunksize=CHUNKSIZE,
              line_generator=line_generator,
              #corpus_files=CORPUS_FILES, max_rows_per_file=NROWS,
              output_file=OUTPUT_FILE)
