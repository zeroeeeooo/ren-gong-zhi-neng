import py_compile, pathlib, sys
errors = False
for p in pathlib.Path('.').rglob('*.py'):
    try:
        py_compile.compile(str(p), doraise=True)
    except py_compile.PyCompileError as e:
        print('Compile error in', p)
        print(e)
        errors = True
if errors:
    sys.exit(1)
print('All files compiled successfully')
