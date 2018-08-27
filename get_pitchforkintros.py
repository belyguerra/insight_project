import settings
import sqlite3
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process

NUM_PROCS = 16


def combine_files():
    with open(settings.FILE_PITCHFORK_INTROS, 'w', encoding='utf-8') as fout:
        fout.write('REVEIWID\tIMG_URL\tINTRO\n')
        for i in range(NUM_PROCS):
            filename = settings.FILE_PITCHFORK_INTROS + '_%d' % (i)
            with open(filename, 'r', encoding='utf-8') as f:
                next(f)  # skip header
                for line in f:
                    fout.write(line)


def save_intros(reviews, mod_num):
    filename = settings.FILE_PITCHFORK_INTROS + '_%d' % mod_num
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("REVIEWID\tIMG_URL\tINTRO\n")
        cnt = 0
        for reviewid, url in reviews:
            cnt += 1
            if cnt % NUM_PROCS != mod_num:
                continue

            response = requests.get(url)
            if response.status_code != 200:
                print("Warning, could not get review for reviewid = %s" % reviewid)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            intro = soup.find('div', attrs={'class': 'review-detail__abstract'})
            if not intro:
                continue

            intro = intro.find('p')
            if not intro:
                continue

            img = soup.find('div', attrs={'class': 'single-album-tombstone__art'})
            if not img:
                continue
            img = img.find('img')
            if not img:
                continue

            intro_str = intro.decode_contents()
            intro_str = intro_str.replace('\n', '').replace('\t', ' ')
            f.write('%s\t%s\t%s\n' % (reviewid, img['src'], intro_str))


def main():
    reviews = get_review_urls()
    print("Loaded %d review urls!" % len(reviews))

    cnt = 0
    procs = []
    for i in range(NUM_PROCS):
        p = Process(target=save_intros, args=(reviews, i))
        p.start()
        procs.append(p)

    print("Waiting for procs...")
    for p in procs:
        p.join()


def get_review_urls():
    reviews = []
    conn = sqlite3.connect(settings.PITCHFORK_DB)
    c = conn.cursor()
    for row in c.execute(settings.SQL_GET_URLS):
        # convert from utf-8
        reviewid = str(row[0])
        url = row[1]
        reviews.append(
            (reviewid, url)
        )

    conn.close()
    return reviews


if __name__ == '__main__':
    main()
