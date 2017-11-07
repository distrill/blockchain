'''
    every blockchain gotta have a first block
    (or sync with peers if any are active)
'''

import os
import datetime

import argparse

from config import NUM_ZEROS, CHAINDATA_DIR
import utils
import sync


def mine_first_block():
    '''
        Every blockchain need it's genesis yo
    '''
    first_block = utils.create_new_block_from_prev(
        prev_block=None, data='First block yo.')
    first_block.update_self_hash()

    while str(first_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        first_block.nonce += 1
        first_block.update_self_hash()

    assert first_block.is_valid()
    return first_block


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generating Blockchain')
    parser.add_argument(
        '--first',
        '-f',
        dest='first',
        help='generate the first node ourselves'
    )
    args = parser.parse_args()

    if not os.path.exists(CHAINDATA_DIR):
        os.mkdir(CHAINDATA_DIR)

    if args.first:
        if os.listdir(CHAINDATA_DIR) == []:
            first_block = mine_first_block()
            first_block.self_save()
            filename = '%sdata.txt' % CHAINDATA_DIR
            with open(filename, 'w') as data_file:
                data_file.write('First Block. (this is the hook motherfucker)')
        else:
            print('chaindata directory already has files. If you want to generate a first block, delete files and rerun')
    else:
        # this is the expected case, sync from peers (fuck you mist y u take so long)
        print('syncing')
        sync.sync(save=True)
