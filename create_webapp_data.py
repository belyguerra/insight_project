import settings
import sqlite3


def main():
    reviewid_2_spotify = get_review_2_spotify_uri()
    reviewid_2_pitchfork = get_review_2_pitchforkimage()
    reviewid_2_url = get_review_urls()
    reviewid_2_artist_album = get_reviews_artist_album()

    with open(settings.FILE_INPUT_WEBAPP, 'w', encoding='utf-8') as fout:
        fout.write('REVIEWID1\tARTIST1\tALBUM1\tINTRO1\tSPOTIFY1\tURL1\tIMAGE1\t')
        fout.write('REVIEWID2\tARTIST2\tALBUM2\tINTRO2\tSPOTIFY2\tURL2\tIMAGE2\tSIM\n')
        with open(settings.FILE_RESULTS_DOC2VEC, 'r', encoding='utf-8') as f:
            next(f)  # skip headers
            for line in f:
                data = line.rstrip('\r\n').split('\t')
                reviewid1 = data[0]
                reviewid2 = data[1]
                sim = data[2]

                data = [
                    reviewid1,
                    reviewid_2_artist_album[reviewid1][0],
                    reviewid_2_artist_album[reviewid1][1],
                    reviewid_2_pitchfork[reviewid1][1],
                    reviewid_2_spotify[reviewid1],
                    reviewid_2_url[reviewid1],
                    reviewid_2_pitchfork[reviewid1][0],
                    reviewid2,
                    reviewid_2_artist_album[reviewid2][0],
                    reviewid_2_artist_album[reviewid2][1],
                    reviewid_2_pitchfork[reviewid2][1],
                    reviewid_2_spotify[reviewid2],
                    reviewid_2_url[reviewid2],
                    reviewid_2_pitchfork[reviewid2][0],
                    sim
                ]
                fout.write('\t'.join(data) + '\n')


def get_review_2_spotify_uri():
    review_2_spotify = {}
    with open(settings.FILE_SPOTIFY_MATCHES, 'r', encoding='utf-8') as f:
        next(f)  # skip header
        for line in f:
            data = line.rstrip('\r\n').split('\t')
            reviewid = data[0]
            spotify_uri = data[1]
            review_2_spotify[reviewid] = spotify_uri

    return review_2_spotify


def get_review_2_pitchforkimage():
    review_2_image = {}
    with open(settings.FILE_PITCHFORK_INTROS, 'r', encoding='utf-8') as f:
        next(f)  # skip header
        for line in f:
            data = line.rstrip('\r\n').split('\t')
            reviewid = data[0]
            image_url = data[1]
            intro = data[2]
            review_2_image[reviewid] = (image_url, intro)

    return review_2_image


def get_review_urls():
    reviews = {}
    conn = sqlite3.connect(settings.PITCHFORK_DB)
    c = conn.cursor()
    for row in c.execute(settings.SQL_GET_URLS):
        # convert from utf-8
        reviewid = str(row[0])
        url = row[1]
        reviews[reviewid] = url

    conn.close()
    return reviews


def get_reviews_artist_album():
    reviews = {}
    conn = sqlite3.connect(settings.PITCHFORK_DB)
    c = conn.cursor()
    for row in c.execute(settings.SQL_GET_ARTIST_ALBUM):
        # convert from utf-8
        reviewid = str(row[0])
        artist = row[1]
        album_name = row[2]
        reviews[reviewid] = (artist, album_name)

    conn.close()
    return reviews


if __name__ == '__main__':
    main()
