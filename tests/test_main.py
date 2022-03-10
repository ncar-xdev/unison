import pathlib

import pytest

import unison


@pytest.fixture(scope='module')
def runner():
    return unison.Unison()


def test_get_conda_kernel_path(runner):
    assert runner.get_conda_kernel_path('py36') is None
    assert isinstance(runner.get_conda_kernel_path('unison-dev'), pathlib.Path)
