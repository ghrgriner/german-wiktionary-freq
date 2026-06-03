#   Slightly reformat input file for counting frequencies
#   Copyright (C) 2026 Ray Griner (rgriner_fwd@outlook.com)
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

import pandas as pd
import numpy as np
import csv
import os

INPUT_FILE1='../data/int_output/german_lemmas_enwk.txt'
INPUT_FILE2='../data/int_output/german_lemmas_dewk.txt'
OUTPUT_FILE = '../data/int_output/enwk_german_lemmas_reformat.txt'
RECODE_MERGE = {'left_only': 'EN', 'right_only': 'DE', 'both': 'Both'}

df1 = pd.read_csv(INPUT_FILE1, sep='\t', quoting=csv.QUOTE_NONE,
                 keep_default_na=False)
df2 = pd.read_csv(INPUT_FILE2, sep='\t', quoting=csv.QUOTE_NONE,
                 keep_default_na=False)

out_df = df1.merge(df2, how='outer', on='Word', indicator=True)
#out_df = df[    ~df.rword.str.contains(' ')
#             & (~df.rword.str.contains('-'))
#             & (~df.rword.str.contains('.', regex=False))
#           ].copy()

#out_df['headword'] = out_df.rword
out_df['lemma_in'] = out_df._merge.map(lambda x: RECODE_MERGE[x])
#out_df['section'] = out_df.pos
out_df['headword'] = out_df.Word
out_df['re1'] = out_df.headword
out_df['re2'] = ''
out_df = out_df.rename(columns={'pos_x': 'pos_en', 'pos_y': 'pos_de',
                                'lemma_x': 'lemma_en', 'lemma_y': 'lemma_de'})

out_df = out_df[['headword','lemma_en','lemma_de',
                 'pos_en','pos_de','lemma_in','re1','re2']]

out_df = out_df.drop_duplicates(subset='headword',keep='first')
print(out_df.lemma_in.value_counts())

out_df.to_csv(OUTPUT_FILE, sep='\t', quoting=csv.QUOTE_NONE, index=False)
