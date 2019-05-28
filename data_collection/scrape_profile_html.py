from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import time
import requests as req


def main():

    scrape_eyd_html()

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


def scrape_eyd_html():
    """
    Scrapes the member pages of the form:
    https://eyd.yunguseng.com/season24/profile.php?id=564 from id=1 ... 850

    Parameters
    ---------
    None

    Return
    ------
    None
    """
    # Connect to local MongoDB
    client, ayd_db, col_dict = get_mongo_connection('eyd', ['html'])
    html_col = col_dict['html']

    # Scrape each link
    for link in generate_eyd_urls():
        soup = soupify(link)
        insert_html_to_mongo(link, soup, html_col)
        time.sleep(2)

    return None


def generate_eyd_urls():
    """
    Generates urls for scraping the EYD member pages.

    Parameters
    ----------
    None

    Yields
    ------
    eyd_url: string
      'https://eyd.yunguseng.com/season24/profile.php?id=<1-850>'
    """
    prepend_address = 'https://eyd.yunguseng.com/season24/profile.php?id='
    for id in range(1, 851):
        yield prepend_address + str(id)


if __name__ == "__main__":
    main()
