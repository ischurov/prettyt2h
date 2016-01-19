# prettyt2h

This is a pretty simple LaTeX to HTML convertor. We do not try to build a comprehensive
convertor, only a small subset of LaTeX can be processed properly.
The idea is that one needs only this part of the syntax to write lecture notes
and books. So one can write LaTeX and get HTML + MathJax instantly.

## Planned features

1. All formulas are carefully preserved to proceed with MathJax on the client
side.
2. The following environments are supported:
- amsthm-style (`theorem`, `lemma`, `example`, `hint`, `remark` and so on);
- `enumerate` and `itemize`;
3. Cross-refs (`\label` and `\ref`) are supported (more or less).
4. Also supported `section`, `subsection`, `subsubsection` as well as
    asterix-version of them;
5. Equation enumeration and `\eqref` are supported as well.
6. %-comments (the corresponding lines are ignored)

## Limitations
This is a really dirty solution. I do not have time to make proper parser and so
on, so I'll use the most horrible design decisions like extensive regex using.
This lead to a bunch of limitations imposed to the input LaTeX text. Hopefully,
they are not very restrictive in terms of output.

- Environments should begin with `\begin{...}` statement, followed by possible `\label`
statement, no other text on the same line is permitted.  
- Environments should end with `\end{...}` statement, no other text on the same
    line is permitted.

## Testcase
This is not very comprehensive testcase

    \begin{document}
        \section*{Introduction}
        This is a test.

        \section{It was the beginning}\label{sec:beg}
            This is another test.

            \begin{theorem}[Pythagor]\label{thm:Pyth}
                Pythogor says:
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
