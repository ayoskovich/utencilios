import random
import pandas as pd
import numpy as np
from unittest import mock
from utencilios import (
    shout,
    squish,
    filter_random,
    collapse_multiindex,
    DataFrameDiffer,
    pathsafenow,
)
import utencilios


def test_shout(capsys):
    start_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    output = (
        start_df.pipe(shout, "before filtering")
        .loc[lambda x: x["a"] == 1]
        .pipe(shout, "after filtering")
    )
    captured = capsys.readouterr()
    out_text = "(3, 2): before filtering\n(1, 2): after filtering\n"
    assert captured.out == out_text
    assert output.shape == (1, 2)


def test_filter_random():
    random.seed(1234)
    df_input = pd.DataFrame(
        columns=["grp", "val"], data=[("a", 15), ("a", 20), ("b", 100)]
    )
    expected_output = pd.DataFrame(columns=["grp", "val"], data=[("a", 15), ("a", 20)])
    actual_output = df_input.pipe(filter_random, "grp")
    pd.testing.assert_frame_equal(actual_output, expected_output)


def test_simple_squish():
    df_input = pd.DataFrame(
        columns=["index_var", "a_1", "a_2", "b_1", "b_2", "b_3"],
        data=[(1, 2, 3, 4, 5, 6), (10, 20, 30, 40, 50, 60)],
    )
    expected_output = pd.DataFrame(
        columns=["index_var", "group", "value"],
        data=[
            (1, "a", [2, 3]),
            (1, "b", [4, 5, 6]),
            (10, "a", [20, 30]),
            (10, "b", [40, 50, 60]),
        ],
    )
    actual_output = squish(df_input, "index_var")
    pd.testing.assert_frame_equal(actual_output, expected_output)


def test_squish_with_non_splittable_columns():
    df_input = pd.DataFrame(
        columns=["index_var", "b", "a_1", "a_2"], data=[(1, 2, 3, 4), (5, 6, 7, 8)]
    )
    expected_output = pd.DataFrame(
        columns=["index_var", "group", "value"],
        data=[(1, "a", [3, 4]), (1, "b", [2]), (5, "a", [7, 8]), (5, "b", [6])],
    )
    actual_output = squish(df_input, "index_var")
    pd.testing.assert_frame_equal(actual_output, expected_output)


def test_excel_cols():
    pass


def test_collapse_multiindex():
    df_input = (
        pd.DataFrame(columns=["g", "val"], data=[("a", 1), ("a", 3), ("b", 5)])
        .groupby("g")
        .agg({"val": [np.mean, np.std]})
    )
    expected_output = pd.DataFrame(
        {"g": ["a", "b"], "val_mean": [2, 5], "val_std": [1.414214, np.NaN]}
    )
    result = collapse_multiindex(df_input)
    pd.testing.assert_frame_equal(result, expected_output, check_dtype=False)


def test_multiple_columns_multiindex():
    input = (
        pd.DataFrame(
            {
                "grp1": np.random.choice(["a", "b", "c"], 15),
                "grp2": np.random.choice(["f", "g", "h"], 15),
                "a": np.random.random(15),
                "b": np.random.random(15),
            }
        )
        .groupby(["grp1", "grp2"])
        .agg({"a": [np.mean, np.std], "b": [min]})
    )
    result = collapse_multiindex(input)
    assert list(result.columns) == ["grp1", "grp2", "a_mean", "a_std", "b_min"]


def test_dataframe_differ():
    df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    df2 = pd.DataFrame({"a": [1, 2, 4], "B": [4, 5, 1], "c": [5, 6, 1]})
    diffy = DataFrameDiffer(df1, df2, "a")

    assert diffy.matching_columns == {"a", "b"}
    assert diffy.missing_columns == set()
    assert diffy.new_columns == {"c"}


def test_pathsafenow():
    from datetime import datetime

    with mock.patch("utencilios.general.datetime") as mock_datetime:
        # Pretend that datetime.now() will return a static date
        mock_datetime.now.return_value = datetime(2024, 8, 9, 11, 30, 5)
        actual_now = pathsafenow()
        expected_now = "2024-08-09_11-30-05"
        assert actual_now == expected_now
