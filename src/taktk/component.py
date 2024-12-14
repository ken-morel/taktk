import efus.component
import efus.namespace
import typing

from pyoload import annotate


class TkComponent(efus.component.Component):
    namespace: efus.namespace.Namespace
    widget_config = ()

    def __init_subclass__(cls):
        if hasattr(cls, "ParamsClass"):
            cls.params = efus.component.CompParams.from_class(cls.ParamsClass)

    def prerender(self):
        self.outlet = self.inlet = self.widget = self.WidgetClass(
            **self.filter_widget_config()
        )
        if self.parent is not None:
            self.parent.child_geometry(self, self.inlet, self.args["pos"])
        return self.widget

    def filter_widget_config(self):
        return {
            k: v
            for k, v in self.args.items()
            if k in self.widget_config and v is not efus.types.ENil
        } | {
            a: self.args[k]
            for k, a in self.widget_config_aliasses.items()
            if self.args[k] is not efus.types.ENil
        }

    @classmethod
    @annotate
    def create(
        cls,
        np: efus.namespace.Namespace,
        attrs: dict[str, efus.types.EObject],
        pc: typing.Optional[efus.component.Component],
    ) -> efus.component.Component:
        return cls(np, cls.params.bind(attrs, np), pc)

    def child_geometry(self, child, widget, args):
        if args.get("pack"):
            args = args.copy()
            args.pop("pack")
            widget.pack(**args)
