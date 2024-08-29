from todoapp import Application
import sys

entry = "/todos"

if len(sys.argv) > 1:
    entry = sys.argv[1]

Application().redirect_to_singleton(entry)
