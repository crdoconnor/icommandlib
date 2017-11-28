def stripshot(text):
    """
    Strips whitespace from screenshot.
    
    >>> stripshot(u'a\\nb\\n')
    'a\\nb'

    >>> stripshot(u'a   \\nb    \\n    \\n')
    'a\\nb'
    """
    return u'\n'.join(
        line.rstrip() for line in text.split(u"\n") if line != u""
    ).rstrip()
