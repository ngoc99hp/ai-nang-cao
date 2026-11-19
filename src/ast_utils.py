"""Tiện ích AST (tree-sitter-c). Duyệt cây bằng đệ quy — không dùng Query API (xem mục 3.9)."""
import hashlib
from functools import lru_cache

import tree_sitter_c as tsc
from tree_sitter import Language, Parser


@lru_cache(maxsize=1)
def parser() -> Parser:
    return Parser(Language(tsc.language()))


def parse(code: str | bytes):
    if isinstance(code, str):
        code = code.encode('utf-8', errors='replace')
    return parser().parse(code)


def walk(node):
    yield node
    for c in node.children:
        yield from walk(c)


def tokens(code: str | bytes) -> list[str]:
    """Chuỗi token lá, bỏ comment → bất biến với định dạng/khoảng trắng/comment."""
    tree = parse(code)
    return [n.text.decode('utf-8', errors='replace') for n in walk(tree.root_node)
            if n.child_count == 0 and n.type != 'comment' and n.text]


def code_hash(code: str | bytes) -> str:
    return hashlib.sha1('\x00'.join(tokens(code)).encode()).hexdigest()
