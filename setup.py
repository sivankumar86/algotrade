from setuptools import setup
import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name="algotrade",
    version="0.1",
    packages=setuptools.find_packages(),
    install_requires = required
)