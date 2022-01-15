from setuptools import setup, find_packages

__author__ = "Manuel Huber"
__version__ = "0.0.0"

setup(
    name='imagesort',
    version=__version__,
    description='Utility to sort images by creation date',
    author=__author__,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only"
    ],
    package_dir={
        '': 'src'
    },
    packages=find_packages(where='./src'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ims = imagesort.cli:main',
            'imagesort = imagesort.cli:main',
        ]
    },
    install_requires=[
        'Pillow >= 8.4.0',
        'click >= 7.1.2',
        'prompt-toolkit >= 3.0.24'
    ]
)
