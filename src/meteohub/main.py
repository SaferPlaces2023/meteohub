# -------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2024 Saferplaces
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Name:        main.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     17/06/2024
# -------------------------------------------------------------------------------
import click
from .logo import logo
from .module_log import *
from .version import get_version

@click.command()
@click.option('--dataset',  type=click.STRING, required=False, help="The dataset to download. Default is 'COSMO-2I-RUC'.")
@click.option('--date', type=click.STRING, required=False,  help="The datetime to download. Default is latest datetime available.")
@click.option('--out', type=click.Path(exists=False), required=False, help="The output file name.")
@click.option('--version', is_flag=True, required=False, default=False, help="Print the version.")
@click.option('--debug', is_flag=True, required=False, default=False,   help="Debug mode.")
@click.option('--verbose', is_flag=True, required=False, default=False, help="Print some words more about what is doing.")
def main(dataset, date, out, version, debug ,verbose):
    """
    meteohub is as client downloader for https://meteohub.mistralportal.it portal
    """
    set_log_level(verbose, debug)

    if debug:
        click.echo(logo())
    if version:
        click.echo(f"v{get_version()}")
    # do something with args
    # 


    click.echo(click.style(f"Hello world!", fg="bright_green", bold=True))
    return True