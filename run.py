import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), 'platform', 'backend'))
os.system(f'"{sys.executable}" simple_main.py')
