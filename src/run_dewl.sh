# only need to do this once to get the corpus
###python3 download_sample.py
'''Run programs to get freq info for words on wishlist (Wunschliste).

The time on the wishlist to date is also calculated.
'''

python3 extract_rwords_dewl.py
python3 reformat_dewl.py
python3 run_counts_dewl.py
python3 postprocess_dewl.py
