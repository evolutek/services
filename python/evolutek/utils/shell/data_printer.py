import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter

def print_json(obj):
    data = json.dumps(obj, sort_keys=True, indent=4)
    out = highlight(data, JsonLexer(), Terminal256Formatter())
    print(out)
