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
# copyright = '2021, Graziella'
# author = 'Graziella'

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

html_theme = 'sphinx_rtd_theme'
#html_theme = "pydata_sphinx_theme"

# -- Options for EPUB output
epub_show_urls = 'footnote'


print("wow, we're in conf.py")

# -- Checking if we can fix docstring without manually updating them...
# solution from chatgpt so it might break...

class DocstringInfo():
    r'''info about a docstring. Also, helpful methods for converting to sphinx format.

    docstring: str
        the original docstring. Stored at self.docstring, and never changed.
    kind: None, 'sphinx', or 'custom'
        what kind of docstring this is.
        None --> infer from docstring.
                'sphinx' if any line matches the KNOWN_SPHINX_PATTERN, else 'custom'.
                (e.g. if there's a :param...: line, then it's 'sphinx'.)
        'sphinx' --> docstring assumed to already follow all sphinx standards.
        'custom' --> docstring assumed to not follow sphinx standards. (See below)


    "Custom" format is used throughout some of my code. Details:
        - first line is a description of the object. Never a param or other special line.
        - subsequent lines might continue the description.
        - line breaks are intended to be maintained when generating docs pages.
        - some lines tell params but don't specify :param:. Example:
            word: description with any number of words
        - after a param line, subsequent indented lines are a description of that param,
            until indentation level reverts back to same level as param line. Example:
            myparam1: description of myparam1
                continues description of myparam1

                also part of description of myparam1
            no longer part of description (might be a different param, or something else).
        - param "word" could instead be comma-separated words, but nothing fancier.
            E.g. "x, y: value" is treated as params, but "x space: value" is not.
            "Word" is defined to be a sequence of characters matching regex: \w
            Also, these can never be single-word params:
                'Example', 'Examples', 'Return', 'Returns'

        - currently, no other fancy-formatting is recognized.
            - (this might be updated eventually)
        - some patterns will be replaced:
            |x| --> \|x|   # to avoid sphinx interpreting as "substitution".
            `x` --> ``x``  # to tell sphinx to interpret as "code"
    If you don't like all the details of "custom" format, you can just use sphinx format.
    '''
    KNOWN_SPHINX_PATTERN = r'\s*(:param|:type|:return|:rtype|:raise).*:.*'
    PARAM_PATTERN = r'\s*((?!(?:Example|Return)s?)[\w]+(?:,\s*[\w]+)*)\s*:\s*(.+)'

    def __init__(self, docstring, *, kind=None):
        self.docstring = docstring  # original docstring, will never be changed
        self.lines = docstring.splitlines()
        self.kind = self._infer_kind(kind)
        # remove trailing blank lines.
        for i, l in enumerate(self.lines[::-1]):
            if not self.is_blank_line(l):
                break
        last_nonblank_line = len(self.lines) - i
        self.lines = self.lines[:last_nonblank_line]
        self.base_indent = self._infer_base_indent()

    def _infer_kind(self, kind):
        if kind is not None:
            return kind
        if any(re.fullmatch(self.KNOWN_SPHINX_PATTERN, l) for l in self.lines):
            return 'sphinx'
        else:
            return 'custom'

    def _infer_base_indent(self):
        '''return minimum indent across all lines except the first.
        if only nonblank line is the first line, return 0.
        '''
        result = None
        for l in self.lines[1:]:
            if not self.is_blank_line(l):
                indent = self.get_indent_n(l)
                if (result is None) or (indent < result):
                    result = indent
        if result is None:  # all nonblank lines have 0 indent
            result = 0
        return result

    @classmethod
    def from_obj(cls, obj):
        '''return DocstringInfo(obj.__doc__)'''
        return cls(obj.__doc__)

    @staticmethod
    def is_blank_line(line):
        '''returns whether this line is blank.'''
        return len(line.strip()) == 0

    @staticmethod
    def get_indent_n(line):
        '''returns number of leading spaces in line.'''
        return len(line) - len(line.lstrip())

    def nonblank_line_here_or_next(self, i):
        '''return self.lines[i] if nonblank, else first nonblank line after i.'''
        for j in range(i, len(self.lines)):
            if not self.is_blank_line(self.lines[j]):
                return self.lines[j]
        assert False, f'no nonblank lines at {i} or after'

    def param_ilines(self):
        '''return dict of {i: [iline of all description lines]} for param lines in docstring.
        param lines are those which match self.PARAM_PATTERN,
            AND are not indented underneath an existing param line.
            (also, line 0 is NEVER a param line, no matter what.)

        line number) example line:
        0) Example docstring
        1) param1: is a param line
        2)     description line
        3) param2: is another param line
        4)    description line
        5)        another description line
        6)    param 3: still not a param line (too indented)
        7) param4: param line again
        8) back to non-param line
        9)
        10) param5: param line again
        11)     description line again
        12) going to talk about a subset of parameters now:
        13)     subparam1: param line
        14)         description line
        15)     subparam2: param line
        16) 
        17) still non-paramline

        --> result would be:
            {1: [2], 3: [4, 5, 6], 7: [], 10: [11], 13: [14], 15: []}
        '''
        result = {}
        current_indent_n = None
        current_iparam = None
        for i, l in enumerate(self.lines):
            if i == 0:
                continue
            # check if sub-indented below a param_line.
            if current_indent_n is None:
                maybe_param_line = True
            else:  # currently considering maybe description lines.
                nonblank_l = self.nonblank_line_here_or_next(i)
                indent_n = self.get_indent_n(nonblank_l)
                if indent_n > current_indent_n:  # description line
                    maybe_param_line = False
                    result[current_iparam].append(i)
                else:  # no longer a description line
                    current_indent_n = None
                    current_iparam = None
                    maybe_param_line = True
            if maybe_param_line and re.fullmatch(self.PARAM_PATTERN, l):
                current_indent_n = self.get_indent_n(l)
                current_iparam = i
                result[i] = []
        return result

    def line_infos(self):
        '''return (i, linetype, indent_n, line_post_indent) for each line in docstring.

        i is line index.
        linetype is 'text', 'empty', 'param', or 'pdesc'.
            'text' --> misc text (not associated with a param)
            'empty' --> empty line
            'param' --> param line
            'pdesc' --> description line for param
        indent_n is number of spaces before text in line,
            used for prepending '| ' to ensure manual line breaks are respected in sphinx format.
            For blank lines, this is the indent_n of the next nonblank line.
            For text lines, this is the minimum indent across all lines (except the first line).
            For pdesc lines, this is the sub-indent level of the first desc line;
                subsequent desc lines have the same indent_n.
                (This makes the sphinx docs maintain the sub-indentation level as well!)
        line is all the text in the line after removing `indent_n` spaces.
        '''
        result = []
        param_ilines = self.param_ilines()
        current_indent_n = None
        i = 0
        result.append((i, 'text', 0, self.lines[i]))
        i = 1
        while i < len(self.lines):
            l = self.lines[i]
            if self.is_blank_line(l):
                nonblank_l = self.nonblank_line_here_or_next(i)
                indent_n = self.get_indent_n(nonblank_l)
                result.append((i, 'empty', indent_n, ''))
                i = i + 1
            elif i in param_ilines:
                current_indent_n = self.get_indent_n(l)
                result.append((i, 'param', current_indent_n, l[current_indent_n:]))
                if len(param_ilines[i]) >= 1:
                    desc0 = param_ilines[i][0]
                    desc0_nonblank = self.nonblank_line_here_or_next(desc0)
                    subindent_n = self.get_indent_n(desc0_nonblank)
                    for j in param_ilines[i]:
                        linej = self.lines[j]
                        if self.is_blank_line(linej):
                            result.append((j, 'pdesc', subindent_n, ''))
                        else:
                            result.append((j, 'pdesc', subindent_n, linej[subindent_n:]))
                    i = i + len(param_ilines[i])
                i = i + 1
            else:
                result.append((i, 'text', self.base_indent, l[self.base_indent:]))
                i = i + 1
        return result

    def _reconstruct(self):
        '''reconstruct docstring from self.line_infos().
        Mainly for debugging purposes.
        [TODO] result has extra (or not enough?) whitespace compared to docstring,
            but only differs in blank lines, so not a big deal.
        '''
        result = []
        for i, linetype, indent_n, line in self.line_infos():
            if linetype == 'empty':
                result.append('')
            elif linetype == 'text':
                result.append(' '*indent_n + line)
            elif linetype == 'param':
                result.append(' '*indent_n + line)
            elif linetype == 'pdesc':
                result.append(' '*indent_n + line)
            else:
                raise ValueError(f'unknown linetype: {linetype}')
        return '\n'.join(result)

    def to_sphinx(self):
        r'''returns self.docstring, converted to sphinx format.
        See help(type(self)) for more details.

        Equivalent: '\n'.join(self.to_sphinx_lines())
        '''
        return '\n'.join(self.to_sphinx_lines())
        
    def to_sphinx_lines(self):
        r'''returns lines of self.docstring, converted to sphinx format.
        See help(type(self)) for more details.

        Equivalent: self.to_sphinx().split('\n')
        '''
        if self.kind == 'sphinx':
            return self.lines
        elif self.kind == 'custom':
            return self._custom_to_sphinx_lines()
        else:
            raise ValueError(f'unknown kind: {self.kind}')

    def _custom_to_sphinx_lines(self):
        '''convert custom docstring to sphinx format.
        assumes but does not check self.kind=='custom'.
        '''
        result = []
        prev_linetype = None
        for i, linetype, indent_n, line in self.line_infos():
            # avoid sphinx interpreting line as "substitution"
            # (replace |x| with \|x|.)
            line = re.sub(r'[|]([^|]+)[|]', r'\|\g<1>|', line)
            # tell sphinx to interpret `x` as "code" (i.e. ``x``).
            line = re.sub(r'`([^`]+)`', r'``\g<1>``', line)
            # handle indentations properly
            if linetype == 'empty':
                result.append('')
            elif linetype == 'text':
                result.append(' '*indent_n + '| ' + line)
            elif linetype == 'param':
                # sphinx sometimes needs extra blank line between text & param
                # to render param appropriately.
                # (noticed this issue in particular when param indent > text indent.)
                if prev_linetype == 'text':
                    result.append('')
                result.append(' '*indent_n + line)
            elif linetype == 'pdesc':
                result.append(' '*indent_n + '| ' + line)
            else:
                raise ValueError(f'unknown linetype: {linetype}')
            prev_linetype = linetype
        return result

    # # # DISPLAY # # #
    def __repr__(self):
        l = self.nonblank_line_here_or_next(0)  # first nonblank line
        if len(self.lines) > 1:
            l = l + '...'
        if len(l) > 60:
            l = l[:60] + '...'
        return f'{type(self).__name__}({l})'


