import settings
from gensim.models import Doc2Vec
import gensim.models.doc2vec
import sqlite3
import os


def main():
    reviews = get_all_reviews()
    print("Loaded %d reviews!" % len(reviews))

    PATH_MODEL = os.path.join(settings.DIR_MODELS, 'Doc2VecModel_2.model')

    model = Doc2Vec.load(PATH_MODEL)

    with open(settings.FILE_RESULTS_DOC2VEC, 'w', encoding='utf-8') as f:
        f.write('REVIEWID1\tREVIEWID2\tSIM\n')
        cnt_reviews = 0
        for reviewid, review in reviews:
            cnt_reviews += 1
            if cnt_reviews % 1000 == 0:
                print("Reached review %d!" % cnt_reviews)
            most_similar = model.docvecs.most_similar([reviewid], topn=5)
            for sim in most_similar:
                data = [
                    reviewid,
                    sim[0],
                    str(sim[1])
                ]
                f.write('\t'.join(data) + '\n')


def normalize_text(text):
    norm_text = text.lower()
    norm_text = norm_text.replace(u'\xa0', u' ')
    norm_text = norm_text.replace(u'/', u' ')
    norm_text = norm_text.replace(u'\\', u' ')
    norm_text = norm_text.replace(u'\u201C', '"')
    norm_text = norm_text.replace(u'\u201D', '"')
    norm_text = norm_text.replace(u'\u2018', '\'')
    norm_text = norm_text.replace(u'\u2019', '\'')
    norm_text = norm_text.replace('\t', ' ')
    # exclude = set(string.punctuation)
    # norm_text = ''.join(ch for ch in norm_text if ch not in exclude)
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


if __name__ == '__main__':
    main()
