"""
These external libraries are required in Noteable:

!pip install -q faiss-cpu
!pip install -q sentence-transformers

Basic import line:

from aissistant import search, index, get_profile, set_profile

Reconnect module if kernel has restarted in Noteable:

from importlib import reload
import aissistant
reload(aissistant)
from aissistant import search, index, get_profile, set_profile

Module API endpoints
====================

Search is used to get n similar results from the vector base combined with
the original prompt and response texts and the associated timestamp from
the sqlite data storage. ->

search(query, n = 1, start_date = None, end_date = None, all_fields = False)

Index is a shorthand function used to add prompt and chatgpt response to
the FAISS index and sqlite database table ->

index(prompt_input_text, response_text)

Administration functions are used to prune sqlite table and FAISS indices, and
add new text data. ->

prune_db_and_index()
init_vector_table_and_index()


Personal profile functions
==========================

Add or update a field in the personal profile. Use semicolons in a list of items in a value string. ->

set_profile(field_name, value)

Remove a field from the personal profile. ->

delete_field_from_profile(field_name)

Retrieve the entire profile or specific fields. ->

get_profile(field_name=None)

Examples for plugin behaviour
-----------------------------

1. Updating Profile

Trigger: Phrases like "update my personal profile."
Action: Specify the field and the new content, and the system will update the profile accordingly.
Function: set_profile(field_name, value)

2. Querying Profile

Trigger: Questions about your profile, such as "What are my plans?" or "Tell me about my interests."
Action: The system retrieves the relevant information from the profile based on the query.
Function: get_profile(field_name=None)

3. Utilizing Profile in Conversations

Action: The system uses the profile information to tailor responses and suggestions based on your preferences, interests, and other profile fields.
Example: If you ask for restaurant recommendations, the system can consider your dietary preferences from the profile.

4. Integration with Noteable

Storage: The profile is stored and managed within Noteable using an SQLite table, allowing for persistence across sessions.
Functionality: The Noteable plugin can be called to update fields or fetch the entire profile as needed.

Additional Considerations

Dynamic Fields: The profile structure allows for dynamic fields, each containing a value that can be a semicolon-separated list of phrases and keywords.
Flexibility: The system can be further customized to recognize specific commands or queries related to the profile, enhancing the personalized interaction.

This functionality creates a more personalized and engaging experience, allowing the system to "remember" who you are and adapt to your unique needs and preferences. It also lays the foundation for more advanced features, such as predictive suggestions or integration with other tools and services.

"""

from datetime import datetime
import sqlite3
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Conversations database name
CONVERSATIONS_DB = 'conversation.db'

###############################################
# VECTOR BASED PROMT+RESPONSE STORAGE FUNCTIONS
###############################################

# Functions for adding and searching conversations with permanent FAISS index storage
FAISS_INDEX_FILE = 'faiss_index.idx'

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the FAISS index from a file if it exists
if os.path.exists(FAISS_INDEX_FILE):
    faiss_index = faiss.read_index(FAISS_INDEX_FILE)
else:
    # Create the FAISS index
    dimension = model.get_sentence_embedding_dimension()
    faiss_index = faiss.IndexFlatL2(dimension)

def ensure_connection():
    global conn, c
    try:
        c.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        conn = sqlite3.connect(CONVERSATIONS_DB, check_same_thread=False)
        c = conn.cursor()

