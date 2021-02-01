from __future__ import annotations

import itertools
import io
import functools
import os
from typing import Any, Collection, Union, Type, Iterable, TypeVar, Callable, cast, TYPE_CHECKING
import pathlib

import tabulate
import pandas as pd
from pandas.io.sql import SQLTable, pandasSQL_builder
from pandas.io.excel._xlsxwriter import XlsxWriter
from pandas.core.indexes.base import Index
from maybe import Maybe

from .str import Str
from .enums import Enum
from .datetime import DateTime

if TYPE_CHECKING:
    from pathmagic import File


pd.set_option("max_columns", None)

PathLike = Union[str, os.PathLike, pathlib.Path]
FuncSig = TypeVar("FuncSig", bound=Callable)


def _check_import_is_available(func: FuncSig) -> FuncSig:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ModuleNotFoundError as ex:
            exception = ModuleNotFoundError(f"Use of method '{func.__name__}' requires module '{ex.name}'. Please ensure it is available by installing it with pip.")
            exception.name, exception.path = ex.name, ex.path
            raise exception

    return cast(FuncSig, wrapper)


class Series(pd.Series):
    def __getitem__(self, key):
        return self._try_native(super().__getitem__(key))

    def __iter__(self):
        for element in super().__iter__():
            yield self._try_native(element)

    def tolist(self) -> list:
        return list(self)

    def _try_native(self, element):
        try:
            return element.item()
        except AttributeError:
            return element


