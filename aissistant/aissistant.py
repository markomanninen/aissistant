"""
Module Requirements
===================

These external libraries are required in Noteable (-q is for quiet):

pip install -q faiss
pip install -q sentence-transformers

Basic import line:

from aissistant import search, index, get_profile, set_profile

Reconnect the module if the kernel has restarted in Noteable or you get a
database write error:

from importlib import reload
import aissistant; reload(aissistant)
from aissistant import search, index, get_profile, set_profile

Module API Endpoints
====================

Search
------

Used to get n similar results from the vector base combined with the original
prompt and response texts and the associated timestamp from the SQLite data
storage. Returns a generator of tuples with the numerical indices 0=input prompt,
1=response text, 2=timestamp, and optionally, if all_fields=True, additional
fields are 3=vector blob, and 4=row id.

search(query, n=1, start_date=None, end_date=None, all_fields=False)

Basic Search for a Single Result:

Search for a single similar result for a given query.

result = search('Tell me a joke!', n=1)
print(result)

Search with Date Filters:

Search for results within a specific date range.

results = search('What is the weather forecast?', n=3, start_date='2023-07-01', end_date='2023-07-31')
for result in results:
    print(result)

Search with All Fields:

Retrieve all fields, including vector blob and row ID, for the top 5 matches.

results = search('Recommend a restaurant.', n=5, all_fields=True)
for result in results:
    print(result)

Search with Custom Parameters:

Combine different parameters to customize the search. In this example, we're
looking for two results within a date range and including all fields.

results = search('Tell me about space exploration.', n=2, start_date='2023-01-01', end_date='2023-06-30', all_fields=True)
for result in results:
    print(result)

Index
-----

A shorthand function used to add prompt and ChatGPT responses to the FAISS index
and SQLite database table.

index(prompt_input_text, response_text)

Administration Functions
========================

Used to prune SQLite table and FAISS indices and add new text data.

prune_db_and_index()
init_vector_table_and_index()

Retrieve SQLite Database Cursor

Retrieve SQLite database cursor handle for querying data. You can use execute
and fetch functions with the returned cursor. For example, retrieve the latest
entries or count the rows in the database.

Example:

Suppose you want to retrieve the latest 5 conversations from the database. You
can use the retrieve_cursor function to get the database cursor and then run a
custom SQL query to fetch the required data.

from aissistant import retrieve_cursor

cursor = retrieve_cursor()

cursor.execute('SELECT input, output, timestamp FROM conversation_indexed ORDER BY timestamp DESC LIMIT 5')

latest_conversations = cursor.fetchall()
for conversation in latest_conversations:
    print(conversation)

In this example, we're using the cursor obtained from retrieve_cursor to execute
a custom SQL query. This query selects the input, output, and timestamp fields
from the conversations_table (replace with the actual table name), orders the
results by timestamp in descending order, and limits the results to 5.

Personal Profile Functions
==========================

Add or Update Profile Fields
----------------------------

Add or update one or more fields in the personal profile. You can provide
individual or multiple fields simultaneously using keyword arguments. Returns
True if successful and False if there's an error.

set_profile(**kwargs) -> bool

Example:

set_profile(name="John", age="30", interests="Reading;Hiking;Cooking")

Remove Profile Field/All Fields
-------------------------------

Remove a specific field or all fields from the personal profile.

delete_field_from_profile(field_name=None)
delete_all_fields_from_profile()

Retrieve Profile
----------------

Retrieve the personal profile information in one of three ways: the entire
profile, a specific field, or multiple fields.

get_profile(*field_names) -> Union[str, List[Tuple[str, str]]]

Examples:

Retrieve the entire profile:

entire_profile = get_profile()

Retrieve a specific field:

age = get_profile("age")

Retrieve multiple fields:

name_and_age = get_profile("name", "age")

Examples of plugin behaviour
============================

1. Updating Profile

Trigger: Phrases like "update my personal profile."
Action: Specify the field and the new content, and the system will update the
profile accordingly.
Function: set_profile(field_name, value)

2. Querying Profile

Trigger: Questions about your profile, such as "What are my plans?" or "Tell me
about my interests."
Action: The system retrieves the relevant information from the profile based on
the query.
Function: get_profile(field_name=None)

3. Utilizing Profile in Conversations

Action: The system uses the profile information to tailor responses and
suggestions based on your preferences, interests, and other profile fields.
Example: If you ask for restaurant recommendations, the system can consider your
dietary preferences from the profile.

4. Integration with Noteable

Storage: The profile is stored and managed within Noteable using an SQLite table,
allowing for persistence across sessions.
Functionality: The Noteable plugin can be called to update fields or fetch the
entire profile as needed.

Additional Considerations

Dynamic Fields: The profile structure allows for dynamic fields, each containing
a value that can be a semicolon-separated list of phrases and keywords.
Flexibility: The system can be further customized to recognize specific commands
or queries related to the profile, enhancing personalized interaction.

This functionality creates a more personalized and engaging experience, allowing
the system to "remember" who you are and adapt to your unique needs and preferences.
It also lays the foundation for more advanced features, such as predictive
suggestions or integration with other tools and services.

"""

