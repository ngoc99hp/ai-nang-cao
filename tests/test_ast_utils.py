import ast_utils as au


def test_hash_ignores_format_and_comments():
    a = 'int main(){int x=1; /* c */ return x;}'
    b = 'int main()\n{\n    int x = 1;   // khác comment\n    return x;\n}\n'
    assert au.code_hash(a) == au.code_hash(b)


def test_hash_sensitive_to_code():
    assert au.code_hash('int f(){return 1;}') != au.code_hash('int f(){return 2;}')
