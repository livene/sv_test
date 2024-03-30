import os
import sys
from pathlib import Path

from loguru import logger


if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()


FILES_DIR = os.path.join(ROOT_DIR, 'files')
ABIS_DIR = os.path.join(ROOT_DIR, 'data', 'abis')
DEBUG_LOG = os.path.join(FILES_DIR, 'debug.log')
IMPORT_PATH = os.path.join(FILES_DIR, 'import.csv')
SETTINGS_PATH = os.path.join(FILES_DIR, 'settings.json')

logger.add(f'{DEBUG_LOG}', format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')
# logger.remove()
