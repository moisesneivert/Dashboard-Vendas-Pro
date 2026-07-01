from io import StringIO

import pytest

from src.dashboard.data_sources import load_csv, load_sales_from_database
from src.dashboard.exceptions import DataSourceError
from src.dashboard.formatting import currency_brl, percentage_br


def test_load_csv():
    frame = load_csv(StringIO("a,b\n1,2\n"))
    assert frame.iloc[0, 0] == 1


def test_database_rejects_non_select():
    with pytest.raises(DataSourceError):
        load_sales_from_database("sqlite:///:memory:", "DELETE FROM sales")


def test_formatting():
    assert currency_brl(1234.5) == "R$ 1.234,50"
    assert percentage_br(12.34) == "12,3%"
