import psycopg2 as psy

def main():
    fix_member_tags()
    return 0


def fix_member_tags():
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
        UPDATE users
        SET ayd_member = True
        WHERE users.kgs_username IN (
            SELECT users.kgs_username FROM users
            JOIN games
            ON users.kgs_username = games.black
            OR users.kgs_username = games.white
            WHERE games.ayd_game = true
            GROUP BY users.kgs_username
        );
        """
    
    cur.execute(q)
    conn.commit()
    
    q = """
        UPDATE users
        SET eyd_member = True
        WHERE users.kgs_username IN (
            SELECT users.kgs_username FROM users
            JOIN games
            ON users.kgs_username = games.black
            OR users.kgs_username = games.white
            WHERE games.eyd_game = true
            GROUP BY users.kgs_username
        );
        """

    cur.execute(q)
    conn.commit()

    cur.close()
    conn.close()

    return None


if __name__ == "__main__":
    main()