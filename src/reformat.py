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

INPUT_FILE='../data/int_output/de_wishlist_no_freq.txt'

df = pd.read_csv(INPUT_FILE, sep='\t', quoting=csv.QUOTE_NONE)

out_df = df.copy()
#out_df = df[    ~df.rword.str.contains(' ')
#             & (~df.rword.str.contains('-'))
#             & (~df.rword.str.contains('.', regex=False))
#           ].copy()

OUTPUT_FILE = '../data/int_output/dewk_wishlist_reformat.txt'

#out_df['headword'] = out_df.rword
out_df['re1'] = out_df.headword
out_df['re2'] = ''

out_df = out_df[['section','headword','re1','re2']]

out_df = out_df.drop_duplicates(subset='headword',keep='first')

out_df.to_csv(OUTPUT_FILE, sep='\t', quoting=csv.QUOTE_NONE, index=False)
