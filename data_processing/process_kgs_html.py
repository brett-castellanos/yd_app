from pymongo import MongoClient
from bs4 import BeautifulSoup
import psycopg2 as psy
import datetime
import pandas as pd
import re


def main():
    scrape_kgs_profiles()
    return 0

def get_mongo_connection(database, collections):
    """
    Connects to the local MongoDB.

    Parameters
    ----------
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


def scrape_kgs_profiles():
    """
    Scrapes all game records from the collected pages.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # Connect to KGS MongoDB
    client, kgs_db, col_dict = get_mongo_connection('kgs', ['html'])
    html_col = col_dict['html']

    for record in html_col.find():
        r_soup = BeautifulSoup(record['html'], 'html5lib')
        print('Now scraping {}'.format(record['url']))
        scrape_kgs_page(record['url'], r_soup)

    return None


def scrape_kgs_page(url, soup):
    """
    Scrapes a KGS archive page and inserts game records
    into PostgreSQL.

    Parameters
    ----------
    soup: BeautifulSoup:
      The page to be scraped

    Returns
    -------
    None
    """

    table_dfs = pd.read_html(
    soup.prettify(),
    header=0
    )
    if len(table_dfs) < 2:
        print("No record table found at {}".format(url))
        return None

    table_df = table_dfs[0]
    clean_df = clean_table(table_df)

    insert_kgs_table(clean_df)

    return None


def clean_table(table_df):
    """
    Returns a new dataframe to be inserted into PostgreSQL kgs_games table.
    Modifies the passed table.
    
    Parameters
    ----------
    table_df: Pandas Dataframe
      The table to be cleaned
    
    Returns
    -------
    clean_df: Pandas Dataframe
      Table formated to be enters into kgs_games table.
    """
    
    table_df.dropna()
    table_df = table_df[table_df['Setup'] == '19×19']
    table_df = table_df[table_df['Viewable?'] == 'Yes']
    table_df = table_df[table_df['Type'] == 'Ranked']

    clean_df = pd.DataFrame()
    clean_df['white'] = table_df['White'].map(lambda x: x.split('[')[0].strip())
    clean_df['w_rank'] = table_df['White'].map(get_kgs_rank)
    clean_df['black'] = table_df['Black'].map(lambda x: x.split('[')[0].strip())
    clean_df['b_rank'] = table_df['Black'].map(get_kgs_rank)
    clean_df['date'] = table_df['Start Time  (  GMT  )'].map(get_datetime)
    clean_df['b_win'] = table_df['Result'].map(lambda x: x.startswith('B'))
    clean_df['w_win'] = table_df['Result'].map(lambda x: x.startswith('W'))
    
    return clean_df


def get_kgs_rank(kgs_string):
    """
    Given a player + rank string from a KGS Archive Table, returns the 
    integer rank of the player.
    
    Parameters
    ----------
    kgs_string: string:
      The string containing the rank
    
    Returns
    -------
    rank_int: int:
      The rank of the player cast as an integer.
    """
    
    split_string = kgs_string.split('[')
    if len(split_string) < 2:
        return 'Null'
    rank_string = split_string[1]
    if 'p' in rank_string:
        return 10
    rank = re.findall(r'\d+', rank_string)
    if len(rank) == 0:
        return 'Null'
    else:
        rank = rank[0]
    if 'd' in rank_string:
        return int(rank)-1
    if 'k' in rank_string:
        return -1*int(rank)


def get_datetime(kgs_date_string):
    """
    Given a date string from a KGS Archive table, returns a string
    and format string for using in datetime.datetime.
    
    Parameters
    ----------
    kgs_date_string: string:
      The string to be formatted.
    
    Returns
    -------
    date_tuple: (string, string):
      A tuple containg the date string, and the format string.
    """
    # Replace / and : with spaces
    kgs_date_string = kgs_date_string.strip()
    split_strings = kgs_date_string.replace('/', ' ').replace(':', ' ').split()
    # Pad the strings if necessary
    month = int(split_strings[0])
    day = int(split_strings[1])
    year = int(split_strings[2])+2000
    hour = int(split_strings[3]) 
    minute = int(split_strings[4])
    pm = split_strings[5]
    if pm:
        hour += 12
        hour %= 24
        
    
    return datetime.datetime(year, month, day, hour=hour, minute=minute,tzinfo=datetime.timezone.utc,)


def insert_kgs_table(clean_df):
    """
    Given a Pandas DataFrame, insert that DataFrame's info
    into the PostgreSQL table 'kgs_games'
    
    Parameters
    ----------
    clean_df: Pandas DataFrame
      A table containing the information to be inserted.
      
    Returns
    -------
    None
    """
    # Open connection and cursor
    conn = psy.connect(
            dbname='yd_records',
            user='postgres',
            password='docker',
            host='localhost'
    )
    cur = conn.cursor()
    
    # For each row, insert the row into kgs_games
    for game in clean_df.itertuples():
        insert_kgs_game(cur, game)
    
    # Commit and then close connection and cursor
    conn.commit()
    cur.close()
    conn.close()
    return None


def insert_kgs_game(cursor, game):
    """
    Given a curser and game record, insert the record to kgs_games.
    
    Parameters
    ----------
    cursor: psycopg2 cursor:
      A cursor connected to PostgreSql
    game: tuple:
      A tuple containing the items to be inserted.
    
    Returns
    -------
    None
    """
    q = """
        INSERT INTO "kgs_games" (white, w_rank, black, b_rank, w_win, b_win, date)
        VALUES ('{w}', {w_rank}, '{b}', {b_rank}, {w_win}, {b_win}, TIMESTAMP '{d}')
        ON CONFLICT ON CONSTRAINT  uniq_kgs_game_con DO NOTHING     
        """.format(
        w=game[1],
        w_rank=game[2],
        b=game[3],
        b_rank=game[4],
        w_win=game[7],
        b_win=game[6],
        d=game[5],
           )
    cursor.execute(q)
    return None

if __name__ == "__main__":
    main()