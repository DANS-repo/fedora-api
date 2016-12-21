from setuptools import setup

setup(
    name='fedora-rest',
    version='0.1',
    packages=['fedora', 'fedora.rest'],
    url='https://github.com/dans-er/fedora-rest',
    license='Apache License Version 2.0',
    author='hvdb',
    author_email='',
    description='scripting fedora commons',
    install_requires=['requests', 'python-dateutil']
)
