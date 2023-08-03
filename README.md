# aissistant v0.0.1

Initialization prompt for persistent conversation vector database and personal profile in ChatGPT using Noteable plugin and aissistant module written by Marko T. Manninen ([https://github.com/markomanninen/aissistant/](https://github.com/markomanninen/aissistant/)) (c) 08/2023.

Get creative and productive with this initialization script in ChatGPT that utilizes the Noteable plugin. Natively, you can create, edit, and run code and generate data within notebooks as well as in ChatGPT interchangeably, back and forth. By using this initialization prompt, you can use the combined environment to store data and explore past conversations, as well as manage profile information for a more intelligent chat and coding experience.

To start the chat and initiate the notebook, follow these steps one by one. Confirm each step from the user.

## 1. Noteable Project and Notebook Name

Use the given project or notebook URL from Noteable, or create a new project and notebook. Give instructions to the user on how all these work in Noteable, where and how to get the project url/id, etc.

### 2.1 Install Required Libraries

Run the following commands in the notebook cell on behalf of the user:

```
!pip install -q faiss-cpu
!pip install -q sentence-transformers
```

### 2.2 Download Necessary Module

If `aissistant.py` file does not exist in a current notebook project, download it on behalf of the user. Else, ask if the user wants to replace the file. In that case, append the `-O aissistant.py` option to the following download command, and run it in the notebook cell:

```
!wget https://raw.githubusercontent.com/markomanninen/aissistant/main/aissistant.py
```

## 3. Upload or Create Database and Vector Index Files

Ask the user to upload `conversation.db` and `faiss_index.idx` files to the project directory or let the system create empty files automatically. In Noteable, it is possible to manually upload files to the project directory or retrieve files via some cloud service. Help the user in this procedure.

Note: Empty `.db` and `.idx` files are created automatically when aissistant module is imported and used in the next steps and if data files are unavailable.

## 4. Import Module Functions

Run the following line in the notebook cell on behalf of the user:

```
from aissistant import search, index, get_profile, set_profile
```

## 5. Conversation Vector Database & Personal Profile Functions

Explain to the user how the following four functions can be used in two different ways:

a) in the chat, by giving natural language triggers
b) at Noteable cell in a programmable way

Conversation Functions:

I. Search Conversations: Use `search(query, n=1, start_date=None, end_date=None, all_fields=False)` to find similar conversations from the FAISS index and SQLite database. Returns a generator of numerically indexed tuples, with a handle to the rows, that contain 0=prompt and 1=response text, 2=timestamp, and optional 4=vector blob and 5=id fields.
II. Index Conversation: Use `index(prompt_input_text, response_text)` to add conversations to the FAISS index and SQLite database.

Profile functions:

III. Get Profile: Use `get_profile(field_name=None)` to retrieve profile information from the database.
IV. Set Profile: Use `set_profile(field_name, value)` to update your profile to the database.

## 6. Additional Instructions

* Tell how to download and use SQLite database (and FAISS index) on the other chat sessions and Noteable projects.
* Read and output the `aissistant.py` file content in the project on behalf of the user.
* Deduce the rest of the functionality from the file header for the user.
* Give usage examples, use cases, and data processing tips to the user, and encourage the user to explore and invent new ways of using permanent storage in ChatGPT and Noteable environment.
