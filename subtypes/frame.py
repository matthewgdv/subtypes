from __future__ import annotations

import contextlib
import itertools
import functools
import os
from typing import Any, Collection, List, Dict, Union, Type, Iterable, TypeVar, Callable, cast

import tabulate
import pandas as pd
from pandas.core.indexes.base import Index
import numpy as np

from .str import Str
from .enum import Enum
from .datetime import DateTime


PathLike = Union[str, os.PathLike]
FuncSig = TypeVar("FuncSig", bound=Callable)


def _check_import_is_available(func: FuncSig) -> FuncSig:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ModuleNotFoundError as ex:
            raise ModuleNotFoundError(f"Use of method '{func.__name__}' requires module '{ex.name}'. Please ensure it is available by installing it with pip.")

    return cast(FuncSig, wrapper)


class Frame(pd.DataFrame):
    class InferRange(Enum):
        TrimSurrounding, StripNulls, SmallestValid = "trim_surrounding", "strip_nulls", "smallest_valid"

    class ColumnCase(Enum):
        Snake, Camel, Pascal = "snake", "camel", "pascal"

    class PathType(Enum):
        PathMagic, PathLib, String = "pathmagic", "pathlib", "string"

    DEFAULT_COLUMN_CASE = ColumnCase.Snake
    DEFAULT_INFER_RANGE = InferRange.SmallestValid
    DEFAULT_PATH_TYPE = PathType.PathMagic
    DEFAULT_SHEET_NAME = "Sheet1"

    columns: Index

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        with self._using_parent_constructor():
            super().__init__(*args, **kwargs)
            self._clean_dtypes()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(rows={len(self.index)}, columns={list(self.columns)})"

    @property
    def _constructor(self) -> Type[Frame]:
        return type(self) if self._using_own_constructor() else pd.DataFrame

    def to_excel(self, filepath: PathLike, sheet_name: str = DEFAULT_SHEET_NAME, index: bool = False, **kwargs: Any) -> PathLike:
        with ExcelWriter(filepath) as writer:
            self._write_to_excel(writer=writer, sheet_name=sheet_name, index=index, **kwargs)
        return self._get_path_constructor()(filepath)

    @_check_import_is_available
    def to_alchemy(self, table: str, schema: str = None, database: str = None, if_exists: str = "fail") -> Any:
        from sqlhandler import Alchemy
        return Alchemy(schemas={schema, None}, database=database).frame_to_table(self, table=table, schema=schema, if_exists=if_exists)

    def sanitize_colnames(self, case: str = DEFAULT_COLUMN_CASE) -> Frame:
        df = self.copy()
        df.columns = [Str(str(colname)).strip().replace("\n", "") for colname in df.columns]

        if case is not None:
            clean_case = case.strip().lower()
            if clean_case == Frame.ColumnCase.Snake:
                df.columns = [Str(str(colname)).snake_case() for colname in df.columns]
            elif clean_case in [Frame.ColumnCase.Camel, Frame.ColumnCase.Pascal]:
                df.columns = [Str(str(colname)).camel_case(pascal=clean_case == Frame.ColumnCase.Pascal) for colname in df.columns]
            else:
                raise ValueError(f"Unrecognized case '{case}', must be 'snake', 'camel', or 'pascal'.")

        return df

    def to_ascii(self, index: bool = False, fancy: bool = True) -> str:
        return str(tabulate.tabulate(self, headers=self.columns, tablefmt="fancy_grid" if fancy else "grid", showindex="never" if not index else "default"))

    @_check_import_is_available
    def to_desktop_as_excel(self, name: str, with_timestamp: bool = True, index: bool = False, **kwargs: Any) -> PathLike:
        from pathmagic import Dir

        desktop = Dir.from_desktop()
        file = desktop.newfile(f"{name}_{DateTime.today().isoformat_date(dashes=False) if with_timestamp else ''}.xlsx")
        self.to_excel(file.path, index=index, **kwargs)
        return file

    def pivot(self, field_col: Union[pd.Series, str], value_col: Union[pd.Series, str]) -> Frame:
        field_name = field_col.name if isinstance(field_col, pd.Series) else field_col
        value_name = value_col.name if isinstance(value_col, pd.Series) else value_col

        pivoted = self.set_index([*[colname for colname in self.columns if colname not in {field_name, value_name}], field_name]).unstack(level=field_name).reset_index()
        pivoted.columns = [list(itertools.takewhile(lambda val: val, item))[-1] for item in pivoted.columns.to_flat_index()]
        return pivoted

    def unpivot(self, index_cols: List[Union[pd.Series, str]] = None, cols_to_unpivot: List[Union[pd.Series, str]] = None, unpivot_field_name: str = "field", unpivot_value_name: str = "value") -> Frame:
        indexed = self.set_index(index_cols) if index_cols is not None else self.copy()

        if cols_to_unpivot is not None:
            indexed.drop([colname for colname in indexed.columns if colname not in cols_to_unpivot], axis=1, inplace=True)

        unpivoted = type(self)(indexed.stack().reset_index())
        final = unpivoted.rename(columns={unpivoted.columns[-2]: unpivot_field_name, unpivoted.columns[-1]: unpivot_value_name})
        final[unpivot_field_name] = final[unpivot_field_name].replace(True, 1).replace(False, 0)
        final.dropna(how="all", subset=list(final.columns[:-2]), inplace=True)

        return final

    def infer_dtypes(self) -> Frame:
        return type(self)(self.to_dict())

    def fillna_as_none(self) -> Frame:
        df = self.copy()
        for name, col in df.iteritems():
            if col.isnull().any():
                df[name] = col.astype(object)

        return df.where(df.notnull(), None)

    @classmethod
    def many_to_excel(cls, frames: Collection[Frame], filepath: os.PathLike, index: bool = False, **kwargs: Any) -> PathLike:
        with ExcelWriter(filepath=filepath) as writer:
            for idx, frame in enumerate(frames):
                frame._write_to_excel(writer=writer, sheet_name=f"Sheet{idx + 1}", index=index, **kwargs)
        return cls._get_path_constructor()(filepath)

    @classmethod
    def from_excel(cls, filepath: os.PathLike, case: str = DEFAULT_COLUMN_CASE, skipcols: int = 0, infer_headers: bool = True, infer_range: str = DEFAULT_INFER_RANGE, password: str = None, **kwargs: Any) -> Frame:
        """Reads in the specified Excel spreadsheet into a pandas DataFrame. Passes on arguments to the pandas read_excel function. Optionally snake_cases column names and strips out non-ascii characters."""

        if password is not None:
            cls._unprotect_xlsx_file(path=filepath, password=password)

        frame = cls(pd.read_excel(os.fspath(filepath), **kwargs))

        if skipcols:
            frame = frame.iloc[:, skipcols:]

        frame = frame.sanitize_colnames(case=case)

        if infer_headers:
            frame._infer_column_headers()
            frame = frame.sanitize_colnames(case=case)

        if infer_range:
            frame._infer_range(mode=infer_range)

        return frame.infer_dtypes()

    @classmethod
    def from_object(cls, obj: Any, private: bool = False) -> Frame:
        mappings = vars(obj) if private else {name: attr for name, attr in vars(obj).items() if not name.startswith("_")}
        return cls({name: [val] for name, val in mappings.items()})

    @classmethod
    def from_objects(cls, objects: Iterable[Any], private: bool = False) -> Frame:
        attrs = list(dict.fromkeys([name for obj in objects for name in vars(obj)]))
        valid_attrs = attrs if private else [name for name in attrs if not name.startswith("_")]
        return cls([tuple(vars(obj).get(attr) for attr in valid_attrs) for obj in objects], columns=valid_attrs)

    def _using_own_constructor(self) -> None:
        return object.__getattribute__(self, "_own_constructor_")

    def _use_own_constructor(self, own: bool) -> None:
        object.__setattr__(self, "_own_constructor_", own)

    @contextlib.contextmanager
    def _using_parent_constructor(self) -> None:
        self._use_own_constructor(False)
        yield
        self._use_own_constructor(True)

    @classmethod
    @_check_import_is_available
    def _get_path_constructor(cls) -> Type[PathLike]:
        if cls.DEFAULT_PATH_TYPE == Frame.PathType.PathMagic:
            from pathmagic import File
            return File
        elif cls.DEFAULT_PATH_TYPE == Frame.PathType.PathLib:
            import pathlib
            return pathlib.Path
        elif cls.DEFAULT_PATH_TYPE == Frame.PathType.String:
            return os.fspath
        else:
            raise ValueError(f"Default path type must be one of: {Frame.PathType}.")

    def _infer_column_headers(self) -> None:
        col_run = len(max("".join(["0" if self._value_is_null(col) else "1" for col in self.columns]).split("0")))

        longest_runs: Dict[int, Any] = {}
        for index, row in self.iterrows():
            longest_runs.setdefault(len(max("".join(["0" if self._value_is_null(col) else "1" for col in row]).split("0"))), []).append(index)

        if max(longest_runs) > col_run:
            first_longest_index = longest_runs[max(longest_runs)][0]
            self.columns = [str(val) for val in self.loc[first_longest_index]]
            self.drop(self.loc[:first_longest_index].index.tolist(), axis=0, inplace=True)

    def _infer_range(self, mode: str = None) -> None:
        if mode is None:
            pass
        elif mode == Frame.InferRange.TrimSurrounding:
            self._trim_nulls_around_table()
        elif mode == Frame.InferRange.StripNulls:
            self._strip_fully_null()
        elif mode == Frame.InferRange.SmallestValid:
            self._truncate_after_valid()
        else:
            raise ValueError(f"Unrecognized mode for 'infer_range'. Valid values are: {', '.join([option.value for option in Frame.InferRange])}.")

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
        invalid_rows = sum([list(itertools.takewhile(lambda row: row[1], iterable)) for iterable in (nulls, reversed(nulls))], [])
        if invalid_rows:
            self.drop([index for index, isnull in invalid_rows], axis=0, inplace=True)

    def _drop_columns_around_table(self) -> None:
        nulls = [(name, col.isnull().all()) for name, col in self.iteritems()]
        invalid_cols = sum([list(itertools.takewhile(lambda col: self._value_is_null(col[0]) and col[1], iterable)) for iterable in (nulls, reversed(nulls))], [])
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

    def _clean_dtypes(self) -> Frame:
        for name, col in self.iteritems():
            if col.dtype.name == "float64":
                if col.apply(lambda val: val is None or np.isnan(val) or val.is_integer()).all():
                    self[name] = col.astype("Int64")

            try:
                if col.isin([True, False, None]).all():
                    unfinished = col.replace(1, True).replace(0, False)
                    self[name] = unfinished.where(unfinished.notnull(), None)
            except (TypeError, SystemError):
                pass

        return self

    def _write_to_excel(self, writer: ExcelWriter, sheet_name: str, index: bool, **kwargs: Any) -> None:
        df = self.infer_dtypes()
        super(type(df), df).to_excel(writer.writer, sheet_name=sheet_name, index=index, **kwargs)
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
    def _unprotect_xlsx_file(path: PathLike, password: str) -> None:
        import win32com.client as win

        app = win.Dispatch("Excel.Application")
        workbook = app.Workbooks.Open(path, False, False, None, password)
        app.DisplayAlerts = False
        workbook.SaveAs(path, None, "", "")
        app.Quit()


class ExcelWriter:
    def __init__(self, filepath: PathLike) -> None:
        self.writer = pd.ExcelWriter(os.fspath(filepath), engine="xlsxwriter", mode="w")

    def __enter__(self) -> ExcelWriter:
        return self

    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        self.writer.save()

    def __getitem__(self, sheet_name: str) -> Any:
        if self.writer.sheets is None:
            self.writer.add_worksheet(sheet_name)

        return self.writer.sheets.get(sheet_name)
