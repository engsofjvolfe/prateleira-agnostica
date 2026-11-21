"""
Diz se uma pasta fica num repositório git: se ela, ou uma pasta acima dela, no lugar real do disco, tem um ".git".

Dá às peças: no_repositorio.
"""
import os
from pathlib import Path

PASTA_DO_GIT = ".git"  # onde o git guarda o histórico: uma pasta, ou um arquivo que aponta para ela


def no_repositorio(pasta):
    """Se a pasta, ou uma pasta acima dela, tem um ".git", com os atalhos do caminho seguidos."""
    real = Path(os.path.realpath(pasta))
    return any((acima / PASTA_DO_GIT).exists() for acima in (real, *real.parents))
