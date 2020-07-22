
from pkg_resources import resource_stream, resource_string

def get_grammar(name: str) -> str:
    return resource_string("grascii.grammars", name + ".lark").decode("utf-8")

