#    Count selected strings in corpora.
#    Copyright (C) 2025 Ray Griner (rgriner_fwd@outlook.com)
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

'''Count selected strings in corpora.
'''

#------------------------------------------------------------------------------
# File: count_regexes.py
#------------------------------------------------------------------------------

__all__ = ['count_regexes']

import csv
from dataclasses import dataclass, field
from functools import partial, reduce
import multiprocessing
import os
import re
import warnings
from collections import Counter

import pandas as pd
import numpy as np
import urllib

#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
warnings.filterwarnings('ignore', 'This pattern has match groups')

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

# entries that start with underscore are for use in separable verbs, so they
# do not have the '\b' to mark the start of the word boundary for the present
# and past forms.

#vf_df = pd.DataFrame.from_dict(VERB_FORMS, orient='index',
#                               columns=['replacement'])
#vf_df = vf_df.rename_axis('placeholder')
#vf_df.to_csv('endehw_verbforms.txt', sep='\t', quoting=csv.QUOTE_NONE)

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------
#@dataclass
#class IdiomReadRec:
#    '''Idiom information the worker threads need only read from.
#    '''
#    headword: str = ''
#    regexes: list = field(default_factory=list)
#    ic_regexes: list = field(default_factory=list)

#@dataclass
#class IdiomWriteRec:
#    '''Idiom information the worker threads will need to write to.
#    '''
#    results: list = field(default_factory=list)
#    ic_results: list = field(default_factory=list)

#------------------------------------------------------------------------------
# Globals
#------------------------------------------------------------------------------

# These are global for the multiprocessing for the reasons below. The
# encapsulation could be improved by putting the worker functions in their own
# file with these globals. This may be improved in the future.
# All these are initialized to a value that is not `None` in the `_worker_init`
# function that is called when the pool is created.
#
# The barrier should be global so that it can be initialized for each process
# before the process calls `_return_results`.
_RESULT_BARRIER = None
# These are global for efficiency reasons. The _IDIOM_READONLY won't change
# for each execution of a worker task so we choose not to send it as an
# argument for each task. The IDIOM_COUNTS will be updated for each worker task
# but we want it to maintain state across the task executions within each
# process. The alternative is sending the results out for each task, but this
# is too much interprocess communication and will be significantly slower.
#
# This is a list that the worker processes only need to read from. Each element
# is a 2-tuple and each element in the tuple is an `IdiomReadRec` object. Every
# row in the input idiom file is added to the list.
_IDIOM_READONLY = None
# Like above, but the workers will need to write to it. Each element in the
# tuple is a `IdiomWriteRec`.
_IDIOM_COUNTS = None
# Non-None value used to indicate that text should be written to the match
# file, and the workers should return a list of the text to write. Otherwise,
# the workers return `None`.
_MATCH_FILE = None

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def _quote_url(s: str) -> str:
    #return urllib.parse.quote(s.replace(' ','_'), safe='')
    return urllib.parse.quote(s, safe='')

def _add_caps(x):
    if x[0].isupper() or not x[0].isalpha():
        return r'\b' + x + r'\b'
    else:
        return r'\b[' + x[0].upper() + x[0] + ']' + x[1:] + r'\b'

def _makeuc(x):
    return x[0].upper() + x[1:]

def _makelc(x):
    return x[0].lower() + x[1:]

# ctr and note_id are currently unused but might be wanted when debugging
def _process_one_re(headword, relist_as_str, prob_verb_stems,
                    idiom_readonly, idiom_counts, re_idx):
    if not relist_as_str:
        raise ValueError('empty regex not allowed')

    regex = relist_as_str

    regex = regex.strip()

    #regex = _add_caps(regex)
    #regex = r'\b' + regex + r'\b'
    #regex.replace('ß','(ß|ss)')

    idiom_counts[0][_makeuc(regex)] = 0
    idiom_counts[1][_makelc(regex)] = 0
    idiom_counts[2][_makeuc(regex)] = 0
    idiom_counts[3][_makelc(regex)] = 0

def _fmt_one_output(word, idiom_readonly, idiom_counts, re_idx):
    return {'n_uc_s': idiom_counts[0][_makeuc(word)],
            'n_lc_s': idiom_counts[1][_makelc(word)],
            'n_uc_r': idiom_counts[2][_makeuc(word)],
            'n_lc_r': idiom_counts[3][_makelc(word)],
           }

