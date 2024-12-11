import os

from setuptools import find_packages
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='jwt_auth',
        version=os.getenv('PACKAGE_VERSION', '1.0.0'),
        package_dir={'': 'src'},
        packages=find_packages('src', include=['jwt_auth*']),
        description='A package with jwt authentication',
        install_requires=[
            'fastapi',
            'sqlalchemy',
            'pytz',
            'pyjwt',
            'pydantic-settings',
            'backoff',
        ],
    )
