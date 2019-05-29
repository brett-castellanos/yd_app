from bs4 import BeautifulSoup
import psycopg2 as psy
import requests as req
from pymongo import MongoClient
from time import sleep
import random
import datetime


def main():
    # Open connects to postgres db
    # conn = psy.connect(
    #     dbname='yd_records',
    #     user='postgres',
    #     password='docker',
    #     host='localhost'
    # )

    # cur = conn.cursor()
    # q = '''
    #     SELECT kgs_username FROM users
    #     '''
    
    # cur.execute(q)
    with open('usernames.txt') as usernames:
      for username in usernames.readlines():
          print("Now scraping for {}".format(username))
          links = get_user_links(username.strip())
          print("Getting Links")
          insert_user_subpages(links)
          print('Waiting 8-20 seconds.')
          sleep(random.uniform(8, 20))

    # cur.close()
    # conn.close()

    return 0


def get_user_links(username):
    """
    Given a KGS username, returns the archive urls associated with that user.
    
    Parameters
    ----------
    username: string:
      The username on KGS
      
    Returns
    -------
    subpage_urls: list of strings
      A list containing all the urls associated with that user.
    """
    
    kgs_archive_base_url = 'https://www.gokgs.com/'
    add_old_users = '&oldAccounts=y'
    first_url = kgs_archive_base_url + 'gameArchives.jsp?user=' + username + add_old_users
    print('Going to {}'.format(first_url))
    webpage = req.get(first_url)
    soup = BeautifulSoup(webpage.text, 'html5lib')
    
    # Get all the the 'href' tags
    all_links = soup.findAll(lambda tag: tag.name == 'a'
                                     and tag.has_attr('href'))

    # Get the elements that contains an url starting with the link to this user
    sub_links = [link['href'] for link in all_links if link['href']
                  .startswith('gameArchives.jsp?user='+username)]
    
    sub_links = set([kgs_archive_base_url+link for link in sub_links])

    return list(sub_links)


def insert_user_subpages(links):
    """
    Given a list of links, inserts the html from these links into MongoDB.
    
    Parameters
    ----------
    links: list of strings
      A list of strings representing the URLs to be scraped
      
    Returns
    -------
    None
    """
    
    client, kgs_db, col_dict = get_mongo_connection('kgs', ['html'])
    html_col = col_dict['html']
    
    for link in links:
        cur_page = req.get(link)
        print('Scraping {}'.format(link))
        print(cur_page.status_code)
        cur_soup = BeautifulSoup(cur_page.text, 'html5lib')
        insert_html_to_mongo(link, cur_soup, html_col)
        print('Waiting 8-20 seconds.')
        sleep(random.uniform(8, 20))
        
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


def insert_html_to_mongo(url, soup, collection):
    """
    Given a BeautifulSoup object and a MongoDB collection,
    inserts the html into the collection.

    Parameters
    ----------
    url: str
      The URL for the soup object
    soup: BeauitifulSoup
      The html to be inserted into the collection
    collection: MongoDB Collection
      The collection into which the soup is inserted

    Returns
    -------
    None
    """
    collection.insert_one(
        {
            'url': url,
            'date_scraped': datetime.datetime.now(),
            'html': soup.prettify()
        }
    )

    return 0


# def insert_to_mongo():
#     return 0

    
# def process_user_subpage():
#     return 0


# def clean_game_table():
#     return 0


# def insert_table_to_db():
#     return 0


# def insert_row_to_db():
#     return 0


# def insert_user_to_db():
#     return 0


if __name__ == "__main__":
    main()
