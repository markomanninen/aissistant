from setuptools import setup, find_packages
from setuptools.command.install import install

version = 0.7

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print("\n\nWelcome to aissistant!")
        print("For usage tips and help, you can call `help(aissistant)` or access `aissistant.__doc__`, and `dir(aissistant)` to see the functions and `help(any_function)` after importing the module.")
        print("\nEnjoy!\n")

#with open('README.md', 'r') as file:
#    long_description = file.read()

long_description = f"""
# Aissistant v{version}

Initialization prompt for persistent conversation vector database and personal profile in ChatGPT using Noteable plugin and `aissistant` module written by Marko T. Manninen ([https://github.com/markomanninen/aissistant/](https://github.com/markomanninen/aissistant/)) ©

Copyright © 08/2023.

Get creative and productive with this initialization script in ChatGPT that utilizes the Noteable plugin. Natively, you can create, edit, and run code and generate data within notebooks as well as in ChatGPT interchangeably, back and forth. By using this initialization prompt, you can use the combined environment to store data and explore past conversations, as well as manage profile information for a more intelligent chat and coding experience.

## Start Wizard

To start the chat and initiate the notebook, follow these steps one by one. Confirm each step from the user.

Remember actually to run the cells, not just write them.

Write headings and descriptions of each operation in markdown format to the notebook above executed cells in a human-readable way.

## 1. Noteable Project and Notebook Name

Use the given project or notebook URL from Noteable, or create a new project and notebook. Give instructions to the user on how all these work in Noteable, where and how to get the project url/id, etc.

After creating a new document, add the main heading `1. Aissistant` and description with initialization introduction and GitHub project reference to the markdown cell at the beginning of the document.

## 2. Installation

Add the heading `2. Installation` and description to the notebook document.

### 2.1 Install Required Libraries

Add a heading and description to the markdown cells.

Run the following commands in the notebook cell on behalf of the user:

```
!pip install -q faiss-cpu
!pip install -q sentence-transformers
```

### 2.2 Download Module

Add heading, description, and user decision information to the markdown cells.

If the `aissistant.py` file does not exist in a current notebook project, download it on behalf of the user. Else, ask if the user wants to replace the file. In that case, append the `-O aissistant.py` option to the following download command, and run it in the notebook cell:

```
!wget https://raw.githubusercontent.com/markomanninen/aissistant/main/aissistant.py
```

Steps 2.1 and 2.2 will take time to finish, and they are mandatory to be finished before continuing to the next step!

## 2.3 Upload or Create Database and Vector Index Files

Add heading, description, and user decision information to the markdown cells.

Ask the user to upload `conversation.db` and `faiss_index.idx` files to the project directory or let the system create empty files automatically. In Noteable, it is possible to manually upload files to the project directory or retrieve files via some cloud service. Help the user in this procedure. Typically, the user has these files downloaded from the other `aissistant` session.

Note: Empty `.db` and `.idx` files are created automatically when the `aissistant` module is imported and used in the next steps and if data files are unavailable.

## 2.4 Import Module Functions

Add a heading and description to the markdown cells.

Run the following line in the notebook cell on behalf of the user:

```
from aissistant import search, index, get_profile, set_profile
```

Then continue to the instructions.

## 3. Instructions

Conversation Vector Database, Personal Profile, and Other Functions

Explain to the user how the following four functions can be used in two different ways:

a) in the chat, by giving natural language triggers
b) at Noteable notebook cell in a programmable way

### 3.1 Conversation Functions

- Search Conversations: Use `search(query, n=1, start_date=None, end_date=None, all_fields=False)` to find similar conversations from the FAISS index and SQLite database. Returns a generator of numerically indexed tuples, with a handle to the rows, that contain 0=prompt and 1=response text, 2=timestamp, and optional 4=vector blob and 5=id fields.
- Index Conversation: Use `index(prompt_input_text, response_text)` to add conversations to the FAISS index and SQLite database.

### 3.2 Profile Functions

- Get Profile: Use `get_profile(field_name=None)` to retrieve profile information from the database. Reason the necessity of retrieving user profile information to enhance your responses. Usually, it contains personal contact, employment, education, interests, goals, preferences, research topics, ideological stances, and various other information.
- Set Profile: Use `set_profile(field_name, value)` to update profile to the database. Reason the necessity of storing and updating fields and values from the user inputs.

### 3.3 Additional Functions

- Retrieve Cursor: Use `retrieve_cursor()` to access the database directly, for example, getting the count of the rows, etc.

## 4. Further Instructions

* Tell the user how to download and use SQLite database (and FAISS index) on the other chat sessions and Noteable projects.
* Read and output the `aissistant.py` file content in the project on behalf of the user.
  - Deduce the rest of the functionality from the file header for the user.
* Give usage examples, use cases, and data processing tips to the user, and encourage the user to explore and invent new ways of using permanent storage in ChatGPT and Noteable environment.

Don't start your responses with "certainly," "surely," "great," or similar expressions. Go straight to the point in all of your future responses. Avoid intro and conclusion sections on responses and any unnecessary repetitions.

Along the way interacting with the user, ChatGPT, and Noteable notebook document, write headings and descriptions of the operations in markdown format to the notebook above each executed cell in a human-readable way.
"""

setup(
    name='aissistant',
    version=version,
    cmdclass={'install': PostInstallCommand},
    packages=find_packages(),
    install_requires=[
        'sentence-transformers',
        'numpy',
    ],
    extras_require={
        'gpu': ['faiss-gpu'],
        'cpu': ['faiss-cpu'],
    },
    entry_points={
        'console_scripts': [
            'aissistant=issistant.aissistant.cli:main',
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
    description=f"Aissistant v{version}",
    long_description=long_description,
    long_description_content_type='text/markdown',
)
