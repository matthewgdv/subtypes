from __future__ import annotations

import subprocess


class CompletedProcess(subprocess.CompletedProcess):
    def __bool__(self) -> bool:
        return self.returncode == 0


class Process(subprocess.Popen):
    def __init__(self, *args, cwd=None, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace", text=True, **kwargs) -> None:
        if cwd is not None and not shell:
            raise RuntimeError("'cwd' argument not supported without 'shell=True'")

        super().__init__(*args, stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, encoding=encoding, errors=errors, text=text, **kwargs)

    def wait(self) -> Process:
        if self.stdout is None:
            return CompletedProcess(self.args, returncode=super().wait(), stdout=None)
        else:
            stdout = []
            while self.poll() is None:
                line = self.stdout.readline()
                print(line, end="")
                stdout.append(line)

            return CompletedProcess(self.args, returncode=self.poll(), stdout="".join(stdout))