def sphinx_docstring(f):
    '''return sphinx docstring for this object.
    None if f.__doc__ is None or doesn't exist.
    Else, DocstringInfo(f.__doc__).to_sphinx()
    '''
    if getattr(f, '__doc__', None) is None:
        return None
    else:
        return DocstringInfo(f.__doc__).to_sphinx()

def reformat_pc_docstrings(app, what, name, obj, options, lines0):
    '''modify docstring formatting to be decent even if not written to respect rst standards.
    Many of my docstrings don't respect sphinx / python standards,
        preferring instead to be more readable directly in the source code.
    Thankfully, sphinx provides "autodoc-process-docstring" hook to modify docstrings.
    That's when this function gets called (see sphinx docs on that hook for more details).

    app: the sphinx application object
    what: type of obj: 'module', 'class', 'function', 'method', 'attribute', 'exception'
    name: fully qualified name of obj
    obj: the obj itself
    options: options given to the sphinx directive
    lines: lines of the docstring. Edit in-place to modify the docstring.

    E.g. we want functions like this to not look ugly when rendered by sphinx:
        def f(x,y,z,t, **kw):
            """one line summary.
            Longer description, but we don't want to destroy the line breaks;
                we also want to keep any indents like this one.

            x: int. description about x
            y: None or any value
                description about y
                extends to multiple lines
            z: str   # has no description here
            t: bool.
                description about t
                extends to multiple lines
                    and sometimes includes sub-indents on those lines!
            additional kwargs go to ...

            returns something.
            """
            ...  # code for f goes here.

    [TODO] spend more time fiddling with this function, to make into more "official" format:
        e.g. :param p: for params, :returns: for return info...
    '''
    if len(lines0)<=1 or all(len(l.strip())==0 for l in lines0):
        return  # don't mess with anything if only 1 line, or empty.
    else:
        docstring = '\n'.join(lines0)
        di = DocstringInfo(docstring)
        newlines = di.to_sphinx_lines()
        lines0[:] = newlines

