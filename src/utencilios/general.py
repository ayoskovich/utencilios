from string import ascii_uppercase
import random
from typing import Union, Callable
from collections import defaultdict
import pandas as pd
from datetime import datetime


def shout(df: pd.DataFrame, msg: str = None) -> pd.DataFrame:
    """A simple function to be used with ``pd.pipe`` to print out
    the size of a dataframe and an optional message.

    :param df: The input dataframe
    :param msg: The message you want to print

    :returns: The original dataframe

    Example:
        .. ipython:: python

            output = (
                pd.DataFrame([{'a': 10}, {'a': 15}, {'a': 20}])
                .pipe(ut.shout, 'Starting pipeline')
                .loc[lambda x: x['a'] >= 15]
                .pipe(ut.shout, 'After filtering')
            ); output
    """
    msg = f"{df.shape}: {msg or ''}"
    print(msg)
    return df


def collapse_multiindex(df: pd.DataFrame, sep: str = "_") -> pd.DataFrame:
    """Collapses a multi-index, this usually happens after some sort of aggregation.

    Currently only supports an index that's nested 1 level (so 2 levels)

    :param df: The input dataframe
    :param sep: A delimiter to use when joining the index values
    """
    _df = df.copy()
    index = _df.columns
    nlevels = index.nlevels
    assert nlevels == 2, f"Collapsing {nlevels} levels isn't handled yet."
    assert type(index) is pd.MultiIndex, "You must pass a dataframe with a multi-index."
    _df.columns = [sep.join([str(x) for x in v]) for v in index.values]
    _df.reset_index(inplace=True)
    return _df


def squish(
    df: pd.DataFrame,
    index_var: Union[str, list[str]],
    col_sep: str = "_",
    agg_func: Callable = list,
) -> pd.DataFrame:
    """Reshapes wide data into long format and adds a "group" column.

    :param df: The input dataframe
    :param index_var: The column or columns that uniquely identify
    :param col_sep: The thing to split the columns on
    :param agg_func: The function to use to aggregate the values. Defaults to a simple list

    Example:
        .. ipython:: python

            df = pd.DataFrame(
                columns=['index_var', 'a_1', 'a_2', 'b_1', 'b_2', 'b_3'],
                data=[
                    (1, 2, 3, 4, 5, 6),
                    (10, 20, 30, 40, 50, 60)
                ]
            )
            df

            df.pipe(squish, 'index_var')
    """
    if not isinstance(index_var, list):
        index_var = [index_var]

    def _try_split_column(colname: str) -> Union[str, None]:
        try:
            return colname.split(col_sep)[-2]
        except IndexError:
            return colname

    return (
        df.melt(id_vars=index_var, value_name="value", var_name="variable")
        .assign(group=lambda x: x["variable"].apply(_try_split_column))
        .groupby(index_var + ["group"], group_keys=False)["value"]
        .apply(lambda x: agg_func(x))
        .reset_index()
    )