# noinspection PyFinal
class Frame(pd.DataFrame):
    columns: Union[Index, Iterable]

    _constructor_sliced = Series

    class InferRange(Enum):
        TRIM_SURROUNDING, STRIP_NULLS, SMALLEST_VALID = "trim_surrounding", "strip_nulls", "smallest_valid"

    class ColumnCase(Enum):
        IGNORE, SNAKE, CAMEL, PASCAL = "ignore", "snake", "camel", "pascal"

    class PathType(Enum):
        PATHMAGIC, PATHLIB, STRING = "pathmagic", "pathlib", "string"

    DEFAULT_COLUMN_CASE = ColumnCase.SNAKE
    DEFAULT_INFER_RANGE = InferRange.SMALLEST_VALID
    DEFAULT_PATH_TYPE = PathType.PATHMAGIC
    DEFAULT_SHEET_NAME = "Sheet1"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pd.DataFrame(*args, **kwargs).convert_dtypes())

    def __repr__(self) -> str:
        return f"{type(self).__name__}(rows={len(self.index)}, columns={list(self.columns)})"

    @property
    def _constructor(self) -> Type[Frame]:
        return type(self)

    def is_nan(self, val: Any) -> bool:
        return pd.isna(val)

    def to_excel(self, filepath: PathLike, sheet_name: str = None, index: bool = False, **kwargs: Any) -> PathLike:
        """Write this Frame to an xlsx file. Returns that File."""
        with ExcelWriter(filepath) as writer:
            self._write_to_excel(writer=writer, sheet_name=sheet_name, index=index, **kwargs)
        return self._get_path_constructor()(filepath)

    def to_sql(self, engine: Any, name: str, if_exists: str = "fail", index: bool = True, index_label: str = "id", primary_key: str = "id", schema: str = None, dtype: dict = None, **kwargs: Any) -> None:
        """Override of the pandas.DataFrame.to_sql() method allowing a primary key identity field to be supplied when creating the sql table."""
        table = SQLTable(name, pandasSQL_builder(engine), frame=self, index=index, if_exists=if_exists, index_label=index_label, keys=primary_key, schema=schema, dtype=dtype, **kwargs)
        table.create()
        table.insert(None)

    @_check_import_is_available
    def to_table(self, table: str, schema: str = None, database: str = None, if_exists: str = "fail", primary_key: str = "id", sql: Any = None) -> Any:
        """Load this Frame into a SQL database table using the config defaults of the sqlhandler library. An sqlhandler.Sql object can be provided to override the connection defaults."""
        from sqlhandler import Sql
        sql = sql if sql is not None else Sql.from_connection(database=database)
        return sql.frame_to_table(self, table=table, schema=schema, if_exists=Sql.Enums.IfExists(if_exists), primary_key=primary_key)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert this Frame to a pandas.DataFrame."""
        return pd.DataFrame(self)

    def sanitize_colnames(self, casing: str = None) -> Frame:
        """Strip newlines from the column names and apply arbitrary casing."""
        df: Frame = self.copy()
        df.columns = [str(colname).strip().replace("\n", "") for colname in df.columns]

        casing = Maybe(casing).else_(self.DEFAULT_COLUMN_CASE)
        if casing is not None:
            if casing == self.ColumnCase.SNAKE:
                df.columns = [Str(colname).case.snake() for colname in df.columns]
            elif casing == self.ColumnCase.CAMEL:
                df.columns = [Str(colname).case.camel() for colname in df.columns]
            elif casing == self.ColumnCase.PASCAL:
                df.columns = [Str(colname).case.pascal() for colname in df.columns]
            else:
                self.ColumnCase(casing)

        return df

    def to_ascii(self, index: bool = False, fancy: bool = True) -> str:
        """Convert this Frame to an ascii representation."""
        return str(tabulate.tabulate(self, headers=self.columns, tablefmt="fancy_grid" if fancy else "grid", showindex="never" if not index else "default"))

    @_check_import_is_available
    def to_desktop_as_excel(self, name: str, with_timestamp: bool = True, index: bool = False, **kwargs: Any) -> File:
        """Save this Frame to the current user's desktop as an xlsx file. Returns that File."""
        from pathmagic import Dir

        file = Dir.from_desktop().new_file(f"{name}_{DateTime.today().to_filetag() if with_timestamp else ''}", "xlsx")
        self.to_excel(file.path, index=index, **kwargs)
        return file

    # noinspection PyMethodOverriding
    def pivot(self, field_col: Union[pd.Series, str], value_col: Union[pd.Series, str]) -> Frame:
        """Pivot the content of this Frame."""
        field_name = field_col.name if isinstance(field_col, pd.Series) else field_col
        value_name = value_col.name if isinstance(value_col, pd.Series) else value_col

        pivoted: Frame = self.set_index([*[colname for colname in self.columns if colname not in {field_name, value_name}], field_name]).unstack(level=field_name).reset_index()
        pivoted.columns = [list(itertools.takewhile(lambda val: val, item))[-1] for item in pivoted.columns.to_flat_index()]
        return pivoted

    def unpivot(self, index_cols: list[Union[pd.Series, str]] = None, cols_to_unpivot: list[Union[pd.Series, str]] = None, field_name: str = "field", value_name: str = "value") -> Frame:
        """Unpivot the content of this Frame."""
        indexed = self.set_index(index_cols) if index_cols is not None else self.copy()

        if cols_to_unpivot is not None:
            indexed.drop([colname for colname in indexed.columns if colname not in cols_to_unpivot], axis=1, inplace=True)

        unpivoted = type(self)(indexed.stack().reset_index())
        final: Frame = unpivoted.rename(columns={unpivoted.columns[-2]: field_name, unpivoted.columns[-1]: value_name})
        final[field_name] = final[field_name].replace(True, 1).replace(False, 0)
        final.dropna(how="all", subset=list(final.columns[:-2]), inplace=True)

        return final

    def convert_dtypes(self, infer_objects: bool = True, convert_string: bool = True, convert_integer: bool = True, convert_boolean: bool = True, convert_floating: bool = True,) -> Frame:
        print(type(super().convert_dtypes()))
        return type(self)(super().convert_dtypes())

    def fillna_as_none(self) -> Frame:
        """Fill any nan values with None. Returns self."""
        df = self.copy()
        for name, col in df.iteritems():
            if col.isnull().any():
                df[name] = col.astype(object).where(pd.notnull(col), None)

        return df

    @_check_import_is_available
    def profile_report(self, *args: Any, style: dict = None, **kwargs: Any) -> Any:
        """Produce and return a pandas profile report"""
        import pandas_profiling

        style = Maybe(style).else_({'full_width': True})
        return pandas_profiling.ProfileReport(pd.DataFrame(self), *args, style=style, **kwargs)

    def profile_report_to(self, path: PathLike, *args: Any, **kwargs: Any) -> PathLike:
        """Produce a pandas profile report and return it as an html file"""
        file = self._get_path_constructor()(path)
        self.profile_report(*args, **kwargs).to_file(output_file=str(file))

        return file

    @classmethod
    def many_to_excel(cls, frames: Union[Collection[Frame], dict[str, Collection[Frame]]], filepath: os.PathLike, index: bool = False, **kwargs: Any) -> PathLike:
        """Write an iterable of Frames or a mapping of string-keys and Frame-values into an xlsx file with several sheets."""

        named_frames = frames if isinstance(frames, dict) else {f"Sheet{idx + 1}": frame for idx, frame in enumerate(frames)}

        with ExcelWriter(filepath=filepath) as writer:
            for name, frame in named_frames.items():
                frame._write_to_excel(writer=writer, sheet_name=name, index=index, **kwargs)

        return cls._get_path_constructor()(filepath)

    @classmethod
    def from_excel(cls, filepath: os.PathLike, casing: str = None, skipcols: int = 0, infer_headers: bool = True, infer_range: str = None, password: str = None, **kwargs: Any) -> Frame:
        """Reads in the specified Excel spreadsheet into a Frame. Passes on arguments to the pandas read_excel function. Optionally changes casing on column names and strips out non-ascii characters."""

        filepath = os.fspath(filepath)

        if password is None:
            frame = cls(pd.read_excel(filepath, **kwargs))
        else:
            with cls._decrypted_stream_from_xlsx(path=filepath, password=password) as stream:
                frame = cls(pd.read_excel(stream, **kwargs))

        if skipcols:
            frame = frame.iloc[:, skipcols:]

        if infer_headers:
            frame._infer_column_headers()

        frame = frame.sanitize_colnames(casing=Maybe(casing).else_(cls.DEFAULT_COLUMN_CASE))

        if infer_range := Maybe(infer_range).else_(cls.DEFAULT_INFER_RANGE):
            frame._infer_range(mode=infer_range)

        frame._infer_boolean_columns()
        return frame

    @classmethod
    def from_csv(cls, filepath: os.PathLike, casing: str = None, skipcols: int = 0, **kwargs: Any) -> Frame:
        """Reads in the specified csv file into a Frame. Passes on arguments to the pandas read_csv function. Optionally changes casing on column names and strips out non-ascii characters."""

        frame = cls(pd.read_csv(os.fspath(filepath), **kwargs))

        if skipcols:
            frame = frame.iloc[:, skipcols:]

        frame._infer_boolean_columns()
        return frame.sanitize_colnames(casing=casing)

    @classmethod
    def from_object(cls, obj: Any, private: bool = False) -> Frame:
        """Create a Frame from a single python object"""
        mappings = vars(obj) if private else {name: attr for name, attr in vars(obj).items() if not name.startswith("_")}
        return cls({name: [val] for name, val in mappings.items()})

    @classmethod
    def from_objects(cls, objects: Iterable[Any], private: bool = False) -> Frame:
        """Create a Frame from a homogenous list of python objects"""
        attrs = list(dict.fromkeys([name for obj in objects for name in vars(obj)]))
        valid_attrs = attrs if private else [name for name in attrs if not name.startswith("_")]
        return cls([tuple(vars(obj).get(attr) for attr in valid_attrs) for obj in objects], columns=valid_attrs)

    @classmethod
    @_check_import_is_available
    def _get_path_constructor(cls) -> Callable[..., PathLike]:
        if cls.DEFAULT_PATH_TYPE == Frame.PathType.PATHMAGIC:
            from pathmagic import File
            return File.from_pathlike
        elif cls.DEFAULT_PATH_TYPE == Frame.PathType.PATHLIB:
            return pathlib.Path
        elif cls.DEFAULT_PATH_TYPE == Frame.PathType.STRING:
            return os.fspath
        else:
            raise cls.PathType(cls.DEFAULT_PATH_TYPE)

    def _infer_column_headers(self) -> None:
        col_run = len(max("".join(["0" if self._value_is_null(col) else "1" for col in self.columns]).split("0")))

        longest_runs: dict[int, Any] = {}
        for index, row in self.iterrows():
            longest_runs.setdefault(len(max("".join(["0" if self._value_is_null(col) else "1" for col in row]).split("0"))), []).append(index)

        if max(longest_runs) > col_run:
            first_longest_index = longest_runs[max(longest_runs)][0]
            self.columns = [str(val) for val in self.loc[first_longest_index]]
            self.drop(self.loc[:first_longest_index].index.tolist(), axis=0, inplace=True)

    def _infer_range(self, mode: Frame.InferRange = None) -> None:
        if mode is None:
            pass

        self.InferRange(mode).map_to({
            self.InferRange.TRIM_SURROUNDING: self._trim_nulls_around_table,
            self.InferRange.STRIP_NULLS: self._strip_fully_null,
            self.InferRange.SMALLEST_VALID: self._truncate_after_valid,
        })()

    def _trim_nulls_around_table(self) -> None:
        self._drop_rows_around_table()
        self._drop_columns_around_table()

    def _strip_fully_null(self) -> None:
        self._drop_fully_null_rows()
        self._drop_fully_null_columns()

    def _truncate_after_valid(self) -> None:
        self._drop_rows_around_table()
        self._truncate_rows_after_valid()

        self._drop_columns_around_table()
        self._truncate_columns_after_valid()

    def _drop_rows_around_table(self) -> None:
        nulls = [(index, row.isnull().all()) for index, row in self.iterrows()]
        invalid_rows: list = sum([list(itertools.takewhile(lambda row: row[1], iterable)) for iterable in (nulls, reversed(nulls))], [])
        if invalid_rows:
            self.drop([index for index, isnull in invalid_rows], axis=0, inplace=True)

    def _drop_columns_around_table(self) -> None:
        nulls = [(name, col.isnull().all()) for name, col in self.iteritems()]
        invalid_cols: list = sum([list(itertools.takewhile(lambda col: self._value_is_null(col[0]) and col[1], iterable)) for iterable in (nulls, reversed(nulls))], [])
        if invalid_cols:
            self.drop([name for name, isnull in invalid_cols], axis=1, inplace=True)

    def _truncate_rows_after_valid(self) -> None:
        empty_rows = self[self.isnull().all(axis=1) == True].index.tolist()
        if empty_rows:
            self.drop(self.loc[empty_rows[0]:].index.tolist(), axis=0, inplace=True)

    def _truncate_columns_after_valid(self) -> None:
        invalid_columns = list(itertools.dropwhile(lambda val: not self._value_is_null(val), self.columns))
        if invalid_columns:
            self.drop(invalid_columns, axis=1, inplace=True)

    def _drop_fully_null_rows(self) -> None:
        self.dropna(axis=0, how="all", inplace=True)

    def _drop_fully_null_columns(self) -> None:
        self.drop([name for name, col in self.iteritems() if self._value_is_null(name) and col.isnull().all()], axis=1, inplace=True)

    def _infer_boolean_columns(self) -> None:
        for name, col in self.iteritems():
            try:
                if col.isin([True, False, None]).all():
                    unfinished = col.replace(1, True).replace(0, False)
                    self[name] = unfinished.where(unfinished.notnull(), None)
            except (TypeError, SystemError):
                pass

    def _write_to_excel(self, writer: ExcelWriter, sheet_name: str, index: bool, **kwargs: Any) -> None:
        df, sheet_name = self.convert_dtypes(), Maybe(sheet_name).else_(self.DEFAULT_SHEET_NAME)
        super(type(df), df).to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)
        df._table_from_sheet(writer[sheet_name])

    def _table_from_sheet(self, sheet: Any) -> None:
        for idx, col in enumerate(self):
            series = self[col]
            datalen, headerlen = series.astype(str).map(len).max(), len(str(series.name))
            max_len = datalen + 1 if datalen > headerlen + 3 else headerlen + 4
            sheet.set_column(idx, idx, max_len)
        sheet.add_table(0, 0, len(sheet.table) - 1, len(sheet.table[0]) - 1, {"columns": [{"header": str(name)} for name in self.columns], "style": "Table Style Light 9"})

    @staticmethod
    def _value_is_null(value: Any) -> bool:
        return any([str(value).lower().startswith("unnamed"), *[str(value).lower() == nullproxy for nullproxy in ("none", "nan", "null", "")]])

    @staticmethod
    def _decrypted_stream_from_xlsx(path: PathLike, password: str) -> io.BytesIO:
        import msoffcrypto

        with open(path, "rb") as source_stream:
            file = msoffcrypto.OfficeFile(source_stream)
            file.load_key(password=password)
            destination_stream = io.BytesIO()
            file.decrypt(destination_stream)

        return destination_stream


class ExcelWriter(XlsxWriter):
    def __init__(self, filepath: PathLike) -> None:
        super().__init__(os.fspath(filepath), engine="xlsxwriter", mode="w")

    def __getitem__(self, sheet_name: str) -> Any:
        return self.sheets.get(sheet_name)
