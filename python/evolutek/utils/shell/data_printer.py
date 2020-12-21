import json

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer


def print_json(obj):
    data = json.dumps(obj, sort_keys=True, indent=4)
    out = highlight(data, JsonLexer(), Terminal256Formatter())
    print(out)
