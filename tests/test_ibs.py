import sys
from unittest.mock import MagicMock

import pandas as pd

sys.modules.setdefault("matplotlib", MagicMock())
sys.modules.setdefault("matplotlib.pyplot", MagicMock())

from ibs import calculate_ibs


def test_calculate_ibs():
    df = pd.DataFrame({"Open": [0], "High": [2], "Low": [1], "Close": [1.5]})
    ibs_series = calculate_ibs(df)
    assert ibs_series.iloc[0] == 0.5