def _fmt_output(rl_entry, idiom_readonly, idiom_counts):
    return {'re1': _fmt_one_output(rl_entry,
                                   idiom_readonly, idiom_counts, 1),
           #'re2': _fmt_one_output(rl_entry,
           #                       idiom_readonly, idiom_counts, 2)
           }

def _return_results(_):
    _RESULT_BARRIER.wait()
    return _IDIOM_COUNTS

def _worker_init(barrier, match_file, idiom_readonly, idiom_counts):
    global _RESULT_BARRIER
    global _IDIOM_READONLY
    global _IDIOM_COUNTS
    global _MATCH_FILE
    _RESULT_BARRIER = barrier
    _IDIOM_READONLY = idiom_readonly
    _IDIOM_COUNTS = idiom_counts
    _MATCH_FILE = match_file

def _process_corpus_row(x):
    ret_val = []
    tokens = re.split(r'\b', x)
    for idx, token in enumerate(tokens):
        if not token:
            continue

        #if idx == 0:
        #    print(f'WARNING: Unexpected index! {token=}, {x=}')

        if idx == 1:
            if token in _IDIOM_COUNTS[0]:
                _IDIOM_COUNTS[0][token] += 1
            elif token in _IDIOM_COUNTS[1]:
                _IDIOM_COUNTS[1][token] += 1
        elif idx > 1:
            if token in _IDIOM_COUNTS[2]:
                _IDIOM_COUNTS[2][token] += 1
            elif token in _IDIOM_COUNTS[3]:
                _IDIOM_COUNTS[3][token] += 1

    if not ret_val:
        ret_val = None
    return ret_val

def _process_idiom(headword, re1, re2, prob_verb_stems,
                   idiom_readonly, idiom_counts):
    _process_one_re(headword, re1, prob_verb_stems,
                    idiom_readonly, idiom_counts, 1)
#    #_process_one_re(headword, re2, prob_verb_stems,
#    #                idiom_readonly, idiom_counts, 2)

def _reduce_counts(rcvd, idiom_counts):
    '''Add the results from a worker to total.
    '''
    return (rcvd[0] + idiom_counts[0],
            rcvd[1] + idiom_counts[1],
            rcvd[2] + idiom_counts[2],
            rcvd[3] + idiom_counts[3],
           )

def _sum_counts(x, y):
    '''Add the results from two ragged arrays.
    '''
    tmp = _reduce_counts(x, y)
    #print(f'REDUCING RESULT: {tmp}')
    return tmp

def default_line_generator(corpus_files, max_rows_per_file):
    all_file_ctr = 0
    #for file_index, file in enumerate(corpus_files):
    for file in corpus_files:
        with open(file, encoding='utf-8') as f:
            for ctr, line in enumerate(f):
                if (max_rows_per_file is not None
                    and ctr >= max_rows_per_file): break
                if all_file_ctr % 10000 == 0:
                    print(f"Input line: {all_file_ctr}")
                all_file_ctr += 1
                #yield file_index, line.rstrip()
                yield line.rstrip()

