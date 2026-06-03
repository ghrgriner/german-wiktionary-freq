#   Post-process counts
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

'''Post-process counts
'''

import csv
import os

import pandas as pd
import numpy as np
import re
import math

#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
INPUT_FILE = os.path.join('../data/int_output', 'enwk_counts_raw.txt')
DEWK_INPUT_FILE = '../../dump_de/german_output.txt'
OUTPUT_FILE = os.path.join('../data/int_output', 'endewk_words_freq.txt')
LEMMA_OUTPUT_FILE = os.path.join('../data/int_output','endewk_lemmas_freq.txt')
NROWS = None

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def estimate_count(word, uc_s, lc_s, uc_r, lc_r):
    div_zero = ''
    if word[0].isupper() and uc_r + lc_r > 0:
        n_est = uc_r + uc_s*(uc_r/(uc_r+lc_r))
    elif word[0].isupper():
        n_est = uc_s
        div_zero = 'Y'
    elif uc_r + lc_r > 0:
        n_est = lc_s + lc_r + uc_s*(lc_r/(uc_r+lc_r))
    else:
        n_est = lc_s + uc_s
        div_zero = 'Y'
    if not n_est:
        div_zero = ''
    return {'n_est': round(n_est), 'div_zero': div_zero}

#------------------------------------------------------------------------------
# Main entry point
#------------------------------------------------------------------------------
df = pd.read_csv(INPUT_FILE, sep='\t', na_filter=False,
                 quoting=csv.QUOTE_NONE, nrows=NROWS)

res = [ estimate_count(word, int(uc_s), int(lc_s), int(uc_r), int(lc_r)) for
        word, uc_s, lc_s, uc_r, lc_r in df[['headword','n_uc_s','n_lc_s','n_uc_r','n_lc_r']].values ]
df['n_total_est'] = [ x['n_est'] for x in res ]
df['div_zero'] = [ x['div_zero'] for x in res ]

# if headword contains word boundaries, set to missing instead of 0
# check len > 3 since start and end of word are boundaries
df['notdone'] = df.headword.map(lambda x: len(re.split(r'\b', x)) > 3)
for var in ['n_uc_s','n_lc_s','n_uc_r','n_lc_r','n_total_est','div_zero']:
    df[var] = np.where(df.notdone, '', df[var].astype(str))

df.to_csv(OUTPUT_FILE, sep='\t', quoting=csv.QUOTE_NONE, index=False)
wl_df = df[(df.lemma_en == 'Y') | (df.lemma_de == 'Y') ]
wl_df.to_csv(LEMMA_OUTPUT_FILE, sep='\t', quoting=csv.QUOTE_NONE, index=False)
#de_df = pd.read_csv(DEWK_INPUT_FILE, sep='\t', na_filter=False,
#                    usecols=['headword'],
#                    quoting=csv.QUOTE_NONE, nrows=NROWS)
#wl_df = df.merge(de_df[['headword']], on='headword', how='left', indicator=True)
#wl_df = wl_df[wl_df._merge == 'left_only']
#wl_df = wl_df.drop(['notdone','_merge'], axis=1)

wl_df['freq'] = pd.to_numeric(wl_df['n_total_est'], errors='coerce')
print(wl_df.freq.value_counts(dropna=False))
wl_df['freq cat'] = pd.cut(wl_df.freq, [0, 1, 2, 4,8,16,32,64,128,256,512,1024,2056], right=False)
print(wl_df['freq cat'].value_counts(dropna=False))

counts = wl_df['freq cat'].value_counts(dropna=False).sort_index()

# 2. Get percentages (relative frequency * 100)
pcts = wl_df['freq cat'].value_counts(normalize=True) * 100

# 3. Combine into a single table
pd.options.display.float_format = '{:.1f}'.format
freq_table = pd.DataFrame({'Count': counts, 'Percent': pcts})
print(freq_table)
print(f'Total           {len(wl_df)}')
