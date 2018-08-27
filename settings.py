import os

BASE_DIR = os.path.dirname(__file__)
PITCHFORK_DB = os.path.join(BASE_DIR, '..', 'database.sqlite')
DIR_MODELS = os.path.join(BASE_DIR, 'models')
SQL_GET_REVIEWS = 'SELECT reviewid, content FROM content'
NUM_CORES = 4

PATH_WORDVECTORS = os.path.join(
    BASE_DIR,
    # 'wiki-news-300d-1M.vec'
    'wiki.en.vec'
)

FILE_KEYPHRASES = os.path.join(BASE_DIR, 'keyphrases_v2.txt')
FILE_WORD_2_WORD_SIM = os.path.join(BASE_DIR, 'word2wordsim_v2.txt')

FILE_RESULTS_TOTALVECTOR = os.path.join(BASE_DIR, 'results_totalvector.txt')
FILE_RESULTS_WORD = os.path.join(BASE_DIR, 'results_word_v2.txt')

FILE_RESULTS_TS_UNIV_SENTENCE = os.path.join(BASE_DIR, 'phrase_sim.txt')

FILE_RESULTS_DOC2VEC = os.path.join(BASE_DIR, 'doc2vecsim_2.txt')
