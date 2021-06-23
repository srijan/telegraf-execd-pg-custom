from setuptools import setup, find_packages

setup(
    name="telegraf-execd-pg-custom",
    version="2.0",
    description="PostgreSQL Custom Input Plugin for Telegraf",
    long_description=open("README.md").read(),
    author="Srijan Choudhary",
    provides=['telegraf_execd_pg_custom'],
    license="MIT",
    include_package_data=True,
    install_requires=[
        "psycopg2",
        "pytoml",
        "pytz",
        "python-dateutil",
        "six",
    ],
    packages=find_packages(exclude=["tests.*", "tests", "docs"]),
    url="https://github.com/srijan/telegraf-execd-pg-custom",
    # For a list of classifiers see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    entry_points={
        "console_scripts": [
            "postgresql-query=telegraf_execd_pg_custom.postgresql_query:main"
        ]
    }
)
