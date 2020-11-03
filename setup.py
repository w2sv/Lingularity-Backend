from setuptools import setup, find_packages
from pathlib import Path

from backend.utils import spacy

version = {}
exec(open(Path(__file__).parent /'backend/version.py').read(), version)


setup(
    name='backend',
    packages=find_packages(),
    version=version['__version__'],
    python_requires='>=3.8',
    install_requires=[
        'numpy==1.18.1',
        'requests==2.23.0',
        'unidecode==1.1.1',
        'nltk==3.4.5',
        'pymongo==3.9.0',
        'dnspython',
        'python-vlc==3.0.11115',
        'cryptography==3.1',
        'gTTS',
        'googletrans',
        'textacy==0.10.1',
        'spacy',
        'aenum'
    ] + spacy.model_names(),
    author='W2SV',
    author_email='zangenbergjanek@googlemail.com',
    platform='Linux'
)