from typing import List, Tuple, Generator, Union
from datetime import datetime
import sqlite3
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Conversations database name
CONVERSATIONS_DB: str = 'conversation.db'

# Conversations table name
CONVERSATIONS_TABLE: str = 'conversation_indexed'

# Personal profile table name
PERSONAL_PROFILE_TABLE: str = 'personal_profile'

###############################################
# VECTOR BASED PROMT+RESPONSE STORAGE FUNCTIONS
###############################################

# Functions for adding and searching conversations with permanent FAISS index storage
FAISS_INDEX_FILE: str = 'faiss_index.idx'

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the FAISS index from a file if it exists
if os.path.exists(FAISS_INDEX_FILE):
    faiss_index = faiss.read_index(FAISS_INDEX_FILE)
else:
    # Create the FAISS index
    dimension = model.get_sentence_embedding_dimension()
    faiss_index = faiss.IndexFlatL2(dimension)

# SQL Query cursor, and connection handles
c, conn = None, None

def retrieve_cursor() -> sqlite3.Cursor:
    """
    Retrieve the SQLite database cursor handle for querying data.

    This function returns the cursor handle, allowing you to perform various database operations,
    such as executing queries and fetching results.

    Returns:
        sqlite3.Cursor: The cursor handle to the SQLite database.

    Example:
        cursor = retrieve_cursor()
        cursor.execute('SELECT * FROM my_table')
        rows = cursor.fetchall()

    Note:
        This function relies on the ensure_connection function to make sure the connection and cursor are valid.
    """
    return ensure_connection()

def ensure_connection() -> sqlite3.Cursor:
    """
    Ensure that the database connection and query cursors are open and valid.

    This function checks whether the existing connection and cursor are valid.
    If not, it establishes a new connection and cursor to the specified SQLite database.

    Returns:
        sqlite3.Cursor: The cursor handle to the SQLite database.

    Note:
        The global variables conn (connection) and c (cursor) should be defined and properly initialized
        within the module scope. The path to the SQLite database file is defined by the constant CONVERSATIONS_DB.
    """
    global conn, c
    if not c or not conn:
        conn = sqlite3.connect(CONVERSATIONS_DB, check_same_thread=False)
        c = conn.cursor()
    try:
        c.execute("SELECT 1")
    except:
        conn = sqlite3.connect(CONVERSATIONS_DB, check_same_thread=False)
        c = conn.cursor()
    return c

# Connect to the database
ensure_connection()

# Create the table if it doesn't exist
c.execute(f'''
CREATE TABLE IF NOT EXISTS {CONVERSATIONS_TABLE}
(id INTEGER PRIMARY KEY, input TEXT, output TEXT, vector BLOB, timestamp TEXT)
''')
conn.commit()

