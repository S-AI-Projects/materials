"""Age classification and string concatenation demonstration.

Refactoring Responsibility Simplified:
Decouples the core age category classification calculation from string
formatting and standard output printing.

Preconditions established in source:
- Line 1: def age_group(age):
- Line 2: if 0 <= age <= 9: result = "a Child!"
- Line 4: elif 9 < age <= 18: result = "an Adolescent!"
- Line 6: elif 19 < age <= 65: result = "an Adult!"
- Line 8: else: result = "in your Golden Years!"
- Line 10: print("You are " + result)
"""


def get_age_category(age: int) -> str:
    """Classify an age into its corresponding demographic category string.

    Single Responsibility: Pure calculation/classification based on age boundaries.
    """
    if 0 <= age <= 9:
        return "a Child!"
    elif 9 < age <= 18:
        return "an Adolescent!"
    elif 19 < age <= 65:
        return "an Adult!"
    else:
        return "in your Golden Years!"


def format_age_group(age: int) -> str:
    """Format the full display string for an age group using string concatenation."""
    return "You are " + get_age_category(age)


def age_group(age: int):
    """Print the formatted age group message to standard output.

    Preserves existing public signature, behavior, and stdout output.
    """
    message = format_age_group(age)
    print(message)
    return message
