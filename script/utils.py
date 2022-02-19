"""
Project: AsyncFFmpegHelper
Author: hyugogirubato
Script: utils.py
Version: v2022.02.19
"""
import sys

from termcolor import colored, cprint
from colorama import init

init()


def error(message, ignore=False):
    if ignore:
        cprint(message, 'red')
    else:
        cprint(f'ERROR: {message}', 'red')
        sys.exit(1)


def log(_type, message):
    print(f'{colored(_type, "magenta")} {message}')


def warning(message):
    cprint(f'WARNING: {message}', 'yellow')

