#   Extract lemmas from German word forms from English Wiktionary
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

'''Extract lemmas from German word forms from German Wiktionary
'''

import pandas as pd
import numpy as np
import csv

#NROWS = 10000
NROWS = None
INPUT_FILE = '../data/int_output/german_words_dewk.txt'
OUTPUT_FILE = '../data/int_output/german_lemmas_dewk.txt'

def not_lemma(x):
    return (
           '|Deklinierte Form|' in x or
           '|Konjugierte Form|' in x or
           '|Partizip II|' in x or
           '|Partizip I|' in x or
            False
           )

def any_lemma(x):
    for item in x:
        if item and not not_lemma(item):
            return 'Y'
    return 'N'
        
def pos_to_list(x):
    as_list = x.split(';')
    return as_list

df = pd.read_csv(INPUT_FILE, sep='\t', keep_default_na=False,
                 nrows=NROWS, quoting=csv.QUOTE_NONE)
df['pos_list'] = df.pos.map(pos_to_list)
df['lemma'] = df.pos_list.map(any_lemma)

#lemmas_df = df[~df.not_lemma]
#print(df.n_def.value_counts())
#print(df[df.n_def > 10])

lemmas_df = df.sort_values(['Word'])

lemmas_df[['Word','lemma','pos']].to_csv(OUTPUT_FILE, sep='\t',
                                 quoting=csv.QUOTE_NONE)

#print(df)
