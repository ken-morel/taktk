import PIL.Image
import PIL.ImageTk
from functools import cached_property


MEDIA_DIR = None


def get_media(spec):
    assert spec.count(':') == 1, "media spec should include ':'"
    match tuple(spec.slit(':', 1)):
        case ('img', path):
            return Image(path)
        case wrong:
            raise ValueError(f'Unrecognised media {spec!r}')


class Resource:
    pass

class Image(Resource):
    @cached_property
    def image(self):
        if MEDIA_DIR is None:
            raise RuntimeError("Media directory not set")
        return PIL.Image.open(MEDIA_DIR / self.path)

    @cached_property
    def tk(self):
        return PIL.ImageTk.PhotoImage(self.image)

    def get(self):
        return self.tk

    def __init__(self, path):
        if not '.' in path:
            path += '.png'
        self.path = path
