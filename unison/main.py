from __future__ import annotations

import dataclasses
import json
import pathlib
import subprocess

import nbconvert.preprocessors
import nbformat

from .console import console


@dataclasses.dataclass
class Unison:
    def get_conda_kernel_path(self, env_name) -> str | None:
        command = ['conda', 'env', 'list', '--json']
        try:
            output = subprocess.check_output(command).decode('ascii')
            envs = json.loads(output)['envs']

            for env in envs:
                env = pathlib.Path(env)
                if env.stem == env_name:
                    return env
        except Exception as exc:
            console.print(f'Error getting conda kernel path: {exc}')
            return None

    def set_kernel_name(
        self,
        notebook_in: str | pathlib.Path,
        kernel_name: str,
        *,
        notebook_out: str | pathlib.Path = None,
    ) -> None:
        if notebook_out is None:
            notebook_out = notebook_in

        notebook = nbformat.read(notebook_in, as_version=nbformat.NO_CONVERT)
        notebook['metadata']['kernelspec']['name'] = kernel_name
        nbformat.write(notebook, notebook_out)

    def get_kernel_name(self, notebook_in: str | pathlib.Path) -> str:
        notebook = nbformat.read(notebook_in, as_version=nbformat.NO_CONVERT)
        return notebook['metadata']['kernelspec']['name']

    def clear_outputs(
        self, notebook_in: str | pathlib.Path, notebook_out: str | pathlib.Path = None
    ) -> None:
        if notebook_out is None:
            notebook_out = notebook_in

        notebook = nbformat.read(notebook_in, as_version=nbformat.NO_CONVERT)
        if not isinstance(notebook['cells'], list):
            raise TypeError('Notebook cells must be a list')

        cells = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                cell['execution_count'] = None
                cell['outputs'] = []
            cells.append(cell)
        notebook['cells'] = cells
        nbformat.write(notebook, notebook_out)

    def execute(
        self,
        notebook_in: str | pathlib.Path,
        output_dir: str | pathlib.Path = '.',
        *,
        timeout: int = None,
    ) -> None | str:

        with open(notebook_in, encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=nbformat.NO_CONVERT)

        executor = nbconvert.preprocessors.ExecutePreprocessor(timeout=timeout)

        try:
            output = executor.preprocess(notebook, {'metadata': {'path': './'}})
        except nbconvert.preprocessors.CellExecutionError:
            output = None
            msg = f'Error executing the notebook "{notebook_in}".\n'
            msg += f'See notebook "{notebook_in}" for the traceback.\n'
            console.print(msg)

        finally:
            notebook_out = pathlib.Path(output_dir) / notebook_in.stem
            with open(notebook_out, 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)

            console.print(f'Notebook "{notebook_out}" saved.')

        return output
