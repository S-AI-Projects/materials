def get_path(filename):
    """Return file's path or empty string if no path.

    Representative outputs:
      get_path('/dir/file.py') -> '/dir'
      get_path('file.py')       -> ''
      get_path('')              -> ''
    Precondition: filename is str.
    """
    import os
    head, tail = os.path.split(filename)
    return head
