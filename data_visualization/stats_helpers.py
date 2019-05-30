import psycopg2 as psy
import matplotlib.pyplot as plt
import numpy as np


def main():
    
    return 0


def get_random_usernames(n, member_type='any'):
    """
    Connects to the local yd_records db and randomly selects n
    usernames of type: 'ayd', 'eyd', 'spectator'

    Parameters
    ----------
    n: int:
      The number of usernames to be returned.
    member_type: string:
      'ayd', 'eyd', 'spec', 'any'
      Defaults to 'any'

    Returns:
    usernames: list of strings:
      A list of n users of the requested type.
    """

    conn = connect_to_yd_records()
    cur = conn.cursor()
    table_name = ''
    if member_type == 'any':
        table_name = 'users'
    else:
        table_name = create_temp_table(member_type, cur)
        
    # Get the approximate row count.
    q = """
        SELECT COUNT(*) FROM {table};
        """.format(table=table_name)

    # The query below is faster, but only approximiate.
    # Further, it does not work with temp tables.
    # q = """
    #     SELECT reltuples AS approximate_row_count
    #     FROM pg_class WHERE relname = '{}'}';
    #     """.format(table_name)
    
    cur.execute(q)
    # Get number of rows is the first item of this tuple
    row_count = cur.fetchone()[0]
    
    queries = {
        'ayd': """
            SELECT kgs_username FROM {table}
            OFFSET (random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'eyd': """
            SELECT kgs_username FROM {table}
            OFFSET (random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'spectator': """
            SELECT kgs_username FROM {table}
            OFFSET (random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'any': """
            SELECT kgs_username FROM {table}
            OFFSET (random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count)
    }
    records = []
    for _ in range(n):
        cur.execute(queries[member_type])
        records.append(cur.fetchone()[0])
    
    cur.close()
    conn.close()

    return records
        

def create_temp_table(member_type, cur):
    """
    Given a member type ('ayd', 'eyd', 'spectator') and
    a cursor, creates a temp table of those users.
    
    Parameters
    ---------
    member_type: string:
      'ayd', 'eyd', or 'spectator'
    cur: psycopg2 cursor:
      The cursor to use while creating the table

    Returns
    -------
    temp_table_name: string
      The name of the temp table created.
    """

    type_dict = {
        'ayd':"""  
            CREATE TEMPORARY TABLE ayd_users AS (
                SELECT kgs_username FROM users
                WHERE ayd_member = true
            );
        """,
        'eyd':"""
            CREATE TEMPORARY TABLE eyd_users AS (
                SELECT kgs_username FROM users
                WHERE eyd_member = true
            );
        """,
        'spectator':"""
            CREATE TEMPORARY TABLE spectator_users AS (
                SELECT kgs_username FROM users
                WHERE ayd_member = false
                AND eyd_member = false
            );
        """
    }

    cur.execute(type_dict[member_type])

    name_dict = {
        'ayd': 'ayd_users',
        'eyd': 'eyd_users',
        'spectator': 'spectator_users'
    }
    return name_dict[member_type]


def connect_to_yd_records():
    """
    Connects to the local yd_records database.

    Parameters
    ----------
    None

    Returns
    -------
    conn: psycopg2 connection
      The connection to the yd_records db.
    """

    conn = psy.connect(
            dbname='yd_records',
            user='postgres',
            password='docker',
            host='localhost'
    )

    return conn


if __name__ == "__main__":
    main()