# Create a table for the personal profile if it doesn't exist
c.execute(f'''
CREATE TABLE IF NOT EXISTS {PERSONAL_PROFILE_TABLE}
(field_name TEXT PRIMARY KEY, value TEXT)
''')
conn.commit()

def index(input_text: str, output_text: str) -> bool:
    """
    Index a conversation by adding it to the database and FAISS index.

    Parameters:
        input_text (str): The input text of the conversation.
        output_text (str): The output text (response) of the conversation.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    return add_conversation_to_db_and_index_with_timestamp(input_text, output_text)

def add_conversation_to_db_and_index_with_timestamp(input_text: str, output_text: str) -> bool:
    """
    Add a conversation to the database and FAISS index, along with a timestamp.

    Parameters:
        input_text (str): The input text of the conversation.
        output_text (str): The output text (response) of the conversation.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    try:
        # Convert the conversation to a vector
        conversation_vector = model.encode([input_text + ' ' + output_text])[0]

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Ensure that the connection is established
        ensure_connection()

        # Add the conversation to the database
        query = f'INSERT INTO {CONVERSATIONS_TABLE} (input, output, vector, timestamp) VALUES (?, ?, ?, ?)'
        c.execute(query, (input_text, output_text, conversation_vector.tobytes(), timestamp))
        conn.commit()

        # Add the conversation to the FAISS index
        faiss_index.add(np.array([conversation_vector]))

        # Save the FAISS index to a file
        faiss.write_index(faiss_index, FAISS_INDEX_FILE)
        return True
    except Exception as e:
        print(f"An error occurred while indexing the conversation: {e}")
        return False

def search(query: str, n: int = 1, start_date: str = None, end_date: str = None, all_fields: bool = False) -> Generator[Union[Tuple[str, str, str], Tuple[str, str, str, bytes, int]], None, None]:
    """
    Search for conversations based on a query and return n similar results from the vector base,
    combined with the original prompt, response texts, and associated timestamp from the SQLite data storage.

    The function performs a similarity search using a given query and returns a generator of tuples containing
    the matched conversations. By default, each tuple contains the input prompt, response text, and timestamp.
    Optionally, if all_fields=True, additional fields such as the vector blob and row ID are also included.

    Parameters:
        query (str): The text query to search for similar conversations.
        n (int, optional): The number of similar results to return. Default is 1.
        start_date (str, optional): The start date for filtering results in the format 'YYYY-MM-DD HH:MM:SS'. Default is None.
        end_date (str, optional): The end date for filtering results in the format 'YYYY-MM-DD HH:MM:SS'. Default is None.
        all_fields (bool, optional): If True, includes additional fields (vector blob, row ID) in the results. Default is False.

    Returns:
        Generator[Union[Tuple[str, str, str], Tuple[str, str, str, bytes, int]], None, None]:
            A generator of tuples, where each tuple contains:
                0: input prompt (str)
                1: response text (str)
                2: timestamp (str)
                4: vector blob (bytes), included if all_fields=True
                5: row ID (int), included if all_fields=True

    Example:
        results = search('What is the weather like?', n=3)
        for result in results:
            print(result)
    """
    return search_conversation_with_date_filter_and_n_results(query, n=n, start_date=start_date, end_date=end_date, all_fields=all_fields)

