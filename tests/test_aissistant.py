
import pytest
from aissistant import index, search, set_profile, get_profile

def test_index():
    assert index("What's the weather like?", "It's sunny and warm.") == True

def test_search():
    results = search("What's the weather like?")
    assert results[0][0] == "What's the weather like?"
    assert results[0][1] == "It's sunny and warm."

def test_set_get_profile():
    set_profile("email", "user@example.com")
    email = get_profile("email")
    assert email == "user@example.com"
