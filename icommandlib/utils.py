def stripshot(text):
    """
    Strips whitespace from right and bottom of
    a terminal screenshot.

    >>> stripshot(u'a\\nb\\n')
    'a\\nb'

    >>> stripshot(u'a   \\nb    \\n    \\n')
    'a\\nb'

    >>> stripshot(u'a   \\n     \\nc   \\n')
    'a\\n\\nc'
    """
    return u'\n'.join(
        line.rstrip() for line in text.split(u"\n") if line != u""
    ).rstrip()
