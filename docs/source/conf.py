# Configuration file for the Sphinx documentation builder.

import os
import sys
import re

from lumache import __version__

# Source code dir relative to this file;
# used by api.rst's autosummary
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))


# -- Project information

project = 'Lumache'
copyright = '2021, Graziella'
author = 'Graziella'

release = __version__
version = __version__

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

#html_theme = 'sphinx_rtd_theme'
html_theme = "pydata_sphinx_theme"

# -- Options for EPUB output
epub_show_urls = 'footnote'


print("wow, we're in conf.py")

# -- Checking if we can fix docstring without manually updating them...
# solution from chatgpt so it might break...

def preserve_newlines(app, what, name, obj, options, lines0):
    """Modify docstrings to preserve manual line breaks."""
    print(f'debug0in: {what!r}, {name!r}, {obj!r}, {options!r}')
    print('debug0', lines0)
    if len(lines0)<=1 or all(len(l.strip())==0 for l in lines0):
        return  # don't mess with anything if only 1 line, or empty.
    lines = [l for l in lines0]  # copy of lines
    first_nonblank = next((i for i, l in enumerate(lines) if len(l.strip())>0))
    lines = lines[first_nonblank:]
    # make groups of lines with same type
    groups = []
    group = []
    gtype = None
    for l in lines:
        if len(l.strip())>0:
            ltype = 'text'
        else:
            ltype = 'empty'
        if gtype is None:
            gtype = ltype
        if ltype == gtype:
            group.append(l)
        else:
            groups.append((gtype, group))
            group = [l]
            gtype = ltype
    groups.append((gtype, group))
    # groups of text lines need leading '| ' to respect manual line breaks.
    # however, need to handle param lines in a special way.
    #   pname: type / other details
    #       description (maybe)
    # --> if no description, add blank description.
    # --> if description, prepent '| ' in description lines, but indented appropriately.
    newlines = []
    for gtype, group in groups:
        if gtype == 'empty':
            newlines.extend(group)
        else:
            assert gtype == 'text'
            param_pattern = r'\s*([\w]+(?:,\s*[\w]+)*)\s*:\s*(.+)'
            if re.fullmatch(param_pattern, group[0]):  # param group
                indent_ns = [len(l) - len(l.lstrip()) for l in group]
                params_lines = []  # groups of plines
                indent = None
                for i in range(len(group)):
                    l = group[i]
                    if indent is None:  # first line -- new param
                        assert i==0
                        indent = indent_ns[0]
                        sub_indent_n = None
                        plines = [l]
                    elif indent_ns[i] == indent:  # next new param
                        if len(plines) == 1:  # no description --> make bold & add blank description.
                            plines[0] = f'**{plines[0]}**'
                            plines.append('')
                        params_lines.append(plines)
                        sub_indent_n = None
                        plines = [l]
                    elif indent_ns[i] > indent:  # description line
                        if sub_indent_n is None:
                            sub_indent_n = indent_ns[i]
                            sub_indent = l[:sub_indent_n]
                        plines.append(f'{sub_indent}| {l[sub_indent_n:]}')
                    else:
                        raise ValueError(f"unexpected indent: {l!r}")
                # add final param group
                if len(plines) == 1:
                    plines[0] = f'**{plines[0]}**'
                    plines.append('')
                params_lines.append(plines)
                # add to newlines
                for plines in params_lines:
                    newlines.extend(plines)
            else:  # non-param group
                indent_n = len(group[0]) - len(group[0].lstrip())
                indent = group[0][:indent_n]
                grouplines = [f'{indent}| {l}' for l in group]
                newlines.extend(grouplines)
    # edit input lines to adjust sphinx output :)
    print('debug1', newlines)
    lines0[:] = newlines

def setup(app):
    app.connect("autodoc-process-docstring", preserve_newlines)
