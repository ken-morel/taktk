"""Tkmap example."""
from tkmap import model, widget

canvas = widget.Tkmap()
canvas.pack(fill="both", expand=True)
canvas.open(
    model.MapModel.load("openstreetmap"),
    zoom=10,
    location=(48.645272, 1.841411),
)
