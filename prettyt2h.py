#!/usr/bin/env python3

# Copyright (c) 2016 Ilya V. Schurov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import re
from yattag import Doc

LANG = "ru"
if LANG == "ru":
    named_envs = {
        'theorem': 'Теорема',
        'lemma': 'Лемма',
        'example': 'Пример',
        'hint': 'Подсказка',
        'remark': 'Замечание'
    }
else:
    named_envs = {
        'theorem': 'Theorem',
        'lemma': 'Lemma',
        'example': 'Example',
        'hint': 'hint',
        'remark': 'remark'
    }

enumerateable_envs = set(named_envs.keys())
list_envs = {'itemize': 'ul', 'enumerate': 'ol'}
mathjax_snipped = """
<head>
<script type="text/javascript" async
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
</head>
"""

class ParseError(Exception):
    def __init__(self, error="", line=-1, context="", *args):
        self.line = line
        self.context = context
        self.error = error
        self.message = "Parser error '%s' occured on line %i with context '%s'" % (
            error, line, context
        )
        super().__init__(self, self.message, error, line, context, *args)


class Counter():
    """
    Very simple class that support latex-style counters with subcounters.
    For example, if new section begins, the enumeration of subsections resets.
    That's all.
    """

    def __init__(self):
        self.value = 0
        self.child = None
        self.parent = None

    def reset(self):
        self.value = 0
        if self.child:
            self.child.reset()

    def increase(self):
        self.value += 1
        if self.child:
            self.child.reset()

    def spawn_child(self):
        self.child = Counter()
        self.child.parent = self
        return self.child

    def __str__(self):
        my_str = str(self.value)
        if self.parent:
            my_str = str(self.parent) + "." + my_str
        return my_str


def mk_safe_css_ident(s):
    # see http://stackoverflow.com/a/449000/3025981 for details
    s = re.sub("[^a-zA-Z\d_-]", "_", s)
    if re.match("([^a-zA-Z]+)", s):
        m = re.match("([^a-zA-Z]+)", s)
        first = m.group(1)
        s = s[len(first):] + "__" + first
    return s


def environment_begin_end(env, label=None, number=None, optional=None):
    if env == 'document':
        return '<html><meta charset="UTF-8">'+mathjax_snipped, '</html>\n'

    doc, tag, text = Doc().tagtext()
    stop_sign = "!!!chahpieXeiDu3zeer3Ki"

    if env == 'itemize' or env == 'enumerate':
        with tag(list_envs[env]):
            text(stop_sign)
    else:
        with tag("div", klass="env_" + mk_safe_css_ident(env)):
            if label:
                doc.attr(id="label_" + mk_safe_css_ident(label))
            if env in named_envs:
                with tag("span", klass="env__name"):
                    text(named_envs[env])
            text(" ")
            if number:
                with tag('span', klass='env__number'):
                    text(number)
            text(" ")
            if optional:
                with tag('span', klass='env__opt_text'):
                    text(optional)
            text(stop_sign)
    ret = doc.getvalue()
    index = ret.index(stop_sign)
    begin = ret[:index] + "\n"
    end = ret[index + len(stop_sign):] + "\n"

    return (begin, end)


def section_tag(level, title, label=None, number=None):
    doc, tag, text = Doc().tagtext()
    with tag("h" + str(level), klass=mk_safe_css_ident("section")):
        if label:
            doc.attr(id="label_" + mk_safe_css_ident(label))
        if number:
            with tag("span", klass="section__number"):
                text(number + ".")
            text(" ")
        text(title)
    return doc.getvalue() + "\n"


def find_matching_bracket(line, start=0):
    brackets = dict(zip("([{", ")]}"))
    opening = line[start]
    closing = brackets[opening]
    depth = 0
    for i, c in enumerate(line[start:], start):
        if c == opening:
            depth += 1
        if c == closing:
            depth -= 1
            if depth == 0:
                return i
    return None


