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

'''Extract lemmas from German word forms from English Wiktionary

I doubt this is exactly the algorithm used when one searches using
the Wiktionary category, but it seems close enough. (Compare to:
https://en.wiktionary.org/wiki/Category:German_lemmas.)

It currently gives about 1k more lemmas than the Category search (~100k
total lemmas), but it also uses an export file that is a month old.
'''

import pandas as pd
import numpy as np
import csv

#NROWS = 10000
NROWS = None
INPUT_FILE = '../data/int_output/german_words_enwk.txt'
OUTPUT_FILE = '../data/int_output/german_lemmas_enwk.txt'

def not_lemma(x):
    return (
            '{{verb form of|' in x or
            '{{plural of|' in x or
            '{{inflection of|' in x or
            '{{infl of|' in x or
            '{{de-adj form of|' in x or
            '{{past participle of|' in x or
            '{{present participle of|' in x or
            '{{comparative of|' in x or
            '{{superlative of|' in x or
            False
           )

def all_not_lemmas(x):
    for item in x:
        if item and not not_lemma(item):
            return False
    return True
        
def defn_to_list(x):
    as_list = x.split(';# ')
    return as_list

df = pd.read_csv(INPUT_FILE, sep='\t', keep_default_na=False,
                 nrows=NROWS, quoting=csv.QUOTE_NONE)
df['def_list'] = df.defn.map(defn_to_list)
df['n_def'] = df.def_list.map(lambda x: len(x))
df['not_lemma'] = df.def_list.map(all_not_lemmas)

lemmas_df = df[~df.not_lemma]
#print(df.n_def.value_counts())
#print(df[df.n_def > 10])

lemmas_df = lemmas_df.sort_values(['Word'])

lemmas_df[['Word','pos','defn']].to_csv(OUTPUT_FILE, sep='\t',
                                        quoting=csv.QUOTE_NONE)

#print(df)
