import sys

import logfire

from ensreg_wf.cli import app


def _setup_logfire():
    logfire.configure(send_to_logfire=False)


_setup_logfire()
app()
