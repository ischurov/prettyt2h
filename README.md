# prettyt2h: the simplest LaTeX to HTML convertor

**THE PROJECT IS ABANDONED**

The project is abandoned after several hours of work in favor of
[DocOnce](https://github.com/hplgit/doconce) tool which solves the issue I
experienced. The following README is left for historical purposes.

## Idea
There are a lot of (La)TeX to HTML converters. All of them are unusable. The main reasons for that are  the following:

1. As TeX is Turing-complete language, it is virtually impossible to parse (La)TeX with anything except of
(La)TeX itself.
2. Most of the converters were written a long time ago. Most notably, they are not aware about excellent
[MathJax](https://www.mathjax.org/) tool that parses rather rich subset of LaTeX equation language on the client side.
3. Therefore, the converters try to parse equations (which is difficult) and try to be universal (which is impossible,
due to 1) and fail.

The approach of `prettyt2h` is different:

 1. First of all, we are not going to parse equations. Let MathJax deal with them, it's really good thing!
 2. Then, we are not going to make universal converter. We consider only very, very small subset of a general LaTeX syntax. However,  this syntax is enough to prepare lecture notes, simple papers and books. At least for the author of this tool.
 3. Moreover, we impose additional restrictions on the syntax to make it more parser-friendly.

 Most probably, you will not be able to use `prettyt2h` with your LaTeX files. However, if you'll write LaTeX files with
 `prettyt2h` in mind, you will be able to get pretty HTML pages from your LaTeX files in a moment.

## Features

1. All formulas are carefully preserved to proceed with MathJax on the client
side. (The most important feature!)
2. The following environments are supported:
    - amsthm-style (`theorem`, `lemma`, `example`, `hint`, `remark` and so on);
    - `enumerate` and `itemize`;
3. Cross-refs (`\label` and `\ref`) are supported (more or less).
4. `section`, `subsection`, `subsubsection`, ..., `section*`, `subsection*`, ... are supported.
4. `%`-comments partially supported (lines that begin with `%` will be ignored)

### Planned
1. Equation enumeration and `\eqref`.
2. Figures and tables.

## Limitations
This is rather dirty solutions. We use regexes and all other bad stuff for parsing.
So you have to obey the rules to make parser happy.

- Everything outside `{document}` environment is ignored.
- Environments should begin with `\begin{...}` statement, followed by possible `\label`.
statement, no other text on the same line is permitted.  
- Environments should end with `\end{...}` statement, no other text on the same
    line is permitted.
- The level of section can increase no more than by 1 (e.g. \subsubsection after \section is forbidden).

## Testcase
This is not very comprehensive testcase. See more testcases in the appropriate directory.

    \begin{document}
        \section*{Introduction}
        This is a test.

        \section{It was the beginning}\label{sec:beg}
            This is another test.

            \begin{theorem}[Pythagoras]\label{thm:Pyth}
                Pythagoras says:
                \[
                    c^2 = a^2 + b^2
                \]
            \end{theorem}
            \begin{proof}
                It's obvious.
            \end{proof}
        \section{The next one}
            We discussed Pythagorean theorem in section~\ref{sec:beg} (see
            Theorem~\ref{thm:Pyth} there.
            \begin{enumerate}
                \item One;
                \item Two;
            \end{enumerate}
    \end{document}
