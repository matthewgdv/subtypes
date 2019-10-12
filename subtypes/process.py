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
    """A subclass of subprocess.Popen which can print the args passed to it when starting, and has a modified Process.wait() method."""

    def __init__(self, args: List[str], cwd: PathLike = None, shell: bool = False, print_call: bool = True, stdout: Any = subprocess.PIPE, stderr: Any = subprocess.STDOUT, encoding: str = "utf-8", errors: str = "replace", text: bool = True, **kwargs: Any) -> None:
        if cwd is not None and not shell:
            raise RuntimeError("'cwd' argument not supported without 'shell=True'")

        args = [str(arg) for arg in args]
        if print_call:
            print(subprocess.list2cmdline(args))

        super().__init__(args, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, encoding=encoding, errors=errors, text=text, **kwargs)  # type: ignore

    def wait(self) -> CompletedProcess:  # type: ignore
        """Wait for the process to complete. Returns CompletedProcess rather than a returncode, and prints the stdout to the console in realtime"""
        if self.stdout is None:
            return CompletedProcess(self.args, returncode=super().wait(), stdout=None)
        else:
            stdout = []
            while self.poll() is None:
                line = self.stdout.readline()
                print(line, end="")
                stdout.append(line)

            return CompletedProcess(self.args, returncode=self.poll(), stdout="".join(stdout))
