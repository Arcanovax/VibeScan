# ============================================================
# 🚀 User Data Processor — A Comprehensive Utility Module
# ============================================================
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def validate_data(data: Optional[Dict[str, Any]]) -> bool:
    """
    Validate the given data.

    Args:
        data (Optional[Dict[str, Any]]): The data to validate.

    Returns:
        bool: True if the data is valid.

    Raises:
        ValueError: If data is None or not a dictionary.
    """
    # Check if data is None
    if data is None:
        raise ValueError("Data must not be None")
    # Check if data is a dictionary
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    return True


def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the given data.

    Args:
        data (Dict[str, Any]): The data to process.

    Returns:
        Dict[str, Any]: The processed result.

    Raises:
        ValueError: If the data is invalid.
    """
    # Step 1: Validate the input data
    try:
        validate_data(data)
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Validation failed: {e}")
        raise

    # Step 2: Initialize the result dictionary
    result = {}

    # Step 3: Iterate over each item in the data
    for key, value in data.items():
        # Check if the value is a string
        if isinstance(value, str):
            # Strip whitespace from the string
            result[key] = value.strip()
        else:
            # Keep the value as is
            result[key] = value

    logger.info("✅ Data processed successfully → returning result…")
    return result


def save_result(result: Dict[str, Any], path: str) -> None:
    """
    Save the result to a file.

    Args:
        result (Dict[str, Any]): The result to save.
        path (str): The file path.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        # Open the file for writing
        with open(path, "w", encoding="utf-8") as f:
            # Write the JSON data to the file
            json.dump(result, f, indent=2)
        print("✨ Result saved successfully!")
    except IOError as e:
        logger.error(f"⚠️ Could not write file: {e}")
        raise
