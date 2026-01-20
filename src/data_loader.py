import pandas as pd
from typing import Optional

def load_csv(path: str, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load a CSV into a DataFrame.

    Args:
        path: Path to CSV file.
        nrows: Optional number of rows to read for quick EDA.
    Returns:
        pandas.DataFrame
    """
    return pd.read_csv(path, nrows=nrows)
