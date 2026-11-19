"""Kiểm tra môi trường container (mục 3.5, 4.4)."""
import socket

import pytest
import tree_sitter_c as tsc
from tree_sitter import Language, Parser

import config


def test_tree_sitter_smoke():
    parser = Parser(Language(tsc.language()))
    code = b"int f(int a[],int n){int s=0;for(int i=0;i<=n;i++)s+=a[i];return s;}"

    def walk(n):
        yield n
        for c in n.children:
            yield from walk(c)

    t = parser.parse(code)
    assert not t.root_node.has_error
    ops = [n.child_by_field_name('condition').child_by_field_name('operator').text
           for n in walk(t.root_node) if n.type == 'for_statement']
    assert ops == [b'<=']


def test_no_network():
    with pytest.raises(OSError):
        socket.create_connection(('1.1.1.1', 53), 2)


def test_raw_read_only():
    with pytest.raises(OSError):
        (config.RAW / '.write_probe').touch()
