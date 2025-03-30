"""
Lumache - Python library for cooks and food lovers.
"""

__version__ = "0.1.1"


class InvalidKindError(Exception):
    """Raised if the kind is invalid."""
    pass


def get_random_ingredients(kind=None):
    """
    Return a list of random ingredients as strings.

    :param kind: Optional "kind" of ingredients.
    :type kind: list[str] or None
    :raise lumache.InvalidKindError: If the kind is invalid.
    :return: The ingredients list.
    :rtype: list[str]
    """
    return ["shells", "gorgonzola", "parsley"]


def test_custom_docstring_format0(x, y=None):
    '''prints x and y. Not intended for actual use; for testing purposes.
    Trying to check how the docstring is rendered.
    '''
    print(x, y)

def test_custom_docstring_format1(x, y=None, **kw):
    '''prints x and y. Not intended for actual use; for testing purposes.
    
    Trying to check how the docstring is rendered.

    x: any value
        wow, x is so cool!
    y: None or bool
        default None
        multiline docs here for y
        I wonder how it will look
    additional kwargs go to print

    returns None
    '''
    print(x, y, **kw)


def test_custom_docstring_format2(x, y):
    '''prints x and y. Not intended for actual use; for testing purposes.
    
    Trying to check how the docstring is rendered.

    x, y: any values
        wow, they are so cool!
        Here's another line about it.

    returns None
    '''
    print(x, y, **kw)

def test_custom_docstring_format3(*, x, y):
    '''prints x and y. Not intended for actual use; for testing purposes.
    
    Trying to check how the docstring is rendered.

    x: any values
        | wow, x is pretty neat!
    y: None or bool
        | default None
        | multiline docs here for y
        | I wonder how it will look
    additional kwargs go to print

    returns None
    '''
    print(x, y, **kw)


def test_custom_docstring_format4(*, x, y):
    '''prints x and y. Not intended for actual use; for testing purposes.
    | Trying to check how the docstring is rendered.
    | 
    | here, added a '|' to the start of each line
    | reference to parameter `x` here
    | 
    | x: any values
    |     wow, x is pretty neat!
    | y: None or bool
    |     default None
    |     multiline docs here for y
    |     I wonder how it will look
    | additional kwargs go to print
    | 
    | returns None
    '''
    print(x, y, **kw)
