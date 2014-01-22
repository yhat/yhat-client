#!/usr/bin/python
"""Yet another curses-based directory tree browser, in Python.

I thought I could use something like this for filename entry, kind of
like the old 4DOS 'select' command --- cd $(cursoutline.py).  So you
navigate and hit Enter, and it exits and spits out the file you're on.

"""
# There are several general approaches to the drawing-an-outline
# problem.  This program supports the following operations:
# - move cursor to previous item (in preorder traversal)
# - move cursor to next item (likewise)
# - hide descendants
# - reveal children
# And because it runs over the filesystem, it must be at least somewhat lazy
# about expanding children.
# And it doesn't really bother to worry about someone else changing the outline
# behind its back.
# So the strategy is to store our current linear position in the
# inorder traversal, and defer operations on the current node until the next
# time we're traversing.


import curses.wrapper, time, random, cgitb, os, sys
PROJECT_DIR = os.path.join(os.environ['HOME'], ".yhat/templates")

cgitb.enable(format="text")
ESC = 27
result = ''

def main(stdscr):
    cargo_cult_routine(stdscr)
    stdscr.nodelay(0)
    curidx = 0
    pending_action = None
    pending_save = False


    while 1:
        stdscr.clear()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        line = 0
        stdscr.attrset(curses.color_pair(0))
        stdscr.addstr(line, 3, "Templates")
        line += 1
        stdscr.attrset(curses.color_pair(0))
        stdscr.addstr(line, 0, "="*40)
        line += 1
        offset = max(0, curidx - curses.LINES + 3)

        if os.path.isdir(PROJECT_DIR):
            templates = [f[:-5] for f in os.listdir(PROJECT_DIR) if f.endswith(".json")]
        else:
            templates = []
        templates.append('*new project*')
        templates.append('*search*')
        for name in templates:
            if line == curidx:
                stdscr.attrset(curses.color_pair(1) | curses.A_BOLD)
                if pending_action:
                    getattr(data, pending_action)()
                    pending_action = None
                elif pending_save:
                    global result
                    result = name
                    return
            else:
                stdscr.attrset(curses.color_pair(0))
            if 0 <= line - offset < curses.LINES - 1:
                stdscr.addstr(line - offset, 3, name)

            line += 1
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_UP:
            curidx -= 1
        elif ch == curses.KEY_DOWN:
            curidx += 1
        elif ch == curses.KEY_PPAGE:
            curidx -= curses.LINES
            if curidx < 0:
                curidx = 0
        elif ch == curses.KEY_NPAGE:
            curidx += curses.LINES
            if curidx >= line:
                curidx = line - 1
        elif ch == curses.KEY_RIGHT:
            pending_action = 'expand'
        elif ch == curses.KEY_LEFT:
            pending_action = 'collapse'
        elif ch == ESC:
            return
        elif ch == ord('\n'):
            pending_save = True
        curidx %= max(2, line)

def cargo_cult_routine(win):
    win.clear()
    win.refresh()
    curses.nl()
    curses.noecho()
    win.timeout(0)

def open_tty():
    saved_stdin = os.dup(0)
    saved_stdout = os.dup(1)
    os.close(0)
    os.close(1)
    stdin = os.open('/dev/tty', os.O_RDONLY)
    stdout = os.open('/dev/tty', os.O_RDWR)
    return saved_stdin, saved_stdout

def restore_stdio((saved_stdin, saved_stdout)):
    os.close(0)
    os.close(1)
    os.dup(saved_stdin)
    os.dup(saved_stdout)

if __name__ == '__main__':

    saved_fds = open_tty()
    try:
        curses.wrapper(main)
    finally:
        restore_stdio(saved_fds)
    if result=="*search*":
        result = raw_input("query: ")