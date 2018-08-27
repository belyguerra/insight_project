import settings
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def main():
    reviews = get_reviews()
    print("Loaded %d reviews!" % len(reviews))

    # initialize spotify client
    client_credentials_manager = SpotifyClientCredentials(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    review_cnt = 0
    with open(settings.FILE_SPOTIFY_MATCHES, 'w', encoding='utf-8') as fMatch, open(settings.FILE_SPOTIFY_NOMATCH, 'w', encoding='utf-8') as fNoMatch:
        fMatch.write('REVIEWID\tSPOTIFY_URI\n')
        fNoMatch.write('REVIEWID\tARTIST\tALBUM\n')
        for reviewid, artist, album in reviews:
            review_cnt += 1
            if review_cnt % 1000 == 0:
                print("Reached review %d!" % review_cnt)
            norm_artist = get_normalized_artist(artist)
            norm_album = get_normalized_album(album)
            spotify_uri = search_spotify(sp, norm_artist, norm_album)
            if spotify_uri:
                fMatch.write('%s\t%s\n' % (reviewid, spotify_uri))
            else:
                fNoMatch.write('%s\t%s\t%s\n' % (reviewid, artist, album))


def search_spotify(sp, artist_q, album_q):
    results = sp.search(q='%s %s' % (artist_q, album_q), type='album')
    albums = results['albums']['items']
    for album in albums:
        artists = album['artists']
        artist_match = is_artist_match(artist_q, artists)

        if not artist_match:
            continue

        album_name = album['name']
        album_match = is_album_match(album_q, album_name)
        if album_match:
            return album['uri']

    return None


def get_normalized_artist(artist_text):
    art_norm = artist_text.lower()
    if art_norm.startswith('the ') and len(art_norm) > 4:
        art_norm = art_norm[4:]
    art_norm = art_norm.replace(' & ', ' and ')
    return art_norm


def get_normalized_album(album_text):
    norm_album = album_text.lower()
    norm_album = norm_album.replace('(', '[')
    norm_album = norm_album.replace(')', ']')
    norm_album = norm_album.replace(' & ', ' and ')
    before = norm_album
    if norm_album.endswith('ep'):
        norm_album = norm_album[:-2].strip()
    if '[' in norm_album and ']' in norm_album:
        norm_album = norm_album[:norm_album.find('[')].strip()
    if len(norm_album) == 0:
        return before
    return norm_album


def is_artist_match(artist_q, artist_list):
    norm_q = get_normalized_artist(artist_q)
    for artist in artist_list:
        norm_artistname = get_normalized_artist(artist['name'])
        if norm_artistname == norm_q:
            return True

    return False


def is_album_match(album_q, album_test):
    norm_q = get_normalized_album(album_q)
    norm_test = get_normalized_album(album_test)

    if norm_q == norm_test:
        return True
    return False


def get_reviews():
    reviews = []
    conn = sqlite3.connect(settings.PITCHFORK_DB)
    c = conn.cursor()
    for row in c.execute(settings.SQL_GET_ARTIST_ALBUM):
        # convert from utf-8
        reviewid = str(row[0])
        artist = row[1]
        album_name = row[2]
        reviews.append(
            (reviewid, artist, album_name)
        )

    conn.close()
    return reviews


if __name__ == '__main__':
    main()
