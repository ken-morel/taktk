"""
Here simply manages the database
"""

from taktk.settings import SettingsFile
from pathlib import Path
from pyoload import annotate, Checks, Cast
from dataclasses import dataclass
from uuid import UUID, uuid1

DIR = Path(__file__).parent

data = SettingsFile(
    DIR / "data.json",
    {
        "users": [],
        "todos": [],
    },
)


class Model:
    @classmethod
    def __init_subclass__(cls):
        cls.DoesNotExist = type("DoesNotExist", (cls.DoesNotExist,), {})
        cls.DoesExist = type("DoesExist", (cls.DoesExist,), {})

    @classmethod
    def all(cls):
        return list(map(cls.from_dict, data[cls.field()]))

    @classmethod
    def create(cls, params):
        for raw in data[cls.field()]:
            raw = raw.copy()
            raw.pop('uuid')
            if raw == params:
                raise cls.DoesExist()
        else:
            params['uuid'] = str(uuid1())
            data[cls.field()].append(params)
            return cls.from_dict(params)

    @classmethod
    def _from_uuid(cls, uuid):
        for raw in data[cls.field()]:
            if raw["uuid"] == uuid:
                return raw
        else:
            raise cls.DoesNotExist()

    @classmethod
    def from_uuid(cls, uuid):
        return cls.from_dict(cls._from_uuid(uuid))

    @classmethod
    def field(cls):
        return cls.__name__.lower() + "s"

    @classmethod
    def from_dict(cls, params):
        return cls(**params)

    def save(self):
        params = {k: v for k, v in vars(self).items() if k in self.__annotations__}
        params['uuid'] = str(params['uuid'])
        uuid = str(self.uuid)
        try:
            raw = self._from_uuid(uuid)
        except self.DoesNotExist:
            self.create(params)
        else:
            raw.update(params)
        finally:
            data.save()
        return self

    class Exception(ValueError):
        pass

    class DoesNotExist(Exception):
        pass

    class DoesExist(Exception):
        pass


@dataclass
@annotate
class User(Model):
    uuid: Cast(UUID)
    name: str
    password: str  # Checks(le=slice(8))
    __current_user__ = None

    @classmethod
    def current(cls):
        return cls.__current_user__

    @classmethod
    @annotate
    def login(cls, name: str, password: str):
        for raw in data[cls.field()]:
            if raw['name'] == name and raw['password'] == password:
                cls.__current_user__ = cls.from_dict(raw)
                return cls.current()
        else:
            raise cls.DoesNotExist()

    def create_todo(self, desc: str, done: bool = False):
        return Todo.create({
            'author_id': self.uuid,
            'desc': desc,
            'done': done,
        })

    @classmethod
    def is_login(cls):
        return cls.__current_user__ is not None


@dataclass
@annotate
class Todo(Model):
    uuid: Cast(UUID)
    author_id: Cast(UUID)
    desc: str
    done: bool = False

    @classmethod
    def for_user(cls, user: User):
        return list(
            filter(
                lambda t, u=user: t.has_user(u),
                map(Todo.from_dict, data["users"]),
            )
        )

    def has_user(self, user: User):
        return self.user
