#!/usr/bin/env python3

import argparse
import re
from yattag import Doc

named_environments = {
        'theorem':'Теорема', 
        'lemma':'Лемма', 
        'example':'Пример', 
        'hint':'Подсказка', 
        'remark':'Замечание'
}

enumerateable_envs = set(named_environments.keys())
class ParserError(Exception):
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
        self.value = 1
        self.child = None
    def reset(self):
        self.value = 1
        if self.child:
            self.child.reset()
    def increase(self):
        self.value += 1
        if self.child:
            self.child.reset()
    def __str__(self):
        my_str = str(self.value)
        if self.child:
            my_str += '.'+str(self.child)
        return my_str

def environment_begin_end(env, label=None, number=None, optional=None):
    if env == 'document':
        return ('', '')

    doc, tag, text = Doc().tagtext()
    stop_sign = "!!!chahpieXeiDu3zeer3Ki"

    env2tag = {'itemize':'ul', 'enumerate':'ol'}

    if env == 'itemize' or env == 'enumerate':
        with tag(env2tag[env]):
            text(stop_sign)
    else:
        with tag("div", klass="env_" + env):
            if label:
                doc.attr(id="label_" + label)
            if env in named_environments:
                with tag("span", klass="_env_name"):
                    text(named_environments[env])
            text(" ")
            if number:
                with tag('span', klass='_env_number'):
                    text(number)
            text(" ")
            if optional:
                with tag('span', klass='_env_opt_text'):
                    text(optional)
            text(stop_sign)
    ret = doc.getvalue()
    index = ret.index(stop_sign)
    begin = ret[:index]+"\n"
    end = ret[index + len(stop_sign):]+"\n"

    return (begin, end)

def process_lines(lines):
    counters = {}

    out = []

    environments_stack = []

    # first pass
    for line_num, line in enumerate(lines):
        sl = line.strip()

        # %-comments
        if sl.startswith("%"):
            continue

        # environments
        elif sl.startswith(r"\begin{"):
            m = re.match(r"\\begin{(?P<environment>\w+)}\s*(\[(?P<optional>[^\]]+)\])?\s*(\\label{(?P<label>[^}]+)})?", sl)
            if not m:
                raise ParserError("Can't parse \\begin{, regex doesn't match", line_num, line)
            environment, _, optional, _, label = m.groups()
            number = None
            if environment in enumerateable_envs:
                counter = counters.get(environment, Counter())
                # get counter from counters and create new if there
                # is no such counter
                number = str(counter)
                counter.increase()

            begin, end = environment_begin_end(environment, label=label, number=number, optional=optional) 

            out.append(begin)

            environments_stack.append( (environment, end) )
            # We record to stack the environment we processed and its end
            # part. When the environment we'll be closed, we'll just get its
            # end part from the stack
        elif sl.startswith(r"\end{"):
            m = re.match(r"\\end{([^}]+)}", sl)
            if not m:
                raise ParserError(
                        "Can't parse \\end{",
                        line_num,
                        line
                )
            environment = m.group(1)
            rec_env, end = environments_stack.pop()
            if environment != rec_env:
                raise ParserError(
                        "Environment %s ended with %s" % (rec_env, environment),
                        line_num, 
                        line
                )
            out.append(end)
        else:
            out.append(line)
    return out

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Converts latex to html')
    parser.add_argument('texfile',metavar='texfile',type=str,help='texfile to process')
    args=parser.parse_args()

    texfile=args.texfile
    with open(texfile) as fp:
        try:
            lines = fp.readlines()
        except ParserException as e:
            print(e)
    out = process_lines(lines)
    print("".join(out))


