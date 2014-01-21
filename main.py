#!/usr/bin/env python
from colorama import init
from colorama import Fore, Back, Style
import os
init()


def prompt_user():
    inputs = [
        {"prompt": "Project Name: ", "variable": "name"},
        {"prompt": "Description: ", "variable": "description"},
        {"prompt": "GitHub username: ", "variable": "github_username"},
        {"prompt": "Your name: ", "variable": "your_name"},
        {"prompt": "Your email: ", "variable": "your_email"}
    ]

    user_input = {}
    for prompt in inputs:
        user_input[prompt['variable']] = raw_input(Fore.CYAN + prompt['prompt'])

    return user_input


import urwid
from project import setup
import os
import sys


PROJECT_DIR = os.path.join(os.environ['HOME'], ".yhat/projects")
if os.path.isdir(PROJECT_DIR):
    choices = [f[:-5] for f in os.listdir(PROJECT_DIR)]
else:
    choices = []

choices.append('*new project*')
choices.append('download template')

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

class QuestionBox(urwid.Filler):
    def keypress(self, size, key):
        if key != 'enter':
            return super(QuestionBox, self).keypress(size, key)
        self.original_widget = urwid.Text(
            u"Nice to meet you,\n%s.\n\nPress Q to exit." %
            edit.edit_text)

def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button, choice):
    # response = urwid.Text([u'You chose ', choice, u'\n'])
    edit = urwid.Edit("Project name: ")
    done = urwid.Button(u'Ok')
    fill = QuestionBox(edit)
    urwid.connect_signal(done, 'click', exit_program)
    main.original_widget = urwid.Filler(urwid.Pile([edit,
        urwid.AttrMap(done, None, focus_map='reversed')]))
    setup(choice, choice)

def exit_program(button):
    raise urwid.ExitMainLoop()

main = urwid.Padding(menu('Templates', choices), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 60),
    valign='middle', height=('relative', 60),
    min_width=20, min_height=9)
urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
