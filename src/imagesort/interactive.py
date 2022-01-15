from prompt_toolkit.shortcuts import button_dialog
from .util import UserAborted

def ask_ok_cancel(title, text):
    ok = button_dialog(
        title,
        text,
        buttons=[
            ('Cancel', False),
            ('OK', True)
        ]).run()
    if not ok:
        raise UserAborted


def ask_yes_no(title, text):
    return button_dialog(title, text, buttons=['Yes', True])