def filter_random(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Returns the dataframe filtered to a random value of col.

    :param df: The input dataframe
    :param col: The column to pick a random value from
    """
    val = random.choice(df[col])
    return df.loc[lambda x: x[col] == val]


def create_column(
    df: pd.DataFrame, colname: str, func: Callable, *args, **kwargs
) -> pd.DataFrame:
    """Creates a new column using a function that takes column names as strings.

    :param df: The input dataframe
    :param colname: The name of the column you want to create
    :param func: The function to apply to the columns
    :param args: Column names to pass into ``func``


    Example:
        .. ipython:: python

            df = pd.DataFrame({
                'first': ['myfirst'],
                'last': ['mylast']
            })
            def create_name(first: str, last: str) -> str:
                return f'{last}, {first}'

            df.pipe(ut.create_column, 'mynewcolumn', create_name, 'first', 'last')
    """
    return df.assign(
        # Need to do x.apply(lambda x: func(x['col1'], x['col2'], ..., mykwarg=15))
        __newcol=lambda x: x.apply(
            lambda x: func(
                *[x[arg] for arg in args],
                **{kwarg: value for kwarg, value in kwargs.items()},
            ),
            axis=1,
        )
    ).rename(columns={"__newcol": colname})


def generate_excel_cols() -> list[str]:
    """Returns the excel index (AA) columns."""
    base = [""] + list(ascii_uppercase)
    rv = []
    for first_letter in base:
        for second_letter in ascii_uppercase:
            rv.append(f"{first_letter}{second_letter}")
    return rv


def convert_excel_to_df_cols(df: pd.DataFrame, excel_colname: str) -> str:
    """Returns the dataframe column corresponding to the
    excel_colname

    :param df: The input dataframe
    :param excel_colname: The Excel column name
    """
    excel_cols = generate_excel_cols()
    return df.columns[excel_cols.index(excel_colname)]


class DataFrameDiffer:
    """
    A class to help compare dataframes. Deals with:

    - Matching columns
    - Filtering to differing rows

    Examples

        .. ipython:: python

            df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
            df1

            df2 = pd.DataFrame({"a": [1, 2, 4], "B": [4, 5, 1], "c": [5, 6, 1]})
            df2

            # Create a DataFrameDiffer object
            diffy = ut.DataFrameDiffer(df1, df2, "a")
            diffy.print_report()
            diffy.combined

    """

    lsuffix = "__left"
    rsuffix = "__right"

    @classmethod
    def create_diff(cls, row: pd.Series, cols: list[str]) -> dict:
        """Creates a dictionary that stores changes to the columns in a row.

        :param row: A row from a dataframe
        :param cols: A list of strings
        """
        _diff = defaultdict()
        for col in cols:
            b, a = row[f"{col}{cls.lsuffix}"], row[f"{col}{cls.rsuffix}"]
            if b != a:
                _diff[col] = (b, a)
        return _diff

    def __init__(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        join_on: list[str],
        column_cleaner: Callable = lambda x: x.strip().lower(),
    ):
        self.ldata = left.copy()
        self.rdata = right.copy()

        self.join_on = join_on
        self.column_cleaner = column_cleaner

        self.ldata.columns = [column_cleaner(col) for col in self.ldata]
        self.rdata.columns = [column_cleaner(col) for col in self.rdata]

        self.join_on = [column_cleaner(key) for key in self.join_on]

        self.columns_to_compare = [
            col for col in self.matching_columns if col not in self.join_on
        ]

        def create_message(_merge_indicator: str, diff: dict) -> str:
            """
            Creates a label based on the merge indicator as well as the changes
            that have happened to the row.
            """
            if _merge_indicator == "left_only":
                return "[-] Dropped"
            elif _merge_indicator == "right_only":
                return "[+] Added"
            elif diff:
                return "[~] Changed"
            return "[ ] Untouched"

        self.combined = (
            pd.merge(
                self.ldata,
                self.rdata,
                on=self.join_on,
                indicator=True,
                how="outer",
                suffixes=(self.lsuffix, self.rsuffix),
            )
            .assign(
                diff=lambda x: x.apply(
                    lambda x: self.create_diff(x, self.columns_to_compare), axis=1
                )
            )
            .assign(
                descr=lambda x: x.apply(
                    lambda x: create_message(x["_merge"], x["diff"]), axis=1
                )
            )
        )

    @property
    def left_columns(self) -> set:
        return set(self.ldata.columns)

    @property
    def right_columns(self) -> set:
        return set(self.rdata.columns)

    @property
    def matching_columns(self) -> set:
        return self.left_columns.intersection(self.right_columns)

    @property
    def new_columns(self):
        return self.right_columns.difference(self.left_columns)

    @property
    def missing_columns(self):
        return self.left_columns.difference(self.right_columns)

    @property
    def comparable(self) -> pd.DataFrame:
        return self.combined

    def print_report(self) -> None:
        """
        Prints out a handy report of the differences.
        """
        print("-" * 15)
        print("Difference report")
        print("-" * 15)
        print("Columns:")
        print(f"Removed: {self.missing_columns or 'None'}")
        print(f"Added: {self.new_columns or 'None'}")
        print(f"Matching: {self.matching_columns or 'None'}")
        print("-" * 15)
        print("Rows:")
        print(self.combined["descr"].value_counts(dropna=False))


def create_diff(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe that contains the difference between two
    dataframes. This is meant to work on a source of data with identical
    columns. Useful for testing upserts or other inserts / deletes with
    sql.

    ``pandas.compare`` is not very useful for me bc I'm usually looking for a
    simple "added" / "deleted" / "modified"
    """
    pass


def pathsafenow() -> str:
    """Convert the current datetime into a safe string to be used as a directory name, useful
    when stashing data.

    Returns:
        str: A safe directory name string representing the current datetime.

    Example:
        .. ipython:: python

            ut.pathsafenow()
    """
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_datetime
