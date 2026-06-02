# Overview

This project assigns frequency estimates to most entries
in the 'wishlist' of the German-language Wiktionary™. The time
each word has spent on the wishlist is also provided.

The program is applied to all entries in the [wishlist](https://de.wiktionary.org/wiki/Wiktionary:Wunschliste),
retrieved 31 May 2026. The corpus used for the frequency
estimates was a 10% sample of the February 2022 extract of the
German-language Wikipedia™ as created by Philip May, available
for download at:
    https://github.com/GermanT5/wikipedia2corpus.

The data that is most likely of interest to repository visitors
is the output file [data/output/dewk\_wishlist\_freq.txt](https://github.com/ghrgriner/german-wishlist/blob/main/data/output/dewk\_wishlist\_freq.txt)
and the variables `headword`, `n_total_est`, and `months_on_list`.
The variable `n_total_est` is an estimate that attempts to correct
for the fact that the first word in sentences are capitalized.
Otherwise, we only search for the lemma as entered in the wishlist.
That is, if 'Hund' and 'gehen' are in the wishlist, we do not
count occurrences of 'Hunde' or 'gegangen' (unless they are elsewhere
in the list).

See [LICENSE.txt](LICENSE.txt) for complete license and attribution
details for the corpus, the German-language Wiktionary, and this
repository.

# Trademark Notice
Wiktionary and Wikipedia are
trademarks of the Wikimedia Foundation and are used with the permission of
the Wikimedia Foundation. We are not endorsed by or affiliated with the
Wikimedia Foundation.

# Output File

The `dewk_wishlist_freq.txt` output file has the following variables:
- **section**: The section header from the wishlist. Section headers are
  lines starting with `'== '`.
- **headword**: Headwords are obtained from lines in the wishlist between the lines
  `<!-- Beginn -->` and `<!-- Ende -->`, and extracting (non-greedily) the text
   inside double brackets from lines starting with `*[[..]]`.
- **months_on_list** - Number of consecutive months the word or phrase has been
   on the wishlist, up to a maximum of 36 months. It is probably unusual for a
   word to go off and come back on the wishlist, but if it does, the counter
   restarts.
- **german_missing** - `'Y'` if the line in the wishlist contains the text
   'Deutsch fehlt'. Otherwise, `''`.
- **webpage**: The name of the webpage for the headword. This page might not
   exist. It's provided so that users who download the output file can easily
   check if a page has been created since the output file was created. The
   page title is quoted using `urllib.parse.quote(..., safe='')`.
- **n_uc_s** - Number of times the upper-case headword appears in the first
   position in the sentence. The first position refers to index 1 (not 0)
   after splitting the line on word boundaries. The upper-case headword refers
   to `headword` where the first character is capitalized.
- **n_lc_s** - Number of times the lower-case headword appears in the first
   position in the sentence. The lower-case headword refers to `headword` where
   the first character is made lower-case.
- **n_uc_r** - Number of times the upper-case headword appears in the rest of
   the sentence (i.e., after the first position).
- **n_lc_r** - Number of times the lower-case headword appears in the rest of
   the sentence.
- **n_total_est** - Estimated frequency correcting for capitalization. See below
   for details.
- **div_zero** - `'Y'` if the `n_` variables are not all 0 and `n_uc_r + n_lc_r == 0`.
   Otherwise, `''`.

# Methods

## Correcting for Capitalization
We try to avoid overestimating the frequency of requested non-nouns by adjusting
the frequency of words in the first position of the sentence by assuming the
relative proportion of lower-case and upper-case words in the first position
would be the same as in the rest of the sentence, if not for the fact that
the first word in sentences are capitalized.

For example, consider the requested word 'roger' (in the adjective/adverb/participle
section of the wishlist). There are ~400 occurrences of 'Roger' in the first position but no
'roger' and about ~1800 occurrences of 'Roger' in the remaining positions (but also
no 'roger'). Therefore, the estimated frequency of 'roger' is 0.

In the other direction, consider the requested word 'Statt' (in the noun section of the wishlist).
There are ~800 occurrences of 'Statt' in the first position of the sentences. In the remaining
positions of the sentences, there are 115 occurrences of 'Statt' and ~33000 of 'statt'.
So the estimate for 'Statt' is 115 + 800 * (115/33115) = 118, and not 115 + 800.

# Results

The distribution of the months on the wishlist is as follows:
| Months on List | Count | Percent |
| :---------- | :------: | :-----: |
| 1      |      82  |   0.8   |
| 2      |       3  |   0.0   |
| 3      |     153  |   1.5   |
| (3, 6]      |     663  |   6.5   |
| (6, 12]     |     241  |   2.4   |
| (12, 18]    |     265  |   2.6   |
| (18, 24]    |     109  |   1.1   |
| (24, 30]    |      46  |   0.4   |
| >30         |    8671  |  84.7   |
| Total       |   10233  | 100.0   |

The distribution of the estimated frequency in the 10% Wikipedia sample is as follows:
| Estimated Frequency | Count | Percent |
| :-------  | :---: | :-----: |
| 0       | 3981  |  41.3 |
| 1       | 1073  |  11.1 |
| [2, 4)       | 1077  |  11.2 |
| [4, 8)       |  983  |  10.2 |
| [8, 16)      |  881  |   9.1 |
| [16, 32)     |  623  |   6.5 |
| [32, 64)     |  470  |   4.9 |
| [64, 128)    |  291  |   3.0 |
| [128, 256)   |  142  |   1.5 |
| [256, 512)   |   74  |   0.8 |
| [512, 1024)  |   32  |   0.3 |
| [1024, 2056) |   13  |   0.1 |
| Missing [a]  |  593  |    -  |

[a] Frequency is missing when requested entry contains a word boundary (space, hyphen, etc.).

The 100 most-frequent words in descending frequency are as follows:

Platzierung
Foundation
Landesstraße
Austragung
Game
Dan
Board
Weihbischof
Synchronisation
Dekanat
Area
Special
Contest
YouTube
Empfangsgebäude
Bestehen
Martha
Finalrunde
Track
Radstand
Herausgabe
Einmündung
Girl
Channel
Bond
Konvent
Ida
Weltmeistertitel
Betracht
Springen
Professional
Hardcore
Hansa
Lane
Lane
Staatsrat
Ausgestaltung
demgegenüber
hiervon
Titelgewinn
Part
Petit
Remix
Endstand
Kunsthalle
Rundschau
Erliegen
Underground
Sokrates
Tell
Flash
Haager
Stadtverordnetenversammlung
Take
Fortführung
Buddy
Dora
Mittelteil
Ole
hunderte
Vernetzung
tausende
Eigenschreibweise
Turbo
Nachwahl
Traineramt
Elektro
reflektiert
hierin
Heimmannschaft
Investment
Task
Veranstaltungsort
Einstufung
Spezialisierung
Baukörper
Ottomotor
Commodore
Hürdenlauf
Verkehrsverbund
Motorleistung
Blankenburg
Querhaus
Titelsong
Hauptverwaltung
Volkskammer
Gothic
Karlheinz
Multi
Site
Volksbühne
Rosario
Torsten
Gesamtwerk
Bundesanstalt
Ausgangslage
vornherein
Mittelklasse
Pyrmont
Punktzahl
.

The estimated counts for these words range from 1841 to 283.

# Limitations
- Only the frequency of the lemma is counted.
- The frequency of requested phrases is not counted.
- There is no attempt to ensure the counts are only for German use of the
  word. For example, some frequent nouns are also English words.
- There are probably better corpora to consider than 10% of German Wikipedia.
  We used this corpus as we had previously estimated the relative frequency
  of idioms in this corpus.
- We tokenized the Wikipedia sentences on word boundaries, but it might be
  better to not tokenize on a hyphen.
- The programs were based on code we had written to estimate the frequency
  of idioms using regular expressions. Some of the variables and functions
  had their content changed without changing their (now out-of-date) names.

# Run-Time
The programs run quickly, probably in less than a minute.