def count_regexes(df, output_file, chunksize,
                  n_cores=None,
                  line_generator=None,
                  corpus_files=None, max_rows_per_file=None,
                  match_file=None):
    '''Count regular expression combinations in corpora.

    This is the public interface to this module. See the module docstring
    for a description of module functionality.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame containing the idioms. This should contain the variables
        `headword`, `re1`, and `re2`. It should not contain a variable
        `_counter` as this will be temporarily created to store the sort
        order at input.
    output_file : str
        File name of output file. The output is tab-delimited with no
        quoting. It will be the `df` data frame plus the columns
        `verb_search_cat_N`, `n_cum_N`, `n_ic_cum_N`, where `N` is
        replaced by 1.
    chunksize : int
        Chunk size to pass to `multiprocessing.imap_unordered`, which
        distributes the tasks among the `n_cores` processes.
    n_cores : int (>0) or None [default]
        Number of cores to use for multiprocessing the input corpus files.
        If 0, then no multiprocessing is used. If `None`, this will be set
        to `os.process_cpu_count()` which (at the time of this writing) is
        also the default `multiprocessing.Pool()` would use if `None` were
        passed.
    line_generator : Callable[] or None
        A generator that takes no arguments and yields lines of text from
        the input files. If `None`, the default generator iterates over
        `corpus_files` and reads `max_rows_per_file` from each, with a
        status message printed every 1000 lines to standard output.
        See `default_line_generator` for details.
    corpus_files : iterable[str]
        This is an iterable container of file names containing the text
        from the corpus (e.g., a list[str] or tuple[str]). This is only
        used if `line_generator is None`.
    max_rows_per_file : int or None
        The maximum number of rows to read from each file in
        `corpus_files`. This is used if `line_generator is None`. This can
        also be set to 0 to suppress the check we perform `os.access`
    match_file : str or None
        If not `None`, then all matches for the `re1` case-insenstive
        pattern will be written to this file.

    Results
    -------
    Nothing is returned (so an implicit `None`)
    '''

    if line_generator is None and corpus_files is None:
        raise ValueError('count_regexes: `line_generator` or '
                         '`corpus_files` must be set')
    elif line_generator is None:
        line_generator = partial(default_line_generator,
                                 corpus_files, max_rows_per_file)
    else:
        if corpus_files is not None:
            print('WARNING: `corpus_files` will be ignored since '
                  '`line_generator` was set.')
        if max_rows_per_file is not None:
            print('WARNING: `max_rows_per_file` will be ignored since '
                  '`line_generator` was set.')

    if n_cores is None:
        n_cores = os.process_cpu_count()

    result_barrier = multiprocessing.Barrier(n_cores)

    if '_counter' in df:
        raise ValueError('`_counter` already in input data frame')
    else:
        df['_counter'] = range(len(df))
    if df.headword.duplicated().any():
        print(df.headword[df.headword.duplicated()])
        raise ValueError('count_regexes: Duplicate headwords in `df`')

    # Sort by re1 to increase likelihood of cache hits.
    df = df.sort_values(['re1','_counter'])
    df['webpage'] = ('https://de.wiktionary.org/wiki/' +
                     df.headword.map(_quote_url))

    prob_verb_stems = {}
    # Leave empty here
    idiom_readonly = []
    # token in first position, word starts with upper
    # token in first position, word starts with lower
    # token in > 1st position, word starts with upper
    # token in > 1st position, word starts with lower
    idiom_counters = (Counter(), Counter(), Counter(), Counter())
    for row in df[['headword','re1','re2']].values:
        _process_idiom(headword=row[0], re1=row[1], re2=row[2],
                       prob_verb_stems=prob_verb_stems,
                       idiom_readonly=idiom_readonly,
                       idiom_counts=idiom_counters)

    if n_cores != 0:
        with multiprocessing.Pool(processes=n_cores,
                 initializer=_worker_init,
                 initargs=(result_barrier, match_file,
                           idiom_readonly, idiom_counters)) as pool:
            if match_file is None:
                for _ in pool.imap_unordered(_process_corpus_row,
                                line_generator(), chunksize=chunksize):
                    pass
            else:
                with open(match_file, 'w', encoding='utf-8') as f:
                    for result in pool.imap_unordered(_process_corpus_row,
                                    line_generator(), chunksize=chunksize):
                        if result is not None:
                            for val in result:
                                f.write(val + '\n')

            idiom_counters = reduce( _sum_counts,
                                  pool.imap_unordered(_return_results,
                                                     [0]*n_cores, chunksize=1))
    else:
        _worker_init(result_barrier, match_file, idiom_readonly, idiom_counters)
        if match_file is None:
            for line in line_generator():
                _process_corpus_row(line)
        else:
            with open(match_file, 'w', encoding='utf-8') as f:
                for line in line_generator():
                    result = _process_corpus_row(line)
                    if result is not None:
                        for val in result:
                            f.write(val + '\n')
        idiom_counters = _IDIOM_COUNTS

    ret_val = [ _fmt_output(x, idiom_readonly, idiom_counters)
                for x in df.headword ]

    varlist = ['n_uc_s','n_lc_s','n_uc_r','n_lc_r']
    indices = ['1']
    for ix in indices:
        for var in varlist:
            df[ var ] = [ x['re' + ix][var] for x in ret_val]

    df = df.sort_values(['_counter'])

    # if headword contains word boundaries, set to missing instead of 0
    # check len > 3 since start and end of word are boundaries
    df['notdone'] = df.headword.map(lambda x: len(re.split(r'\b', x)) > 3)
    #for var in varlist:
    #    df[var] = np.where(df.notdone, '', df[var].astype(str))

    df = df.drop(['_counter','re1','re2','notdone'], axis=1)
    df.to_csv(output_file, sep='\t', quoting=csv.QUOTE_NONE, index=False)
