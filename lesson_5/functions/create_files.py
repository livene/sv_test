from typing import Optional

from pretty_utils.miscellaneous.files import touch, write_json, read_json
from pretty_utils.type_functions.dicts import update_dict

from utils.files_utils import write_row_to_csv_file
from data import config
from data.models import InitialCsvData


def create_files():
    touch(path=config.FILES_DIR)
    touch(path=config.DEBUG_LOG, file=True)
    if touch(path=config.IMPORT_PATH, file=True):
        write_row_to_csv_file(path=config.IMPORT_PATH, row=InitialCsvData.HEADER)

    try:
        current_settings: Optional[dict] = read_json(path=config.SETTINGS_PATH)
    except FileNotFoundError:
        current_settings = {}

    settings = {
        'stargate_swaps': {'from': 5, 'to': 15},
        'stargate_swaps_usdc_amount': {'from': 0, 'to': 0},
        'coredao_swaps': {'from': 5, 'to': 15},
        'coredao_swaps_amount': {'from': 0.001, 'to': 0.01},
        'testnetbridge_swaps': {'from': 5, 'to': 15},
        'testnetbridge_swaps_amount': {'from': 0.009, 'to': 0.012},
        'initial_actions_delay': {'from': 3600, 'to': 7200},
        'activity_actions_delay': {'from': 259200, 'to': 345600},
    }
    write_json(path=config.SETTINGS_PATH, obj=update_dict(modifiable=current_settings, template=settings), indent=2)


create_files()
