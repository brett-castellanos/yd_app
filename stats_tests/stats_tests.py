import scipy.stats as stats
import numpy as np
import sys
sys.path.append('../data_visualization')
import stats_helpers as sh


def main():
    ayd_users = sh.get_all_usernames('ayd')
    eyd_users = sh.get_all_usernames('eyd')
    print(len(ayd_users))
    print(len(eyd_users))


    ayd_game_counts = sh.get_game_counts(ayd_users)
    eyd_game_counts = sh.get_game_counts(eyd_users)
    print(ayd_game_counts.mean())
    print(eyd_game_counts.mean())
    print(compute_standard_error(ayd_game_counts, eyd_game_counts))

    print(stats.ttest_ind(ayd_game_counts, eyd_game_counts, equal_var=False))
    return 0


def compute_standard_error(dist_1, dist_2):
    """
    Returns the standard error of the sampling distribution.

    Parameters
    ----------
    dist_1: np.array
      The first sample values
    dist_2: np.array
      The second sample values

    Returns:
    stand_err: float
      The standard error of the sampling distribution
    """

    return np.sqrt((dist_1.std()/dist_1.shape[0]) + (dist_2.std()/dist_2.shape[0]))


def compute_dof(dist_1, dist_2):
    numerator = ((dist_1.std()**2/dist_1.shape[0]) + (dist_2.std()**2/dist_1.shape[0]))**2
    d_p1 = ((dist_1.std()**2/dist_1.shape[0])**2) / (dist_1.shape[0] - 1)
    d_p2 = ((dist_2.std()**2/dist_2.shape[0])**2) / (dist_2.shape[0] - 1)

    return int(round(numerator / (d_p1 + d_p2)))


def compute_t_statistic(dist_1, dist_2, effect):

    numerator = (dist_1.mean() - dist_2.mean()) - effect
    denom = compute_standard_error(dist_1, dist_2)

    return numerator/denom


if __name__ == "__main__":
    main()

