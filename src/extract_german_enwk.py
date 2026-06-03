#   Extract all German entries from English Wiktionary
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

'''Extract all German entries from English Wiktionary
'''

import bz2
import xml.etree.ElementTree as ET

from collections import Counter

import pandas as pd
import csv

# This can be extracted programmatically, but we just hardcode it
XMLNS = '{http://www.mediawiki.org/xml/export-0.11/}'
# This file isn't uploaded to the repository.
INPUT_FILE = '../data/input/enwk_export/enwiktionary-2026-05-01-p6p11630545.xml.bz2'
OUTPUT_FILE = '../data/int_output/german_words_enwk.txt'
MAX_PAGES = None # int or None (no maximum)

EXCLUDE_SECTIONS = [
    '===Alternative forms===',
    '===Further reading===',
    '===See also===',
    '===Etymology===',
    '===Etymology 1===',
    '===Etymology 2===',
    '===Etymology 3===',
    '===Etymology 4===',
    '===Etymology 5===',
    '===Etymology 6===',
    '===Pronunciation===',
    '===References===',
    ]

def update_word_from_xml_dump(word, elem):
    revision_elem = elem.find(f'{XMLNS}revision')
    word.revision = int(revision_elem.find(f'{XMLNS}id').text)
    word.timestamp = revision_elem.find(f'{XMLNS}timestamp').text
    word.wikitext = revision_elem.find(f'{XMLNS}text').text

def process_bz2_xml_dump(input_file, output_file):
    page_counter = 0
    main_page_counter = 0
    german_entry_counter = 0
    selected = []
    pos = []
    defn = []
    h2s = Counter()

    with bz2.open(input_file, "rb") as f:
        context = ET.iterparse(f, events=("end",))
        
        _, root = next(context) 
        
        for event, elem in context:
            if event == 'end' and elem.tag == f'{XMLNS}page':
                page_counter = page_counter + 1
                title = elem.find(f'{XMLNS}title').text
                #print(title)
                
                if page_counter % 10000 == 0:
                    print(f'{page_counter=}')
                if MAX_PAGES is not None:
                    if page_counter == MAX_PAGES:
                        break

                # limit to pages in the main namespace. That is, the pages for
                # words and their definitions. Omits pages like
                # 'Hilfe:Beispiele', etc.
                if ':' not in title:
                    main_page_counter = main_page_counter + 1
                    #gword = Headword(headword=title, lang_code='de')
                    #update_word_from_xml_dump(gword, elem)
                    revision_elem = elem.find(f'{XMLNS}revision')
                    wikitext = revision_elem.find(f'{XMLNS}text').text
                    
                    if not wikitext:
                        print(f'WARNING: empty wikitext {title=}')
                    else:
                        #if '\n==German==' in gword.wikitext: 
                        #    german_entry_counter += 1
                        #    selected.append(title)
                        lines = wikitext.split('\n')
                        in_german = False
                        for line in lines:
                            if line == '==German==':
                                german_entry_counter += 1
                                selected.append(title)
                                pos.append('')
                                defn.append('')
                                in_german = True
                            elif line.startswith('==') and not line.startswith('==='):
                                in_german = False
                            elif in_german:
                                if (line.startswith('===') and not line.startswith('====')
                                    and line not in EXCLUDE_SECTIONS):
                                    pos[-1] = pos[-1] + ';' + line
                                if (line.startswith('# ') and line
                                    and line not in EXCLUDE_SECTIONS):
                                    if ';# ' in line[1:]:
                                         raise ValueError(f'";# " in line for {title=}')
                                    defn[-1] = defn[-1] + ';' + line
                 
                                    
                            #if line.startswith('==') and not line.startswith('==='):
                            #    h2s[line] += 1

                # Clear element once it's processed
                elem.clear()
                # Root will keep references to all of its already-cleared
                # children until it is also cleared
                root.clear()

    print(f'\n{page_counter=}')
    print(f'{main_page_counter=}')
    print(f'{german_entry_counter=}')
    print('\n')

    #for item, count in h2s.most_common():
    #    print(f"FREQ: {item}: {count}")

    out_df = pd.DataFrame(zip(selected, pos, defn), columns=['Word','pos','defn'])
    out_df.to_csv(output_file, sep='\t', quoting=csv.QUOTE_NONE, index=False)

process_bz2_xml_dump(INPUT_FILE, OUTPUT_FILE)

