#!/bin/bash

# 清除之前的构建
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build

# 上传到 PyPI
twine upload dist/*

echo "Package published successfully!"