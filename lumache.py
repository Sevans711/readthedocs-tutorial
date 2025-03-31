"""
Lumache - Python library for cooks and food lovers.
"""

import numpy as np

__version__ = "0.1.1"


class InvalidKindError(Exception):
    """Raised if the kind is invalid."""
    pass


# def get_random_ingredients(kind=None):
#     """
#     Return a list of random ingredients as strings.

#     :param kind: Optional "kind" of ingredients.
#     :type kind: list[str] or None
#     :raise lumache.InvalidKindError: If the kind is invalid.
#     :return: The ingredients list.
#     :rtype: list[str]
#     """
#     return ["shells", "gorgonzola", "parsley"]


def test_custom_docstring_format0(x, y=None):
    '''prints x and y. Not intended for actual use; for testing purposes.
    Trying to check how the docstring is rendered.

    |x| is cool, `y` is too.
    '''
    print(x, y)


def formattingbug0(x, y=None):
    '''some weird formatting, I wonder if I can reproduce it here.

    Manages multiple Dimensions and provides methods for working with them, such as:
        current_n_dimpoints, dim_values, enumerate_dimpoints, get_first_dimpoint.
    Additionally, provides load_across_dims, which is useful when loading arrays from multiple files,
        e.g. see EppicBasesLoader, EbysusBasesLoader.
    The logic for managing the dimensions is implemented in __init_subclass__;
        also note the Dimensions may attach methods to subclasses of this class via setup_haver, e.g.:
            class FluidDimension(Dimension, name='fluid'):
                pass   # no special methods for this example

            @FluidDimension.setup_haver  # setup FluidHaver by attaching various relevant properties & methods.
            class FluidHaver(DimensionHaver, dimension='fluid'):
                pass   # no special methods for this example

    when defining a subclass, can provide these kwargs (e.g. class Foo(DimensionHaver, dimension=...)):
        dimension: str or None
            name of the dimension which has a current value associated with it. e.g. "fluid", "component"
        dim_plural: str or None
            plural name for dimension. if None, append 's' to dimension. e.g. "fluids", "components"
    '''
    pass