def setup(app):
    app.connect("autodoc-process-docstring", reformat_pc_docstrings)


### OLD STUFF ###

# def preserve_newlines_OLD(app, what, name, obj, options, lines0):
#     '''modify docstring formatting to be decent even if not written to respect rst standards.

#     E.g. want functions like this to not look ugly when rendered by sphinx:
#         def f(x,y,z,t, **kw):
#             """one line summary.
#             Longer description, but we don't want to destroy the line breaks;
#                 we also want to keep any indents like this one.

#             x: int. description about x
#             y: None or any value
#                 description about y
#                 extends to multiple lines
#             z: str   # has no description here
#             t: bool.
#                 description about t
#                 extends to multiple lines
#                     and sometimes includes sub-indents on those lines!
#             additional kwargs go to ...

#             returns something.
#             """
#             ...  # code for f goes here.

#     [TODO] spend more time fiddling with this function, to make into more "official" format:
#         e.g. :param p: for params, :returns: for return info...
#     '''
#     if len(lines0)<=1 or all(len(l.strip())==0 for l in lines0):
#         return  # don't mess with anything if only 1 line, or empty.
#     KNOWN_RST_KEYS = {':param', ':type', ':return', ':rtype', ':raise'}
#     if any(l.lstrip().startswith(k) for l in lines0 for k in KNOWN_RST_KEYS):
#         return  # don't mess with anything if it's already formatted to common sphinx standards.
#     lines = [l for l in lines0]  # copy of lines
#     first_nonblank = next((i for i, l in enumerate(lines) if len(l.strip())>0))
#     lines = lines[first_nonblank:]
#     # make groups of lines with same type
#     groups = []
#     group = []
#     gtype = None
#     for l in lines:
#         if len(l.strip())>0:
#             ltype = 'text'
#         else:
#             ltype = 'empty'
#         if gtype is None:
#             gtype = ltype
#         if ltype == gtype:
#             group.append(l)
#         else:
#             groups.append((gtype, group))
#             group = [l]
#             gtype = ltype
#     groups.append((gtype, group))
#     # groups of text lines need leading '| ' to respect manual line breaks.
#     # however, need to handle param lines in a special way.
#     #   pname: type / other details
#     #       description (maybe)
#     # --> if no description, add blank description.
#     # --> if description, prepent '| ' in description lines, but indented appropriately.
#     newlines = []
#     for gtype, group in groups:
#         if gtype == 'empty':
#             newlines.extend(group)
#         else:
#             assert gtype == 'text'
#             param_pattern = r'\s*([\w]+(?:,\s*[\w]+)*)\s*:\s*(.+)'
#             if re.fullmatch(param_pattern, group[0]):  # param group
#                 indent_ns = [len(l) - len(l.lstrip()) for l in group]
#                 params_lines = []  # groups of plines
#                 indent = None
#                 for i in range(len(group)):
#                     l = group[i]
#                     if indent is None:  # first line -- new param
#                         assert i==0
#                         indent = indent_ns[0]
#                         sub_indent_n = None
#                         plines = [l]
#                     elif indent_ns[i] == indent:  # next new param
#                         if len(plines) == 1:  # no description --> make bold & add blank description.
#                             plines[0] = f'**{plines[0]}**'
#                             plines.append('')
#                         params_lines.append(plines)
#                         sub_indent_n = None
#                         plines = [l]
#                     elif indent_ns[i] > indent:  # description line
#                         if sub_indent_n is None:
#                             sub_indent_n = indent_ns[i]
#                             sub_indent = l[:sub_indent_n]
#                         plines.append(f'{sub_indent}| {l[sub_indent_n:]}')
#                     else:
#                         raise ValueError(f"unexpected indent: {l!r}")
#                 # add final param group
#                 if len(plines) == 1:
#                     plines[0] = f'**{plines[0]}**'
#                     plines.append('')
#                 params_lines.append(plines)
#                 # add to newlines
#                 for plines in params_lines:
#                     newlines.extend(plines)
#             else:  # non-param group
#                 indent_n = len(group[0]) - len(group[0].lstrip())
#                 indent = group[0][:indent_n]
#                 grouplines = [f'{indent}| {l}' for l in group]
#                 newlines.extend(grouplines)
#     # edit input lines to adjust sphinx output :)
#     print('debug1', newlines)
#     lines0[:] = newlines


# def setup(app):
#     app.connect("autodoc-process-docstring", preserve_newlines)
