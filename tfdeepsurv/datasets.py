"""Survival datasets preview or pre-processing module.
"""
import pandas as pd

from .vision import plot_km_survf
from .simulator import SimulatedData

def survival_stats(data, t_col="t", e_col="e", plot=False):
    """
    Print statistics of survival data to stdout.

    Parameters
    ----------
    data: pandas.DataFrame
        Survival data to watch.
    t_col: str
        Column name in data indicating time.
    e_col: str
        Column name in data indicating events or status.
    plot: boolean
        Is plot surival curve.
    """
    print("--------------- Survival Data Statistics ---------------")
    N = len(data)
    print("# Rows:", N)
    print("# Columns: %d + %s + %s" % (len(data.columns) - 2, e_col, t_col))
    print("# Events Ratio: %.2f%%" % (1.0 * data[e_col].sum() / N))
    print("# Min Time:", data[t_col].min())
    print("# Max Time:", data[t_col].max())
    print("")
    if plot:
        plot_km_survf(data, t_col="t", e_col="e")

def survival_df(data, t_col="t", e_col="e", label_col="Y", exclude_col=[]):
    """
    Transform raw dataframe to survival dataframe that could be used in model 
    training or predicting.

    Parameters
    ----------
    data: DataFrame
        Survival data to be transformed.
    t_col: str
        Column name in data indicating time.
    e_col: str
        Column name in data indicating events or status.
    label_col: str
        Name of new label in transformed survival data.
    exclude_col: list
        Columns to be excluded.

    Returns
    -------
    DataFrame:
        Transformed survival data. Negtive values in label are considered right censored.
    """
    x_cols = [c for c in data.columns if c not in [t_col, e_col] + exclude_col]

    # Negtive values are considered right censored
    data.loc[:, label_col] = data.loc[:, t_col]
    data.loc[data[e_col] == 0, label_col] = - data.loc[data[e_col] == 0, label_col]

    return data[x_cols + [label_col]]

def load_simulated_data(hr_ratio,
        N=1000, num_features=10, num_var=2,
        average_death=5, end_time=15,
        method="gaussian",
        gaussian_config={},
        seed=42):
    """
    Load simulated data generated by the exponentional distribution.

    Parameters
    ----------
    hr_ratio: int or float
        `lambda_max` hazard ratio.
    N: int
        The number of observations.
    average_death: int or float
        Average death time that is the mean of the Exponentional distribution.
    end_time: int or float
        Censoring time that represents an 'end of study'. Any death 
        time greater than end_time will be censored.
    num_features: int
        Size of observation vector. Default: 10.
    num_var: int
        Number of varaibles simulated data depends on. Default: 2.
    method: string
        The type of simulated data. 'linear' or 'gaussian'.
    gaussian_config: dict
        Dictionary of additional parameters for gaussian simulation.
    seed: int
        Random state.

    Returns
    -------
    pandas.DataFrame
        A simulated survival dataset following the given args.

    Notes
    -----
    Peter C Austin. Generating survival times to simulate cox proportional
    hazards models with time-varying covariates. Statistics in medicine,
    31(29):3946-3958, 2012.
    """
    generator = SimulatedData(hr_ratio, average_death=average_death, end_time=end_time, 
                              num_features=num_features, num_var=num_var)
    raw_data = generator.generate_data(N, method=method, gaussian_config=gaussian_config, seed=seed)
    # To DataFrame
    df = pd.DataFrame(raw_data['x'], columns=['x_' + str(i) for i in range(num_features)])
    df['e'] = raw_data['e']
    df['t'] = raw_data['t']
    return df