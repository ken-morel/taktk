"""
Here simply manages the database
"""

from taktk.store import Store
from pathlib import Path
from pyoload import annotate, Checks, Cast
from dataclasses import dataclass
from uuid import UUID, uuid1
from hashlib import sha256

DIR = Path(__file__).parent

data = Store(
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
            raw.pop("uuid")
            if raw == params:
                raise cls.DoesExist()
        else:
            params["uuid"] = str(uuid1())
            data[cls.field()].append(params)
            return cls.from_dict(params)

    @classmethod
    def _from_uuid(cls, uuid):
        uuid = str(uuid)
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
        params = {
            k: str(v) if isinstance(v, UUID) else v
            for k, v in vars(self).items()
            if k in self.__annotations__
        }
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

    def delete(self):
        uuid = str(self.uuid)
        for idx, obj in enumerate(data[self.field()]):
            if obj["uuid"] == uuid:
                break
        else:
            raise self.DoesNotExist()
        data[self.field()].pop(idx)
        data.save()
        return None

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
        password = sha256(password.encode()).hexdigest()
        for raw in data[cls.field()]:
            if raw["name"] == name and raw["password"] == password:
                cls.__current_user__ = cls.from_dict(raw)
                return cls.current()
        else:
            raise cls.DoesNotExist()

    @classmethod
    @annotate
    def signup(cls, name: str, password: str):
        user = User.create(
            {"name": name, "password": sha256(password.encode()).hexdigest()}
        )
        user.save()
        User.__current_user__ = user

    def create_todo(self, desc: str, done: bool = False):
        return Todo.create(
            {
                "author_id": str(self.uuid),
                "desc": desc,
                "done": done,
            }
        )

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
                map(Todo.from_dict, data[cls.field()]),
            )
        )

    def has_user(self, user: User):
        return str(self.author_id) == str(user.uuid)
