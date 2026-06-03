# only need to do this once to get the corpus
###python3 download_sample.py
'''Run programs to get freq info for lemmas in en Wikt. and not de Wikt.
'''

python3 extract_german_enwk.py   # ~7m run-time
python3 extract_german_dewk.py   # 1.5m run-time
python3 limit_to_lemmas_enwk.py
python3 reformat_enwk.py
python3 run_counts_enwk.py
python3 postprocess_enwk.py
