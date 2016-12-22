from setuptools import setup
from setuptools import find_packages

setup(
    name="ax.graphite_api_finders",
    version="0.2",
    url="https://github.com/axiros/graphite-api-finders",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ax'],
    install_requires=['setuptools']
)
