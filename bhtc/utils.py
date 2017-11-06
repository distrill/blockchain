'''
    general utility helper functions
'''

import datetime

import block
from config import CHAINDATA_DIR, BLOCK_VAR_CONVERSIONS


def dict_from_block_attributes(**kwargs):
    '''
        turn all function params into a dictionary
    '''
    info = {}
    for key in kwargs:
        if key in BLOCK_VAR_CONVERSIONS:
            info[key] = BLOCK_VAR_CONVERSIONS[key](kwargs[key])
        else:
            info[key] = kwargs[key]
    return info


def create_new_block_from_prev(prev_block=None, data=None, timestamp=None):
    '''
        generate a new block given previous block and data
    '''
    if not prev_block:
        index = 0
        prev_hash = ''
    else:
        index = int(prev_block.index) + 1
        prev_hash = prev_block.hash

    if not data:
        filename = '%sdata.txt' % CHAINDATA_DIR
        with open(filename, 'r') as data_file:
            data = data_file.read()

    if not timestamp:
        timestamp = datetime.datetime.now().timestamp()

    nonce = 0
    block_info_dict = dict_from_block_attributes(
        index=index, timestamp=timestamp, data=data, prev_hash=prev_hash, nonce=nonce)
    new_block = block.Block(block_info_dict)
    return new_block
