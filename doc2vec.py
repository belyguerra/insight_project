import settings
import sqlite3
import os
import time
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from collections import namedtuple

ReviewDocument = namedtuple('ReviewDocument', 'words tags')


def main():
    print("Reading in reviews from db...")
    reviews = get_all_reviews()
    print("Done reading reviews. Read %d reviews!" % len(reviews))

    print("Building models...")
    models_by_name = build_models(reviews)
    print("Done building models!")

    # save models
    if not os.path.exists(settings.DIR_MODELS):
        os.makedirs(settings.DIR_MODELS)

    print("Saving models...")
    for model_name, model in models_by_name.items():
        full_path = os.path.join(settings.DIR_MODELS, model_name)
        model.save(full_path)
    print("Done saving models!")


def normalize_text(text):
    norm_text = text.lower()
    norm_text = norm_text.replace(u'\xa0', u' ')
    norm_text = norm_text.replace(u'\xa0', u' ')
    norm_text = norm_text.replace(u'/', u' ')
    norm_text = norm_text.replace(u'\\', u' ')
    norm_text = norm_text.replace(u'\u201C', '"')
    norm_text = norm_text.replace(u'\u201D', '"')
    norm_text = norm_text.replace(u'\u2018', '\'')
    norm_text = norm_text.replace(u'\u2019', '\'')
    norm_text = norm_text.replace('\t', ' ')
    # Pad punctuation with spaces on both sides
    for char in ['.', '"', ',', '(', ')', '!', '?', ';', ':']:
        norm_text = norm_text.replace(char, ' ' + char + ' ')
    return norm_text


# returns list of tuples
# [
#     (reviewid, normalized content of review)
# ]
def get_all_reviews():
    reviews = []
    conn = sqlite3.connect(settings.PITCHFORK_DB)
    c = conn.cursor()
    for row in c.execute(settings.SQL_GET_REVIEWS):
        # convert from utf-8
        reviewid = str(row[0])
        content = row[1]
        normcontent = normalize_text(content)
        reviews.append(
            (reviewid, normcontent)
        )

    conn.close()
    return reviews


def build_models(all_reviews):
    # hyperparameters based on preliminary evaluation of the model in jupyter notebooks
    models = [
        # PV-DBOW
        Doc2Vec(dm=0, dbow_words=1, vector_size=200, window=8, min_count=19, epochs=10, workers=settings.NUM_CORES),
        # PV-DM w/average -- used!
        Doc2Vec(dm=1, dm_mean=1, vector_size=200, window=8, min_count=19, epochs=10, workers=settings.NUM_CORES),
    ]

    # build list of ReviewDocuments from reviews
    alldocs = []
    for r in all_reviews:
        reviewid = r[0]
        normcontent = r[1]

        tag = [reviewid]
        words = gensim.utils.to_unicode(normcontent).split()
        reviewDoc = ReviewDocument(words, tag)
        alldocs.append(reviewDoc)

    models[0].build_vocab(alldocs)
    print(str(models[0]))
    for model in models[1:]:
        model.reset_from(models[0])
        print(str(model))

    models_by_name = {}
    counter = 1
    for model in models:
        models_by_name['Doc2VecModel_%d.model' % counter] = model
        counter += 1

    for model in models:
        print("Training model...")
        start = time.time()
        model.train(alldocs, total_examples=model.corpus_count, epochs=model.iter)
        end = time.time()
        print("Done training model. Took %d seconds" % (end - start))
    return models_by_name


if __name__ == '__main__':
    main()
