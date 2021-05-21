import typing

from pathlib import Path
import sqlalchemy.types as types

class PathType(types.TypeDecorator):

    impl = types.String

    cache_ok = True

    def process_bind_param(self, value: typing.Union[str, Path, None], dialect):
        if isinstance(value, Path):
            return value.as_posix()
        elif isinstance(value, str):
            return Path(value).as_posix()

        return ""

    def process_result_value(self, value: str, dialect):
        if isinstance(value, str):
            return Path(value)

        return Path()

