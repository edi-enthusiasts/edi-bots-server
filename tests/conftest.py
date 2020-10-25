# -*- coding: utf-8 -*-

import logging
import os
import pytest
import shutil
import subprocess
import sys
import bots.botsglobal as botsglobal_module
import bots.botsinit as botsinit_module


# Make sure botsinit is only initialized once when starting up the library.
@pytest.fixture(scope='session')
def general_init():
    botsinit_module.generalinit()


@pytest.fixture(scope='session')
def botssys(general_init):
    return botsglobal_module.ini.get('directories', 'botssys')


@pytest.fixture(scope='session')
def init_charsets(general_init):
    botsinit_module.initbotscharsets()


@pytest.fixture(scope='session')
def bots_db(general_init):
    botsinit_module.connect()
    yield botsglobal_module.db
    botsglobal_module.db.close


@pytest.fixture(scope='module')
def engine_logging(general_init):
    botsglobal_module.logger = botsinit_module.initenginelogging('engine')
    yield botsglobal_module.logger

    # GC the handlers so their file handles close, and the log file can properly rotate.
    botsglobal_module.logger.handlers.clear()


@pytest.fixture(scope='module')
def dummy_logging(botssys):
    botsglobal_module.logger = logging.getLogger('dummy')
    botsglobal_module.logger.setLevel(logging.ERROR)
    botsglobal_module.logger.addHandler(logging.StreamHandler(sys.stdout))
    yield botsglobal_module.logger

    # GC the handlers so their file handles close, and the log file can properly rotate.
    botsglobal_module.logger.handlers.clear()


@pytest.fixture(scope='module')
def clean_output(botssys):
    shutil.rmtree(os.path.join(botssys, 'outfile'), ignore_errors=True)  # remove whole output directory


@pytest.fixture(scope='module')
def run_engine(botssys):
    assert not subprocess.call(['python', '-m', 'bots-engine'])
