import psycopg2 as psy
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import stats_helpers as sh

def main():
    #visualize_membership()
    counts = get_member_counts()

    visualize_yd_games_played('ayd', 50)
    visualize_yd_games_played('eyd', 50)

    return 0


def visualize_membership():
    """
    Plots the membership totals for each school.
    Saves the file as '/visualizations/membership_plot.png'

    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    
    counts = get_member_counts()

    plt.style.use('seaborn')
    ax = plt.subplot()

    ax.set_title('Membership Totals')
    ax.set_xlabel('Membership Type')
    ax.set_ylabel('Count')

    plt.bar(counts.keys(), counts.values())

    plt.savefig('./data_visualization/visualizations/membership_plot.png')

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
    conn = sh.connect_to_yd_records()
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


def visualize_yd_games_played(member_type, n):
    """
    Plot the distribution of games played per user
    for the given membership type.

    Saves the plot as '<member_type>_games_dist.png'

    Parameters
    ----------
    member_type: string
      'ayd', 'eyd', 'any'
    
    Returns
    -------
    None
    """
    
    user_sample = sh.get_random_usernames(n, member_type)

    game_counts = get_game_counts(user_sample)
    
    plt.style.use('seaborn')

    fig, axs = plt.subplots(2, 1, sharex=True)

    fig.suptitle('Distribution of Game Count for {}'.format(member_type))

    axs[1].set_xlabel('Game Count')
    axs[1].scatter(game_counts, sh.jitter(len(game_counts)))
    axs[1].set_yticklabels([])

    axs[0].boxplot(game_counts, vert=False)
    axs[0].set_yticklabels([])
    
    plt.savefig('./data_visualization/visualizations/{}_game_count.png'.format(member_type))
    
    return None


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

    conn = sh.connect_to_yd_records()
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


if __name__ == "__main__":
    main()

