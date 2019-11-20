PLEASE NOTE:
====================

This library is currently still under development. The API will likely undergo significant changes that may break any code you write with it.
The documentation will fall out of sync with the updates regularly until development slows down. Use it at your own risk.

Overview
====================

Provides subclasses for certain python builtins (str, list, dict) and common complex types (datetime, Enum, DataFrame, BeautifulSoup) which add functionality and
convenience methods/properties. Most of these have better `__repr__()` implementations than their superclass.

The `Str` class (subclasses `str`)
--------------------
* Can be sliced
* Complex slicing methods
* Regular expression operations
* Fuzzy matching
* Clipboard functionality
* Casing
* Stripping

The `List_` class (subclasses `list`)
--------------------
* Method chaining on in-place mutation methods (`list.append()`, `list.clear()` etc.)
* Complex slicing methods
* Fuzzy matching

The `Dict_` class (subclasses `dict`)
--------------------
* Method chaining on in-place mutation methods (`dict.update()`, `dict.clear()` etc.)
* filtering and getting values based on regular expressions, for keys that are strings.
* Allows its attributes to be accessed and modified using item access
* Recursively replaces dicts with `Dict_` instances when constructed and when settings an attribute or item

The `DateTime` class (subclasses `datetime.datetime`)
--------------------
* `DateTime.delta()` method (timedelta addition and subtraction using keyword arguments)
* Methods representing the DateTime in various useful formats
* FormatCode Enum, that can be used with `DateTime.strftime()` and `DateTime.strptime()`.
* Accessor objects that shadow the object's basic attributes as PascalCase (`DateTime.Year` for `DateTime.year`, `DateTime.MicroSecond` for `DateTime.microsecond` etc.) which
  return that attribute as a string in various formats, based on the available format codes of the datetime class.

The `Enum` class (subclasses `aenum.Enum`)
--------------------
* Incorporates the aenum library's `extend_enum` function directly as `Enum.extend_enum()`
* Provides `Enum.names` and `Enum.values` attributes that return lists
* A `ValueEnum` subclass which returns the value of its members on attribute access, rather than the members themselves.
* An `AutoEnum` class which does not require values to be explicitly set, and sets the values to be lowercased versions of the name

The `Markup` class (subclasses `bs4.BeautifulSoup`)
--------------------
* Ensures the 'html.parser' is selected , rather than the system's best available parser

The `Frame` class (subclasses `pandas.DataFrame`)
--------------------
* Ensures the use of the new Int64 `Series` dtype when constructed with an iterable that only contains `int` and `None` (rather than using the default float64)
* High-level methods for pivoting and unpivoting
* Change the casing of the column names
* Represent the `Frame` as ascii
* Modified `Frame.to_excel()` formats the output file to an excel table, returns a path object
* Modified `Frame.to_sql()`, with better SQL type selection, allows one of the columns (or the index) to be used as a primary key for the resulting SQL table.
* Modified `Frame.from_excel()`, capable of inferring table boundaries from messy spreadsheets using several rulesets, recasing the column names, and removing password protection
* Create a `Frame` from an iterable of homogenous objects
* Write out an iterable of Frames as a single excel document with multiple sheets.
* Other misc utility functions (eg. replacing all NaN values with None, etc.)

The `Process` class (subclasses subprocess.Popen)
--------------------
* Can print out the actual command-line call when instanciated.
* Modified `Process.wait()` method which prints any stdout to the console and returns a `CompletedProcess` rather than just a return code.

The `Color` class (subclasses colour.Color)
--------------------
* Has a `Color.Name` `Enum` which contains all the possible color names that can be passed to the `Color()` constructor.

The `Http` class (subclasses requests.Session)
--------------------
* Constructor takes a `Http(base_url=)` argument which allows subsequent request to use shortened urls.

The `NameSpace` class
--------------------
* Allows its attributes to be accessed and modified using item access/setting as well as attribute access/setting.
* Implements iteration and membership test magic methods for public members (not starting with `_`).

The `Singleton` class
--------------------
* Inherit from it to implement singletons (subclasses of `Singleton` will return the same instance whenever constucted).


Installation
====================

To install use pip:

    $ pip install pysubtypes


Or clone the repo:

    $ git clone https://github.com/matthewgdv/subtypes.git
    $ python setup.py install


Usage
====================

Detailed usage examples coming soon.

Contributing
====================

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

Report Bugs
--------------------

Report bugs at https://github.com/matthewgdv/subtypes/issues

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
--------------------

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement a fix for it.

Implement Features
--------------------

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

Write Documentation
--------------------

The repository could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

Submit Feedback
--------------------

The best way to send feedback is to file an issue at https://github.com/matthewgdv/subtypes/issues.

If you are proposing a new feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are welcome :)

Get Started!
--------------------

Before you submit a pull request, check that it meets these guidelines:

1.  If the pull request adds functionality, it should include tests and the docs should be updated. Write docstrings for any functions that are part of the external API, and add
    the feature to the README.md.

2.  If the pull request fixes a bug, tests should be added proving that the bug has been fixed. However, no update to the docs is necessary for bugfixes.

3.  The pull request should work for the newest version of Python (currently 3.7). Older versions may incidentally work, but are not officially supported.

4.  Inline type hints should be used, with an emphasis on ensuring that introspection and autocompletion tools such as Jedi are able to understand the code wherever possible.

5.  PEP8 guidelines should be followed where possible, but deviations from it where it makes sense and improves legibility are encouraged. The following PEP8 error codes can be
    safely ignored: E121, E123, E126, E226, E24, E704, W503

6.  This repository intentionally disallows the PEP8 79-character limit. Therefore, any contributions adhering to this convention will be rejected. As a rule of thumb you should
    endeavor to stay under 200 characters except where going over preserves alignment, or where the line is mostly non-algorythmic code, such as extremely long strings or function
    calls.
