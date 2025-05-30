
```bash
# Install required tool
python3 -m pip install --upgrade pip
python3 -m pip install build twine

# Build the package
python3 -m build

# Test project locally
pip install -e .

# Publish to PyPI
python3 -m twine upload dist/*