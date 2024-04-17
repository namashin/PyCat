from setuptools import setup, find_packages

setup(
    name='mia_cat',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'asyncio',
        'configparser',
        'psutil',
        'pystray',
        'Pillow>=10.3.0',
        'pywin32;platform_system=="Windows"',
    ],
    entry_points={
        'console_scripts': [
            'mia_cat = mia_cat:main',
        ],
    },
    console=False,
)