def search_conversation_with_date_filter_and_n_results(query: str, n: int = 1, start_date: str = None, end_date: str = None, all_fields: bool = False) -> Generator[Union[Tuple[str, str, str], Tuple[str, str, str, bytes, int]], None, None]:
    try:
        # Convert the query to a vector
        query_vector = model.encode([query])

        # Perform a search in the FAISS index for the top n matches
        D, I = faiss_index.search(np.array(query_vector).astype('float32'), k=n)

        sql_select = 'input, output, timestamp'
        if all_fields:
            sql_select = 'input, output, timestamp, vector, id'

        # Ensure that the connection is established
        ensure_connection()

        # Retrieve the corresponding conversations from the database
        for idx in I[0]:
            index_id = int(idx)
            sql_query = f'SELECT {sql_select} FROM {CONVERSATIONS_TABLE} WHERE id = ?'
            params = [index_id + 1]
            if start_date:
                sql_query += ' AND timestamp >= ?'
                params.append(start_date)
            if end_date:
                sql_query += ' AND timestamp <= ?'
                params.append(end_date)
            c.execute(sql_query, params)
            rows = c.fetchall()
            for row in rows:
                yield row
    except Exception as e:
        print(f"An error occurred while searching for conversations: {e}")
        yield from ()  # Return an empty generator in case of an error

def init_vector_table_and_index() -> bool:
    """
    Initialize the vector table and FAISS index with sample conversations.

    This function adds a set of sample conversations to the specified table in the database
    and updates the FAISS index accordingly. The FAISS index is then saved to a file.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    # Sample invented conversations with timestamps
    sample_conversations = [
        ('How is the weather today?', 'It is sunny and warm.', '2023-07-01 10:00:00'),
        ('What is your favorite book?', 'I enjoy reading science fiction novels.', '2023-07-01 15:30:00'),
        ('Can you recommend a good restaurant?', 'Sure! How about trying the Italian place downtown?', '2023-07-10 12:45:00'),
        ('Tell me a joke.', 'Why did the chicken cross the road? To get to the other side!', '2023-07-15 18:00:00'),
        ('What is the capital of France?', 'The capital of France is Paris.', '2023-07-16 09:15:00'),
        ('How do you make a cake?', 'You can make a cake by mixing flour, sugar, eggs, and other ingredients, then baking them in an oven.', '2023-07-17 14:30:00'),
        ('What is the meaning of life?', 'The meaning of life is a philosophical question, and answers may vary depending on personal beliefs.', '2023-07-18 16:45:00'),
        ('Can you tell me a story?', 'Once upon a time, in a land far away, there lived a brave knight who embarked on a quest to save a kingdom.', '2023-07-19 20:00:00'),
        ('What time is it?', 'I\'m sorry, I can\'t tell the current time as I don\'t have access to real-time data.', '2023-07-20 11:15:00'),
        ('How do you calculate the area of a circle?', 'The area of a circle can be calculated using the formula A = πr², where r is the radius of the circle.', '2023-07-21 12:30:00')
    ]

    try:
        # Ensure that the connection is established
        ensure_connection()

        # Add the sample conversations to the database and FAISS index
        for input_text, output_text, timestamp in sample_conversations:
            conversation_vector = model.encode([input_text + ' ' + output_text])[0]
            query = f'INSERT INTO {CONVERSATIONS_TABLE} (input, output, vector, timestamp) VALUES (?, ?, ?, ?)'
            c.execute(query, (input_text, output_text, conversation_vector.tobytes(), timestamp))
            faiss_index.add(np.array([conversation_vector]))
            conn.commit()

        # Save the FAISS index to a file
        faiss.write_index(faiss_index, FAISS_INDEX_FILE)
        return True
    except Exception as e:
        print(f"An error occurred while initializing the vector table and index: {e}")
        return False

def prune_db_and_index() -> bool:
    """
    Prune the database and FAISS index.

    This function deletes all rows from the specified conversations table in the database
    and resets the FAISS index. The empty FAISS index is then saved to a file.

    Returns:
        bool: True if the operation is successful, False if any error occurs.

    Note:
        Ensure that the database connection and cursor (`conn` and `c`), FAISS index,
        and related constants are properly initialized before calling this function.
    """
    try:
        # Ensure that the connection is established
        ensure_connection()

        # Use a safe way to format the table name in the query
        query = f'DELETE FROM {CONVERSATIONS_TABLE}'
        c.execute(query)
        conn.commit()

        # Reset the FAISS index
        faiss_index.reset()

        # Save the empty FAISS index to a file
        faiss.write_index(faiss_index, FAISS_INDEX_FILE)
        return True
    except Exception as e:
        print(f"An error occurred while pruning the database and index: {e}")
        return False

#########################################
# PROFILE FUNCTIONS
#########################################

def set_profile(**kwargs) -> bool:
    """
    Add or update fields in the personal profile.

    This function allows you to set multiple profile fields in one call. Each keyword argument
    represents a field name and its corresponding value. The function will insert or update
    these fields in the "personal_profile" table in the database.

    Parameters:
        **kwargs: Any number of keyword arguments, where the key is the field name (str),
                  and the value is the value to be set for that field (str).

    Returns:
        bool: True if the operation is successful, False if any error occurs.

    Example:
        set_profile(name="Alice", age="30", city="New York")
    """
    try:
        for field_name, value in kwargs.items():
            if not add_or_update_field_in_profile(field_name, value):
                return False
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def add_or_update_field_in_profile(field_name: str, value: str) -> bool:
    """
    Add or update a field in the personal profile.

    This function takes a field name and its corresponding value and inserts or updates
    the field in the "personal_profile" table in the database. If the field name already
    exists in the table, its value will be updated; otherwise, a new record will be inserted.

    Parameters:
        field_name (str): The name of the field to be added or updated.
        value (str): The value to be set for the specified field.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    try:
        ensure_connection()
        c.execute(f'INSERT OR REPLACE INTO {PERSONAL_PROFILE_TABLE} (field_name, value) VALUES (?, ?)', (field_name, value))
        conn.commit()
        return True
    except Exception as e:
        print(f"An error occurred while updating the field {field_name}: {e}")
        return False

