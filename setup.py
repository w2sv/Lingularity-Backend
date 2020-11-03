from setuptools import setup, find_packages
from pathlib import Path

from backend.utils import spacy

version = {}
exec(open(Path(__file__).parent /'backend/version.py').read(), version)


setup(
    name='backend',
    packages=find_packages(exclude=(["*.tests", "*.tests.*", "tests.*", "tests"])),
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
        'aenum',
    ],
    dependency_links=spacy.model_package_links('2.3.1'),
    include_package_data=True,
    author='W2SV',
    author_email='zangenbergjanek@googlemail.com',
    platforms=['Linux']
)
