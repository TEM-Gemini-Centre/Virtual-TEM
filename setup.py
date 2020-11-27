from setuptools import setup, find_packages

setup(
    name='vTEM',
    version='0.0.1',
    license='GPLv3',
    author='Emil Christiansen',
    author_email='emil.christiansen@ntnu.no',
    description="Python tools for drawing raypaths in a TEM",
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "License :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "numpy",
        "matplotlib",
        "pathlib",
        "tabulate",
    ],
    package_data={
        "": ["LICENSE", "README.md"],
        "": ["*.py"],
        "": ["*.ipynb"],
    },
)