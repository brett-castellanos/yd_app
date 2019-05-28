import psycopg2 as psy

def main():
    fix_eyd_tags()
    return 0


def fix_eyd_tags():
    """
    Finds all games missing a game tag,
    assigns those games to EYD.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    conn = psy.connect(
        dbname='yd_records',
        user='postgres',
        password='docker',
        host='localhost'
    )

    cur = conn.cursor()

    q = """
        UPDATE games
        SET eyd_game = true
        WHERE eyd_game = false
        AND ayd_game = false;
        """
    
    cur.execute(q)
    conn.commit()
    
    cur.close()
    conn.close()

    return None

    


if __name__ == "__main__":
    main()