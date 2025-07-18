from diffcheck.diff import get_dict_differences


def test_get_dict_differences_no_changes():
    """Test comparing identical dictionaries."""
    dict1 = {"file1.txt": "hash1", "file2.txt": "hash2"}
    dict2 = {"file1.txt": "hash1", "file2.txt": "hash2"}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == []
    assert diff.updated_keys == []
    assert diff.deleted_keys == []


def test_get_dict_differences_new_keys():
    """Test detecting new keys in dict2."""
    dict1 = {"file1.txt": "hash1"}
    dict2 = {"file1.txt": "hash1", "file2.txt": "hash2", "file3.txt": "hash3"}

    diff = get_dict_differences(dict1, dict2)

    assert set(diff.new_keys) == {"file2.txt", "file3.txt"}
    assert diff.updated_keys == []
    assert diff.deleted_keys == []


def test_get_dict_differences_deleted_keys():
    """Test detecting deleted keys (present in dict1 but not dict2)."""
    dict1 = {"file1.txt": "hash1", "file2.txt": "hash2", "file3.txt": "hash3"}
    dict2 = {"file1.txt": "hash1"}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == []
    assert diff.updated_keys == []
    assert set(diff.deleted_keys) == {"file2.txt", "file3.txt"}


def test_get_dict_differences_updated_keys():
    """Test detecting updated keys (same key, different value)."""
    dict1 = {"file1.txt": "hash1", "file2.txt": "hash2"}
    dict2 = {"file1.txt": "hash1_updated", "file2.txt": "hash2_updated"}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == []
    assert set(diff.updated_keys) == {"file1.txt", "file2.txt"}
    assert diff.deleted_keys == []


def test_get_dict_differences_mixed_changes():
    """Test detecting all types of changes simultaneously."""
    dict1 = {
        "file1.txt": "hash1",  # will be updated
        "file2.txt": "hash2",  # will be deleted
        "file3.txt": "hash3",  # unchanged
    }
    dict2 = {
        "file1.txt": "hash1_updated",  # updated
        "file3.txt": "hash3",  # unchanged
        "file4.txt": "hash4",  # new
    }

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == ["file4.txt"]
    assert diff.updated_keys == ["file1.txt"]
    assert diff.deleted_keys == ["file2.txt"]


def test_get_dict_differences_empty_dictionaries():
    """Test comparing empty dictionaries."""
    dict1 = {}
    dict2 = {}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == []
    assert diff.updated_keys == []
    assert diff.deleted_keys == []


def test_get_dict_differences_from_empty_to_populated():
    """Test comparing empty dict1 to populated dict2."""
    dict1 = {}
    dict2 = {"file1.txt": "hash1", "file2.txt": "hash2"}

    diff = get_dict_differences(dict1, dict2)

    assert set(diff.new_keys) == {"file1.txt", "file2.txt"}
    assert diff.updated_keys == []
    assert diff.deleted_keys == []


def test_get_dict_differences_from_populated_to_empty():
    """Test comparing populated dict1 to empty dict2."""
    dict1 = {"file1.txt": "hash1", "file2.txt": "hash2"}
    dict2 = {}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == []
    assert diff.updated_keys == []
    assert set(diff.deleted_keys) == {"file1.txt", "file2.txt"}


def test_get_dict_differences_with_numeric_types():
    """Test function works with different types (not just strings)."""
    dict1 = {1: "value1", 2: "value2"}
    dict2 = {1: "value1_updated", 3: "value3"}

    diff = get_dict_differences(dict1, dict2)

    assert diff.new_keys == [3]
    assert diff.updated_keys == [1]
    assert diff.deleted_keys == [2]