def process_lines(lines):
    counters = {}
    label_to_counter = {}

    out = []

    environments_stack = []
    section_level = 0

    # first pass
    for line_num, line in enumerate(lines):
        sl = line.strip()

        # %-comments
        if sl.startswith("%"):
            continue

        # environments
        elif sl.startswith(r"\begin{"):
            m = re.match(r"\\begin{(?P<environment>\w+)}\s*(\[(?P<optional>[^\]]+)\])?\s*(\\label{(?P<label>[^}]+)})?",
                         sl)
            if not m:
                raise ParseError("Can't parse \\begin{, regex doesn't match", line_num, line)
            environment, _, optional, _, label = m.groups()

            if not environments_stack and environment != 'document':
                raise ParseError("\\begin{document} waited", line_num, line)

            number = None
            if environment in enumerateable_envs:
                counter = counters.get(environment, Counter())
                # get counter from counters and create new if there
                # is no such counter
                counter.increase()
                number = str(counter)

            if label:
                # Store the number of the counter associated with this label for
                # stage 2
                label_to_counter[label] = number

            begin, end = environment_begin_end(environment, label=label, number=number, optional=optional)

            out.append(begin)

            environments_stack.append((environment, end))
            # We record to stack the environment we processed and its end
            # part. When the environment will be closed, we'll just get its
            # end part from the stack
        elif sl.startswith(r"\end{"):
            m = re.match(r"\\end{([^}]+)}", sl)
            if not m:
                raise ParseError(
                    "Can't parse \\end{",
                    line_num,
                    line
                )
            environment = m.group(1)
            rec_env, end = environments_stack.pop()
            if environment != rec_env:
                raise ParseError(
                    "Environment %s ended with %s" % (rec_env, environment),
                    line_num,
                    line
                )
            out.append(end)
            if not environments_stack:
                break
        elif sl.startswith(r"\item"):
            # check if we inside of {enumerate} or {itemize}
            if environments_stack[-1][0] not in list_envs:
                raise ParseError("\\item outside of list environments", line_num, line, environments_stack[-1][0])

            # we produce HTML, not XHTML, and do not bother with closing those tags
            out.append(sl.replace(r"\item", "<li>", 1))
        elif re.match(r"\\(sub)*section(\*)?\{", sl):
            m = re.match(r"\\(sub)*", sl)
            assert m
            level = (len(m.group(0)) - 1) // 3 + 1
            # section -> h1, subsection -> h2 and so on

            m = re.match(r"\\(sub)*section(\*)?\{", sl)

            need_number = m.group(2) is None

            start = len(m.group(0)) - 1
            end = find_matching_bracket(sl, start)

            if not end:
                raise ParseError("section is not closed properly", line_num, line)

            title = sl[start + 1:end]

            ending = sl[end + 1:].strip()
            m = re.match(r"\\label{([^}]+)}", ending)
            if m:
                label = m.group(1)
            else:
                label = None

            if level > section_level + 1:
                raise ParseError("Section level mismatch", line_num, line)

            section_command = "sub" * (level - 1) + "section"
            if need_number:
                if level == section_level + 1 and level > 1 and section_command not in counters:
                    prevsection = "sub" * (level - 2) + "section"
                    counters[section_command] = counters[prevsection].spawn_child()
                if level == 1 and section_command not in counters:
                    counters[section_command] = Counter()
                my_counter = counters[section_command]
                my_counter.increase()
                number = str(my_counter)

                if label:
                    label_to_counter[label] = str(number)
            else:
                number = None

            out.append(section_tag(level, title, label, number))

            section_level = level
            # TODO: reset environment counters if new section begins
        elif environments_stack:
            out.append(sl+"\n")

    # second stage: resolving refs
    out_text = "".join(out)
    def resolve_ref_match(m):
        label = m.group(1)
        if not label:
            return "(??)"
        number = label_to_counter.get(label, "(??)")
        target = "label_" + mk_safe_css_ident(label)
        doc, tag, text = Doc().tagtext()

        with tag("a", href="#"+target, klass="ref"):
            text(number)
        return doc.getvalue()


    out_text = re.sub(r"\\ref{([^}]+?)}", resolve_ref_match, out_text)

    return out_text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts latex to html')
    parser.add_argument('texfile', metavar='texfile', type=str, help='texfile to process')
    args = parser.parse_args()

    texfile = args.texfile
    with open(texfile) as fp:
        try:
            lines = fp.readlines()
        except ParseError as e:
            print(e)
    out = process_lines(lines)
    print("".join(out))