# Connect to the database
conn = sqlite3.connect(CONVERSATIONS_DB, check_same_thread=False)
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS conversation_indexed
(id INTEGER PRIMARY KEY, input TEXT, output TEXT, vector BLOB, timestamp TEXT)
''')
conn.commit()

# Create a table for the personal profile
c.execute('''
CREATE TABLE IF NOT EXISTS personal_profile
(field_name TEXT PRIMARY KEY, value TEXT)
''')
conn.commit()

def index(input_text, output_text):
    add_conversation_to_db_and_index_with_timestamp(input_text, output_text)

def add_conversation_to_db_and_index_with_timestamp(input_text, output_text):
    # Convert the conversation to a vector
    conversation_vector = model.encode([input_text + ' ' + output_text])[0]

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    ensure_connection()

    # Add the conversation to the database
    c.execute('INSERT INTO conversation_indexed (input, output, vector, timestamp) VALUES (?, ?, ?, ?)',
              (input_text, output_text, conversation_vector.tobytes(), timestamp))
    conn.commit()

    # Add the conversation to the FAISS index
    faiss_index.add(np.array([conversation_vector]))

    # Save the FAISS index to a file
    faiss.write_index(faiss_index, FAISS_INDEX_FILE)

def search(query, n = 1, start_date = None, end_date = None, all_fields = False):
	return search_conversation_with_date_filter_and_n_results(query, n=1, start_date=None, end_date=None, all_fields = False)

def search_conversation_with_date_filter_and_n_results(query, n=1, start_date=None, end_date=None, all_fields = False):
    # Convert the query to a vector
    query_vector = model.encode([query])

    # Perform a search in the FAISS index for the top n matches
    D, I = faiss_index.search(np.array(query_vector).astype('float32'), k=n)

    sql_select = 'input, output, timestamp'
    if all_fields:
        sql_select = '*'

    ensure_connection()

    # Retrieve the corresponding conversations from the database
    for idx in I[0]:
        index_id = int(idx)
        sql_query = 'SELECT %s FROM conversation_indexed WHERE id = ?' % sql_select
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

def init_vector_table_and_index():
    # Sample invented conversations with timestamps
    sample_conversations = [
	('How is the weather today?', 'It is sunny and warm.', '2023-07-01 10:00:00'),
	('What is your favorite book?', 'I enjoy reading science fiction novels.', '2023-07-01 15:30:00'),
	('Can you recommend a good restaurant?', 'Sure! How about trying the Italian place downtown?', '2023-07-10 12:45:00'),
	('Tell me a joke.', 'Why did the chicken cross the road? To get to the other side!', '2023-07-15 18:00:00')
    ]

    ensure_connection()

    # Add the sample conversations to the database and FAISS index
    for input_text, output_text, timestamp in sample_conversations:
        conversation_vector = model.encode([input_text + ' ' + output_text])[0]
        c.execute('INSERT INTO conversation_indexed (input, output, vector, timestamp) VALUES (?, ?, ?, ?)', (input_text, output_text, conversation_vector.tobytes(), timestamp))
        faiss_index.add(np.array([conversation_vector]))
        conn.commit()

    # Save the FAISS index to a file
    faiss.write_index(faiss_index, FAISS_INDEX_FILE)

def prune_db_and_index():
    # Delete all rows from the database
    c.execute('DELETE FROM conversation_indexed')
    conn.commit()

    # Reset the FAISS index
    faiss_index.reset()

    # Save the empty FAISS index to a file
    faiss.write_index(faiss_index, FAISS_INDEX_FILE)

#########################################
# PROFILE FUNCTIONS
#########################################

def set_profile(field_name, value):
    add_or_update_field_in_profile(field_name, value)

def add_or_update_field_in_profile(field_name, value):
    """Add or update a field in the personal profile."""
    c.execute('INSERT OR REPLACE INTO personal_profile (field_name, value) VALUES (?, ?)', (field_name, value))
    conn.commit()

def delete_field_from_profile(field_name):
    """Remove a field from the personal profile."""
    c.execute('DELETE FROM personal_profile WHERE field_name = ?', (field_name,))
    conn.commit()

def get_profile(field_name=None):
    """Retrieve the entire profile or specific fields."""
    if field_name:
        c.execute('SELECT value FROM personal_profile WHERE field_name = ?', (field_name,))
        return c.fetchone()[0]
    else:
        c.execute('SELECT * FROM personal_profile')
        return c.fetchall()
