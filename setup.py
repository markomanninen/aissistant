from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print("\n\nWelcome to aissistant!")
        print("For usage tips and help, you can call `help(aissistant)` or access `aissistant.__doc__`, and `dir(aissistant)` to see the functions and `help(any_function)` after importing the module.")
        print("\nEnjoy!\n")

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
    name='aissistant',
    version=0.1,
	cmdclass={'install': PostInstallCommand},
    packages=find_packages(),
    install_requires=[
        'faiss',
        'sentence-transformers',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'aissistant=aissistant.cli:main',
        ],
    },
    author='Marko Manninen',
    url='https://github.com/markomanninen/aissistant',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Aissistant v0.1",
    long_description=long_description,
    long_description_content_type='text/markdown',
)
