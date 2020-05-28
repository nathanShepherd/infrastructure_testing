from os import system

cache = '__pycache__'
system(f'rm -r automation/{cache} /vendor_data/*/*/{cache}')
