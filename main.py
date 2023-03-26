from types import UnionType
from typing import Optional, get_origin, Union

from pydantic import BaseModel, create_model


class MetaPydanticModel:
    @classmethod
    def _dict_model(cls, name: str, dict_def: dict) -> type[BaseModel]:
        fields = {}
        for field_name, value in dict_def.items():
            if isinstance(value, tuple):
                fields[field_name] = value
            elif isinstance(value, dict):
                fields[field_name] = (cls._dict_model(f'{name}_{field_name}', value), ...)
            else:
                raise ValueError(f"Field {field_name}:{value} has invalid syntax")
        return create_model(name, **fields)

    @classmethod
    def _sample_class(cls, obj, ) -> dict:
        annotations = []
        for name, annotation in obj.__annotations__.items():
            default = obj().__getattribute__(name)
            if get_origin(annotation) not in {list, tuple, str, int, bool, None, UnionType, Union, Optional} \
                    or name.startswith("_"):
                continue
            else:
                annotations.append((name, (annotation, default)))
        return dict(annotations)

    @classmethod
    def _gen_model(cls, obj: object, ) -> type[BaseModel]:
        return cls._dict_model(obj.__name__, cls._sample_class(obj))

    def __call__(self, obj):
        return self._gen_model(obj)


# ----------------------------------------------------------------------------------------------------------------------
# example

@MetaPydanticModel()
class Pydantic:
    pass


@MetaPydanticModel()
class Model:
    param1: str = ...
    param2: Pydantic = None


if __name__ == '__main__':
    print(Model(param1='hello world!').json())
