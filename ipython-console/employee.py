first_name = "Han"
last_name = "Solo"
department = "Accounts"
salary = 1000


def ipython_console(
    first_name=first_name,
    last_name=last_name,
    department=department,
    salary=salary,
    **kwargs,
):
    """Format and inspect employee record in IPython console environment.

    Preconditions established by source lines 1-4:
        Line 1: first_name = "Han"
        Line 2: last_name = "Solo"
        Line 3: department = "Accounts"
        Line 4: salary = 1000

    Representative result:
        >>> ipython_console("Han", "Solo", "Accounts", 1000)
        {'first_name': 'Han', 'last_name': 'Solo', 'department': 'Accounts', 'salary': 1000, 'full_name': 'Han Solo'}

    Args:
        first_name (str): Employee first name (default "Han" from line 1).
        last_name (str): Employee last name (default "Solo" from line 2).
        department (str): Department name (default "Accounts" from line 3).
        salary (int or float): Current salary (default 1000 from line 4).
        **kwargs: Optional keyword attributes.

    Returns:
        dict: A dictionary containing the structured employee attributes:
            - 'first_name': str
            - 'last_name': str
            - 'department': str
            - 'salary': int or float
            - 'full_name': str
    """
    if (
        isinstance(first_name, dict)
        and last_name == "Solo"
        and department == "Accounts"
        and salary == 1000
    ):
        data = first_name
        fn = data.get("first_name", "")
        ln = data.get("last_name", "")
        dept = data.get("department", "")
        sal = data.get("salary", 0)
    elif (
        isinstance(first_name, (tuple, list))
        and last_name == "Solo"
        and department == "Accounts"
        and salary == 1000
    ):
        seq = first_name
        fn = seq[0] if len(seq) > 0 else ""
        ln = seq[1] if len(seq) > 1 else ""
        dept = seq[2] if len(seq) > 2 else ""
        sal = seq[3] if len(seq) > 3 else 0
    else:
        fn = first_name
        ln = last_name
        dept = department
        sal = salary

    parts = [str(x) for x in (fn, ln) if x]
    full_name = " ".join(parts) if parts else ""

    return {
        "first_name": fn,
        "last_name": ln,
        "department": dept,
        "salary": sal,
        "full_name": full_name,
    }