def delete_all_fields_from_profile() -> bool:
    """
    Remove all fields and values from the personal profile.

    This function deletes all records from the "personal_profile" table in the database.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    try:
        ensure_connection()
        c.execute(f'DELETE FROM {PERSONAL_PROFILE_TABLE}')
        conn.commit()
        return True
    except Exception as e:
        print(f"An error occurred while deleting all fields: {e}")
        return False

def delete_field_from_profile(field_name: str) -> bool:
    """
    Remove a specific field from the personal profile.

    This function deletes a specific field and its value from the "personal_profile" table
    in the database, based on the provided field name.

    Parameters:
        field_name (str): The name of the field to be removed.

    Returns:
        bool: True if the operation is successful, False if any error occurs.
    """
    try:
        ensure_connection()
        c.execute(f'DELETE FROM {PERSONAL_PROFILE_TABLE} WHERE field_name = ?', (field_name,))
        conn.commit()
        return True
    except Exception as e:
        print(f"An error occurred while deleting the field {field_name}: {e}")
        return False

def get_profile(*field_names: str) -> Union[str, List[Tuple[str, str]]]:
    """
    Retrieve the entire profile or specific fields.

    This function can be called in three ways:
        1) Without arguments to retrieve all fields.
        2) With one field name to retrieve a specific field.
        3) With two or more field names to retrieve specific fields.

    Parameters:
        *field_names (str): The names of the fields to be retrieved (optional).

    Returns:
        Union[str, List[Tuple[str, str]]]:
            - A single value if one field name is provided.
            - A list of tuples (field_name, value) if multiple or no field names are provided.
    """
    try:
        ensure_connection()
        if len(field_names) == 1:
            c.execute(f'SELECT value FROM {PERSONAL_PROFILE_TABLE} WHERE field_name = ?', (field_names[0],))
            return c.fetchone()[0]
        else:
            query = f'SELECT * FROM {PERSONAL_PROFILE_TABLE}'
            if field_names:
                placeholders = ', '.join('?' for _ in field_names)
                query += f' WHERE field_name IN ({placeholders})'
            c.execute(query, field_names)
            return c.fetchall()
    except Exception as e:
        print(f"An error occurred while retrieving the profile fields: {e}")
        return [] if len(field_names) != 1 else None
