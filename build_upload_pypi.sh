# Check if the virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    source ~/.312venv/bin/activate
fi

rm -rf dist/*

python3 -m build
twine upload -u __token__ -p $PYPI dist/*