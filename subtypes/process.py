from __future__ import annotations

import os
import subprocess
from typing import Any, Union, List

PathLike = Union[str, os.PathLike]


class CompletedProcess(subprocess.CompletedProcess):
    """A subclass of subprocess.CompletedProcess which can be tested for truthiness to return whether the process was successful."""

    def __bool__(self) -> bool:
        return self.returncode == 0


class Process(subprocess.Popen):
    """
    A subclass of subprocess.Popen which automatically sets up stdout and stderr pipes, and returns utf-8 decoded str rather than bytes from its streams.
    Can print the args passed to it when starting, and has a modified Process.wait() method that prints stdout in real time.
    """

    def __init__(self, args: list[str], cwd: PathLike = None, shell: bool = False, print_call: bool = True, stdout: Any = subprocess.PIPE, stderr: Any = subprocess.STDOUT, encoding: str = "utf-8", errors: str = "replace", **kwargs: Any) -> None:
        if cwd is not None and not shell:
            raise RuntimeError("'cwd' argument not supported without 'shell=True'")

        self.args = [str(arg) for arg in args]
        if print_call:
            print(self)

        super().__init__(args=self.args, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, encoding=encoding, errors=errors, **kwargs)  # type: ignore

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(str(self))})"

    def __str__(self) -> str:
        return subprocess.list2cmdline(self.args)

    def wait(self, timeout: float = None) -> CompletedProcess:  # type: ignore
        """Wait for the process to complete. Returns CompletedProcess rather than a returncode, and prints the stdout to the console in realtime"""
        if self.stdout is None:
            return CompletedProcess(self.args, returncode=super().wait(timeout=timeout), stdout=None)
        else:
            stdout = []
            while self.poll() is None:
                line = self.stdout.readline()
                print(line, end="")
                stdout.append(line)

            return CompletedProcess(self.args, returncode=self.poll(), stdout="".join(stdout))
