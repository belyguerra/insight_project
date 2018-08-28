from flask import Flask
import settings
from flask import render_template
from flask import request
import collections
import random
from unidecode import unidecode
import bisect

application = Flask(__name__)

Review = collections.namedtuple('Review', 'reviewid artist album intro spotify_uri url image artstr')


@application.route('/')
def index():
    reviews_data, sims = get_full_dataset()
    # get random sample of reviews with similars
    sim_review_ids = random.sample(sims.keys(), settings.INDEX_NUM_RETURNED)

    reviews = [reviews_data[reviewid] for reviewid in sim_review_ids]

    return render_template('index.html', reviews=reviews)


@application.route('/review')
def review():
    reviews_data, sims = get_full_dataset()
    reviewid_q = request.args.get('reviewid')

    review_q = reviews_data[reviewid_q]._asdict()
    review_q['sim'] = 0
    review_q['is_sim'] = False
    reviews = [review_q]
    num_matches = 0
    i = 0
    while num_matches < settings.REVIEW_NUM_RETURNED - 1:
        if i == len(sims[reviewid_q]):
            break
        sim, sim_recording = sims[reviewid_q][i]
        i += 1
        if (
            sim_recording.artist == review_q['artist'] and
            sim_recording.album == review_q['album']
        ):
            continue
        sim_recording_dict = sim_recording._asdict()
        sim_recording_dict['sim'] = round(sim * 100, 2)
        sim_recording_dict['is_sim'] = True
        reviews.append(sim_recording_dict)
        num_matches += 1

    # get random sample of reviews with similars
    sim_review_ids = random.sample(sims.keys(), settings.INDEX_NUM_RETURNED)
    next_reviews = [reviews_data[reviewid] for reviewid in sim_review_ids]

    return render_template('review.html', reviews=reviews, next_reviews=next_reviews)


@application.route('/search')
def artistsearch():
    reviews_data, sims = get_full_dataset()
    art_q = request.args.get('q')

    # get random sample of reviews with similars
    sim_review_ids = random.sample(sims.keys(), settings.INDEX_NUM_RETURNED)
    next_reviews = [reviews_data[reviewid] for reviewid in sim_review_ids]

    norm_q = get_normalized_artist_name(art_q)
    artist_index = {}
    for reviewid, sim_reviews in sims.items():
        r = reviews_data[reviewid]
        if r.artstr not in artist_index:
            artist_index[r.artstr] = []
        artist_index[r.artstr].append(r)

    artist_names_list = list(artist_index.keys())
    artist_names_list.sort()

    matches = []
    while len(matches) == 0:
        if len(norm_q) == 0:
            break

        if len(norm_q) == 1 and len(art_q) > 1:
            break
        if len(norm_q) == 2 and len(art_q) > 3:
            break
        if len(norm_q) == 3 and len(art_q) > 4:
            break

        # binary search
        i = bisect.bisect_left(artist_names_list, norm_q)

        if i != len(artist_names_list) and artist_names_list[i][:len(norm_q)] == norm_q:
            # found match
            matches.append(i)
            i += 1
            while i < len(artist_names_list):
                if artist_names_list[i][:len(norm_q)] == norm_q:
                    matches.append(i)
                else:
                    break
                i += 1
            break
        norm_q = norm_q[:-1]

    matched_reviews = []
    for i in matches:
        artist_name = artist_names_list[i]
        matched_reviews += artist_index[artist_name]

    found_matches = len(matched_reviews) > 0
    return render_template('search.html', found=found_matches, reviews=matched_reviews, next_reviews=next_reviews)



def get_full_dataset():
    reviews = {}
    sims = {}

    with open(settings.FILE_INPUT, 'r', encoding='utf-8') as f:
        next(f)  # skip header
        for line in f:
            data = line.rstrip('\r\n').split('\t')
            r1 = Review(
                reviewid=data[0],
                artist=data[1],
                album=data[2],
                intro=data[3].replace('\\n',''),
                spotify_uri=data[4],
                url=data[5],
                image=data[6],
                artstr=get_normalized_artist_name(data[1])
            )
            r2 = Review(
                reviewid=data[7],
                artist=data[8],
                album=data[9],
                intro=data[10].replace('\\n',''),
                spotify_uri=data[11],
                url=data[12],
                image=data[13],
                artstr=get_normalized_artist_name(data[8])
            )
            sim = float(data[14])

            if r1.reviewid not in reviews:
                reviews[r1.reviewid] = r1
            if r2.reviewid not in reviews:
                reviews[r2.reviewid] = r2

            if r1.reviewid not in sims:
                sims[r1.reviewid] = []

            sims[r1.reviewid].append((sim, r2))

        return reviews, sims


def get_normalized_artist_name(artist_name):
    norm = artist_name.lower()
    if norm.startswith('the ') and len(norm) > 5:
        norm = norm[4:]
    norm = unidecode(norm)

    return norm


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
