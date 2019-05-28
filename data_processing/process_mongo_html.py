from bs4 import BeautifulSoup
from pymongo import MongoClient
import pandas as pd
import psycopg2 as psy
import requests as req
import datetime
import re


def main():
    print("Scraping MongoDB")
    scrape_eyd_profiles()

    return 0


def get_mongo_connection(database, collections):
    """
    Connects to the local MongoDB.

    Parameters
    database: str
      The name of the MongoDB
    collections: list
      A list of strings naming the collections

    Returns
    -------
    client:
      The MongoDB client
    database:
      The MongoDB database
    collections: dict
      A dictionary with the passed strings as keys
      and the Mongo Collections as values
    """

    client = MongoClient()
    db = client[database]
    col_dict = {name: db[name] for name in collections}

    return (client, db, col_dict)


def soupify(url):
    """
    Given an url retreive the website and soupify the text.

    Parameters
    ----------
    url: str
      The full address of the website.
    logfile: str, default=None
      A file object for logging the attempt

    Returns
    -------
    soup: BeautifulSoup object
      Containins the html of the website.
    """
    try:
        webpage = req.get(url)
    except Exception as e:
        print('Failed to retrieve {}.'.format(url),
              'Error message: {}'.format(e))
        return None

    if webpage.status_code == 200:
        print('Retrieved {} at {}'
              .format(url, datetime.datetime.now()))
    else:
        print('Attempted to retreive {} at {}.'
              .format(url, datetime.datetime.now()),
              'Status Code: {}'.format(webpage.status_code))

    return BeautifulSoup(webpage.text, 'html5lib')


def scrape_ayd_profiles():
    """Scrapes all game records from the collected pages."""

    # Connect to AYD MongoDB
    client, ayd_db, col_dict = get_mongo_connection('ayd', ['html'])
    html_col = col_dict['html']

    # Iterate through html send to soup to scrape_subpage
    for link in html_col.find():
        profile_soup = BeautifulSoup(link['html'], 'html.parser')
        print("Now scraping {}".format(link['url']))
        scrape_subpage(profile_soup, 'ayd')


def scrape_eyd_profiles():
    """Scrapes all game records from the collected pages."""

    # Connect to EYD MongoDB
    client, eyd_db, col_dict = get_mongo_connection('eyd', ['html'])
    html_col = col_dict['html']

    # Iterate through html and send soup to scrape subpage
    for link in html_col.find():
        profile_soup = BeautifulSoup(link['html'], 'html.parser')
        print("Now scraping {}".format(link['url']))
        scrape_subpage(profile_soup, 'eyd')


def scrape_subpage(profile_soup, yd=None):
    """Scrapes the profile pages in MongoDB extracting the table data"""
    # Get the statistics table from the page.
    try:
        table_df = pd.read_html(
            profile_soup.prettify(),
            header=0,
            attrs={'class': 'graytable', 'cellpadding': '4'}
        )[0]
    except Exception as e:
        print(e)
        return None

    insert_user(profile_soup, yd)
    insert_game_table(table_df)

    return None


def insert_user(profile_soup, yd):

    # Get the user's name and kgs name
    p_strings = profile_soup.find(text=re.compile(r'\baka\b')).split('aka ')
    if len(p_strings) < 2 or p_strings is None:
        print("No profile on this page.")
        return None
    kgs_name = p_strings[1].strip()
    name = p_strings[0].split('of ')[1].strip().replace("'", "''")
    if len(name) == 0:
        print("No name at this profile")
        return None

    ayd_member, eyd_member = False, False

    conn = psy.connect(
        dbname='yd_records',
        user='postgres',
        password='docker',
        host='localhost'
    )

    cur = conn.cursor()

    q = '''
        SELECT * FROM "user"
        WHERE kgs_username='{}';
        '''.format(kgs_name)

    cur.execute(q)
    row = cur.fetchone()
    if row is None:
        q = '''
            INSERT INTO "user" (name, kgs_username, ayd_member, eyd_member)
            VALUES(E'{name}', '{kgs_username}', {ayd_member}, {eyd_member});
            '''.format(
                    name=name,
                    kgs_username=kgs_name,
                    ayd_member=ayd_member,
                    eyd_member=eyd_member
                )
        cur.execute(q)
        conn.commit()

    cur.close()
    conn.close()


def insert_game_table(table_df):
    # Create new_df to fill with appropriate data
    new_df = pd.DataFrame()

    # Clean out rating adjustment rows
    table_df = table_df.dropna()
    table_df = table_df[table_df['Round'] != '0']
    table_df = table_df[table_df['White'] != 'Manual Rating Reset']
    table_df = table_df[table_df['Black'] != 'Initial Rating']
    
    table_df['date'] = table_df['Tournament'].map(lambda x: x.split(',')[1].strip())
    table_df['date'] = table_df['date'].map(lambda x:  x.split('-')[1] if '-' in x else x)
    table_df['date'] = table_df['date'].map(lambda x: datetime.datetime.strptime(x, '%B %Y'))
    table_df['tournament'] = table_df['Tournament'].map(lambda x: x.split(',')[0].strip())

    new_df['tournament'] = table_df['Tournament'].map(lambda x: x.split(',')[0].replace(',', ''))

    new_df['round'] = table_df['Round'].map(int)
    new_df['black'] = table_df['Black']
    new_df['white'] = table_df['White']
    new_df['b_win'] = table_df['Result'].map(lambda x: x.startswith('B'))
    new_df['w_win'] = table_df['Result'].map(lambda x: x.startswith('W'))
    new_df['date'] = table_df['date']
    new_df['ayd_game'] = table_df['tournament'].map(lambda x: x.startswith('AYD'))
    new_df['eyd_game'] = table_df['tournament'].map(lambda x: x.startswith('EYD'))
    new_df['tournament'] = new_df['tournament'].map(lambda x: x.replace('EYD ', ''))
    new_df['tournament'] = new_df['tournament'].map(lambda x: x.replace('AYD ', ''))

    conn = psy.connect(
            dbname='yd_records',
            user='postgres',
            password='docker',
            host='localhost'
    )

    cur = conn.cursor()

    for row in new_df.itertuples():
        q = """
            INSERT INTO "game" (tournament, round, black, white, b_win, w_win, date, ayd_game, eyd_game)
            VALUES ('{t}', {r}, '{b}', '{w}', {b_win}, {w_win}, TIMESTAMP '{d}', {ayd}, {eyd})
            ON CONFLICT ON CONSTRAINT uniq_con_1
            DO NOTHING;
            """.format(
                t=row[1],
                r=row[2],
                b=row[3],
                w=row[4],
                b_win=row[5],
                w_win=row[6],
                d=row[7],
                ayd=row[8],
                eyd=row[9]
            )
        cur.execute(q)

    conn.commit()
    cur.close()
    conn.close()
    return None


if __name__ == "__main__":
    main()

# column = 'ayd_member' if yd == 'ayd' else 'eyd_member'
# q = '''
#     UPDATE "user"
#     SET {column} = True
#     WHERE kgs_username = '{kgs_name}';
#     '''.format(column=column, kgs_name=kgs_name)
