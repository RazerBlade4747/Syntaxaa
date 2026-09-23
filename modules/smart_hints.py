"""
smart_hints.py
---------------
Smart Hint Mode: instead of showing the full fix immediately,
we reveal hints one step at a time so the student keeps thinking.

VIVA NOTE: This is just a Python list of strings per error category,
revealed one at a time using an index counter kept in the GUI. No
complicated logic is needed - the "intelligence" is in the design of
the hint wording, not in the code.
"""

HINTS_BY_CATEGORY = {
    "Syntax": [
        "Look closely at the line the error mentions.",
        "Check whether every bracket and quotation mark you opened is also closed.",
        "Check if you used '=' where '==' was needed for comparison.",
        "Check for a missing colon (:) at the end of an if/for/while/def line."
    ],
    "Indentation": [
        "Look at the lines just above and below the line mentioned in the error.",
        "Check whether all lines inside the same block start with the same number of spaces.",
        "Make sure you haven't mixed tabs and spaces.",
        "Try re-typing the indentation for that block using 4 spaces consistently."
    ],
    "Name": [
        "Check the exact spelling of the variable or function name.",
        "Make sure the variable is created (assigned a value) somewhere before this line.",
        "Check that the variable isn't only created inside a different function.",
        "Print the variable just before this line to confirm it exists."
    ],
    "Type": [
        "Check what type of data each variable holds (text, number, list, etc).",
        "Look for a place where text and numbers are being combined directly.",
        "Try converting one of the values using str(), int(), or float().",
        "Test each part of the expression separately to find the mismatched type."
    ],
    "Logic": [
        "Re-read what this line is trying to do step by step.",
        "Check any values used for division, indexing, or dictionary keys.",
        "Add a print statement just before this line to see the actual values.",
        "Consider what happens when the input is 0, empty, or missing."
    ],
    "General": [
        "Read the error message slowly - it usually names the exact problem.",
        "Look at the line number mentioned in the error.",
        "Try running a smaller part of your code to isolate the problem.",
        "Check the Error Encyclopedia for this error type."
    ]
}


def get_hints_for_category(category):
    """Returns the ordered hint list for a category, defaulting to General."""
    return HINTS_BY_CATEGORY.get(category, HINTS_BY_CATEGORY["General"])


def get_hint(category, hint_index):
    """
    Returns a single hint by index (0-based) for progressive reveal.
    Returns None if there are no more hints left.
    """
    hints = get_hints_for_category(category)
    if 0 <= hint_index < len(hints):
        return hints[hint_index]
    return None
