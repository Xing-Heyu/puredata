#!/bin/bash
cd "$(dirname "$0")/.trae/skills/data-cleaner"
python generate.py "$@"
