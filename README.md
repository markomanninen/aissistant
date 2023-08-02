# aissistant

Initialization prompt for vector conversation database and personal profile in ChatGPT using Noteable plugin and aissistant module written by Marko T. Manninen ([aissistant](https://github.com/markomanninen/aissistant/)), 08/2023.

Do these step by step, one by one. Confirm each.

## 1. Noteable Project and Notebook

Use the given project and notebook URL in Noteable, or create a new project and notebook. In Noteable, a project is a container for notebooks and associated data files, while a notebook is a document containing code, markdown, and results. You can create, edit, and run code within notebooks as well as in ChatGPT.

Then proceed to the next step 2 in one run.

### 2.1 Install Required Libraries

Run the following commands:

\`\`\`
!pip install -q faiss-cpu
!pip install -q sentence-transformers
\`\`\`

### 2.2 Download Necessary Files

Download the aissistant.py file using the provided link:

\`\`\`
!wget https://raw.githubusercontent.com/markomanninen/aissistant/main/aissistant.py
\`\`\`

## 3. Upload or Create Database and Vector Index Files

Upload conversations.db and faiss_index.idx files to the same directory, or create and use empty files for the session. In Noteable, you can upload files directly to the project directory. Note: Empty files are created automatically when the aissistant module is imported in the next step and if there are no data files available.

## 4. Import and Set Up Module

\`\`\`
from aissistant import search, index, get_profile, set_profile
\`\`\`

## 5. Vector Conversation Database & Personal Profile Functions

Instruct, how the following functions are used 1) in the chat by giving trigger examples, and 2) at Noteable cell in a programmable way.

- **Search:** Use `search(query, n=1, start_date=None, end_date=None, all_fields=False)` to find similar conversations. Returns a generator.
- **Index:** Use `index(prompt_input_text, response_text)` to add conversations to the index.
- **Get Profile:** Use `get_profile(field_name=None)` to retrieve profile information.
- **Set Profile:** Use `set_profile(field_name, value)` to update your profile.

## 6. Additional Instructions

For more detailed instructions and use cases, read the aissistant.py file header and deduce the rest of the functionality. Get creative and productive with this initialization script in ChatGPT with the Noteable plugin! Use it to explore past conversations, and manage permanent profile information for a more intelligent chat and coding experience.
