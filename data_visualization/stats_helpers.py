import psycopg2 as psy
import numpy as np
import random as rand


def main():
    return 0


def get_member_counts():
    """
    Get the member count for each school and spectators.

    Parameters
    ----------
    None

    Returns
    -------
    member_counts: dictionary:
      k: 'ayd', 'eyd', 'spectator' v: count
    """
    conn = connect_to_yd_records()
    cur = conn.cursor()

    q_dict = {
        'ayd': """
        SELECT COUNT(*) FROM users
        WHERE ayd_member = true;
        """,
        'eyd': """
        SELECT COUNT(*) FROM users
        WHERE eyd_member = true;
        """,
        'spectator': """
        SELECT COUNT(*) FROM users
        WHERE ayd_member = false
        AND eyd_member = false
        """
    }

    counts = {}
    for key in q_dict.keys():
        cur.execute(q_dict[key])
        # Get the first value from the tuple
        counts[key] = cur.fetchone()[0]
    
    return counts


def get_game_counts(kgs_usernames):
    """
    Given a list of usernames, returns a list
    containing the number of games played by
    those users.
    
    Parameters
    ----------
    kgs_usernames: list of strings:
      The users to query

    Returns
    -------
    game_counts: np.array of integers
      The number of games played by each user.
    """

    conn = connect_to_yd_records()
    cur = conn.cursor()

    game_counts = []
    formatted_string = str(kgs_usernames).replace('[', '').replace(']', '')
    
    q = """
        SELECT users.kgs_username, COUNT(DISTINCT games.id)
        FROM users JOIN games
        ON users.kgs_username = games.black
        OR users.kgs_username = games.white
        WHERE users.kgs_username IN ({list})
        GROUP BY users.kgs_username; 
        """.format(list=formatted_string)

    cur.execute(q)
    results = np.array([record[1] for record in cur.fetchall()])
    cur.close()
    conn.close()
    
    return results


def jitter(n):
    """
    Returns an np.array with jitter values of length n.

    Parameters
    ----------
    n: int:
      Number of values to be generated

    Returns
    -------
    jitter: np.array:
      Jittery values between .25 and .75
    """


    return np.array([rand.uniform(.25,.75)
                    for _ in range(n)])


def get_all_usernames(member_type='any'):
    """
    Returns a list of all the users of type member_type.

    Parameters
    ----------
    member_type: string:
      'ayd', 'eyd', 'spectator', 'any'

    Returns
    -------
    usernames: list of strings:
      The list of usernames of type member_type.

    """
    conn = connect_to_yd_records()
    cur = conn.cursor()
    table_name = ''
    if member_type == 'any':
        table_name = 'users'
    else:
        table_name = create_temp_table(member_type, cur)
    
    queries = {
        'ayd': """
            SELECT kgs_username FROM {table};
        """.format(table=table_name),
        'eyd': """
            SELECT kgs_username FROM {table};
        """.format(table=table_name),
        'spectator': """
            SELECT kgs_username FROM {table};
        """.format(table=table_name),
        'any': """
            SELECT kgs_username FROM {table};
        """.format(table=table_name)
    }
    cur.execute(queries[member_type])
    records = [record[0] for record in cur.fetchall()]
    
    cur.close()
    conn.close()

    return records


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
            OFFSET floor(random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'eyd': """
            SELECT kgs_username FROM {table}
            OFFSET floor(random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'spectator': """
            SELECT kgs_username FROM {table}
            OFFSET floor(random() * {row_count})
            LIMIT 1;
        """.format(table=table_name, row_count=row_count),
        'any': """
            SELECT kgs_username FROM {table}
            OFFSET floor(random() * {row_count})
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