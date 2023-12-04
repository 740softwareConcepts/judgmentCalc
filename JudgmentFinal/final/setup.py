from setuptools import setup

setup(
    name='JudgmentCLI',
    version=1.0,
    py_modules=['judgment'],
    install_requires=[
        'Click',
        'mysql.connector',
        'datetime',
        'decimal',
    ],
    entry_points='''
        [console_scripts]
        judgment=judgment:cli
    ''',
)