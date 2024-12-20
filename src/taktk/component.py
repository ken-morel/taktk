import efus.component
import efus.namespace
import typing

from efus.types import ENil as Nil
from efus.types import ENilType as NilT

from pyoload import annotate


class TkComponent(efus.component.Component):
    namespace: efus.namespace.Namespace
    widget_config = ()
    has_parent = True

    def __init_subclass__(cls):
        if hasattr(cls, "ParamsClass"):
            cls.params = efus.component.CompParams.from_class(
                cls.ParamsClass, cls.__name__
            )

    def prerender(self):
        if self.parent is not None and self.has_parent:
            self.outlet = self.inlet = self.widget = self.WidgetClass(
                self.parent.outlet, **self.filter_widget_config()
            )
        else:
            self.outlet = self.inlet = self.widget = self.WidgetClass(
                **self.filter_widget_config()
            )
        if self.parent is not None:
            self.parent.child_geometry(self, self.inlet, self.args["pos"])
        return self.widget

    def filter_widget_config(self):
        try:
            return {
                k: v
                for k, v in self.args.items()
                if k in self.widget_config and v is not efus.types.ENil
            } | {
                a: self.args[k]
                for k, a in self.widget_config_aliasses.items()
                if self.args[k] is not efus.types.ENil
            }
        except KeyError as e:
            raise KeyError(
                f"Key {e!s} not found. Please check {type(self).__name__}'s"
                + " configs and aliasses and make sure they are in the "
                + "ClassParams."
            ) from e

    @classmethod
    @annotate
    def create(
        cls,
        np: efus.namespace.Namespace,
        attrs: dict[str, efus.types.EObject],
        pc: typing.Optional[efus.component.Component],
    ) -> efus.component.Component:
        print("received", attrs, "in", id(attrs))
        return cls(np, cls.params.bind(attrs, np), pc)

    def child_geometry(self, child, widget, args):
        if args.get("pack"):
            args = args.copy()
            args.pop("pack")
            widget.pack(**{k: v for k, v in args.items() if v is not Nil})
            print("did> ", end="")
        print("gridded", child, widget, args)

    def update(self):
        self.widget.configure(**self.filter_widget_config())


class PosSpec:
    pack: bool = False
    side: str | NilT
    fill: str | NilT
