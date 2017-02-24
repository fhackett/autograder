from setuptools import setup, find_packages

setup(
    name='autograder',
    version='0.1',
    install_requires=['blessings', 'pytest-datadir', 'pystache', 'aiosmtpd'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'autograder = autograder:main',
        ]
    }
)
