from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='anypath',
    version='0.7.5',
    description='AnyPath makes it trivial to fetch remote resources and work with them locally.',
    long_description=readme(),
    url='https://github.com/vaubarth/anypath',
    license='Mozilla Public License 2.0 (MPL 2.0)',
    author='Vincent Barth',
    author_email='vdbarth@posteo.at',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)'
    ],
    packages=['anypath', 'anypath.pathprovider'],
    install_requires=[]
)