import os
from loguru import logger


def find_env(name_env: str) -> str:
    env = os.environ.get(name_env)
    if env is not None:
        return env
    logger.warning(
        f'Warning, env with name {name_env} not found,'
        ' check you .env or envshell',
        )
