from __future__ import annotations

import os
import subprocess
from typing import Any, Union, List

PathLike = Union[str, os.PathLike]


class CompletedProcess(subprocess.CompletedProcess):
    def __bool__(self) -> bool:
        return self.returncode == 0


class Process(subprocess.Popen):
    def __init__(self, args: List[str], cwd: PathLike = None, shell: bool = False, print_call: bool = True, stdout: Any = subprocess.PIPE, stderr: Any = subprocess.STDOUT, encoding: str = "utf-8", errors: str = "replace", text: bool = True, **kwargs: Any) -> None:
        if cwd is not None and not shell:
            raise RuntimeError("'cwd' argument not supported without 'shell=True'")

        args = [str(arg) for arg in args]
        if print_call:
            print(" ".join(args))

        super().__init__(args, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, encoding=encoding, errors=errors, text=text, **kwargs)  # type: ignore

    def wait(self) -> CompletedProcess:  # type: ignore
        if self.stdout is None:
            return CompletedProcess(self.args, returncode=super().wait(), stdout=None)
        else:
            stdout = []
            while self.poll() is None:
                line = self.stdout.readline()
                print(line, end="")
                stdout.append(line)

            return CompletedProcess(self.args, returncode=self.poll(), stdout="".join(stdout))
