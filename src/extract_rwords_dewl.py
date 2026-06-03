# Extract requested words from last 36 months of German Wiktionary wishlist
# Copyright (C) 2026 Ray Griner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

'''Extract requested words from last 36 months of German Wiktionary™ wishlist

One input file for each of the last 36 months is used. The output file is
named `../data/output/de_wishlist_no_freq.txt` and has the following
variables:
- rword: the requested word or phrase
- section: the section in the wishlist the word exists in
- months_on_list: the number of months the word has been on the list (up to
    a maximum of 36)
- german_missing: 'Y' if the line contains the text 'Deutsch fehlt'.
    Otherwise, ''.
'''

import pandas as pd
import numpy as np
import csv
import re

# Instead of using last version in May, use the below version from
# June 2, because it is right after the bot removed completed pages
# from the list.
curr_input_file = '20260602_oldid_10683750.txt'
CURR_YEAR = 2026
CURR_MONTH = 5

#TODO: treat first item in list below as most recent
input_file_yr_mo = [
#  ('20260531_oldid_10682634.txt', 2026, 5),
  ('20260430_oldid_10650365.txt', 2026, 4),
  ('20260331_oldid_10623045.txt', 2026, 3),
  ('20260228_oldid_10594681.txt', 2026, 2),
  ('20260130_oldid_10541084.txt', 2026, 1),
  ('20251222_oldid_10504332.txt', 2025, 12),
  ('20251129_oldid_10467066.txt', 2025, 11),
  ('20251030_oldid_10440010.txt', 2025, 10),
  ('20250926_oldid_10403385.txt', 2025, 9),
  ('20250831_oldid_10385277.txt', 2025, 8),
  ('20250731_oldid_10353648.txt', 2025, 7),
  ('20250628_oldid_10324930.txt', 2025, 6),
  ('20250531_oldid_10289389.txt', 2025, 5),
  ('20250430_oldid_10266852.txt', 2025, 4),
  ('20250331_oldid_10249409.txt', 2025, 3),
  ('20250228_oldid_10230741.txt', 2025, 2),
  ('20250131_oldid_10213158.txt', 2025, 1),
  ('20241231_oldid_10179618.txt', 2024, 12),
  ('20241130_oldid_10149471.txt', 2024, 11),
  ('20241031_oldid_10138585.txt', 2024, 10),
  ('20240930_oldid_10124619.txt', 2024, 9),
  ('20240831_oldid_10113868.txt', 2024, 8),
  ('20240731_oldid_10101668.txt', 2024, 7),
  ('20240630_oldid_10087785.txt', 2024, 6),
  ('20240528_oldid_10069284.txt', 2024, 5),
  ('20240430_oldid_10017329.txt', 2024, 4),
  ('20240331_oldid_9999701.txt', 2024, 3),
  ('20240229_oldid_9976361.txt', 2024, 2),
  ('20240126_oldid_9945019.txt', 2024, 1),
  ('20231231_oldid_9930947.txt', 2023, 12),
  ('20231119_oldid_9908194.txt', 2023, 11),
  ('20231027_oldid_9896518.txt', 2023, 10),
  ('20230930_oldid_9883591.txt', 2023, 9),
  ('20230831_oldid_9871006.txt', 2023, 8),
  ('20230730_oldid_9857041.txt', 2023, 7),
  ('20230630_oldid_9843260.txt', 2023, 6),
  #('20230531_oldid_9826425.txt', 2023, 5),
                   ]

NOBS = None  # 100

#df = pd.read_csv(INPUT_FILE, sep="\t", quoting=csv.QUOTE_MINIMAL)


def read_from_file(input_file, year, month):
    results = []

    with open(f'../data/input/{input_file}', 'r') as file:
        look_for_words = False
        line_counter = 0
        cat = 'other'
        section = ''
        for line in file:
            if line_counter == NOBS:
                break
            line = line.strip()
            if line == '<!-- Beginn -->':
                look_for_words = True
            if line == '<!-- Ende -->':
                look_for_words = False

            if line.startswith('== Substantive =='):
                cat = 'noun'
            elif line.startswith('== Verben =='):
                cat = 'verb'
            elif line.startswith('== '):
                cat = 'other'

            if line.startswith('== '):
                section = line

            m = re.search(r'^\*\[\[(.*?)\]\]', line)
            if m:
                rword = m.group(1)
                german_missing = 'Y' if 'Deutsch fehlt' in line else ''
                if ':' not in rword:
                    results.append((section, rword, german_missing))
            else:
                rword = ''
            #print(f'{rword=} | {line=}')
            line_counter = line_counter + 1

    df = pd.DataFrame(results, columns=['section','headword','german_missing'])
    df['months_ago'] = CURR_YEAR*12 + CURR_MONTH - (year*12 + month)
    df['prev_month'] = df.months_ago + 1

    return df

cumdf = read_from_file('/monthly/' + curr_input_file, CURR_YEAR, CURR_MONTH)
currdf = cumdf.copy()

for input_file, year, month in input_file_yr_mo:
    df = read_from_file('/monthly/' + input_file, year=year, month=month)
    cumdf = pd.concat([cumdf, df])

out_df = cumdf[['section','headword','prev_month']].merge(
         cumdf[['section','headword','months_ago']], indicator=True,
         how='left',
         left_on=['section','headword','prev_month'],
         right_on=['section','headword','months_ago'])
print(out_df._merge.value_counts())

not_in_prev = out_df[ out_df._merge == 'left_only' ]
on_since = not_in_prev.groupby(['section','headword'])['prev_month'].min()
on_since.name = 'months_on_list'

currdf = currdf.merge(on_since, how = 'left',
                      left_on=['section','headword'], right_index = True)
print(currdf.columns)

#print(cumdf[cumdf.rword == 'Abifez'])

currdf[['section','headword','months_on_list','german_missing']].to_csv(
        '../data/int_output/de_wishlist_no_freq.txt', sep='\t', index=False,
        quoting=csv.QUOTE_NONE)

currdf['Months on List'] = pd.cut(currdf.months_on_list, [0,1,2,3,6,12,18,24,30,36])

counts = currdf['Months on List'].value_counts().sort_index()

# 2. Get percentages (relative frequency * 100)
pcts = currdf['Months on List'].value_counts(normalize=True) * 100

# 3. Combine into a single table
pd.options.display.float_format = '{:.1f}'.format
freq_table = pd.DataFrame({'Count': counts, 'Percent': pcts})
print(freq_table)
print(f'Total           {len(currdf)}')
