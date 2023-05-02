"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = ['data.json']
OPTIONS = {
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'srt_zh',
        'CFBundleDisplayName': 'srt_zh',
    },
    'includes': ['deepl', 'customtkinter', 'tkinterdnd2', 'requests', 'cffi', 'pyopenssl', 'charset-normalizer',
                 'openssl'],
    'packages': ['requests'],
    'argv_emulation': False
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
