'''
    this is the bit that mines new coins in our blockchain
'''

import sys
import logging

import requests
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from block import Block
from config import STANDARD_ROUNDS, NUM_ZEROS
from utils import create_new_block_from_prev
import sync


sched = BlockingScheduler(standalone=True)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    '''
        try and get the next block in the chain
    '''
    if not chain:
        chain = sync.sync_local()
    prev_block = chain.most_recent_block()
    print(prev_block)
    return mine_from_prev_block(
        prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp)


def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    '''
        mine the next block, given a previous block
    '''
    new_block = create_new_block_from_prev(
        prev_block=prev_block, timestamp=timestamp)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    '''
        mine the next block, but only for a given number of rounds
    '''
    # attempt to find a valid nonce to match the required difficulty
    # of leading zeros. we're only going to try 1000
    print("\n\nstart_nonce: %s\nrounds: %s\n\n" % (start_nonce, rounds))
    nonce_range = [i + start_nonce for i in range(rounds)]
    for nonce in nonce_range:
        new_block.nonce = nonce
        new_block.update_self_hash()
        if str(new_block.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            print("block %s mined. Nonce: %s" %
                  (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            return new_block, rounds, start_nonce, new_block.timestamp
    # couldn't find a hash that worked, return rounds and start_nonce
    # so we know what we tried
    return None, rounds, start_nonce, new_block.timestamp


def mine_for_block_listener(event):
    '''
        handle/schedule mining events
    '''
    if event.job_id == 'mining':
        new_block, rounds, start_nonce, timestamp = event.retval
        # if we didn't mine, new_block is None. use rounds
        # and start_nonce to figure what to do next
        if new_block:
            print("Mined a new block!")
            new_block.self_save()
            broadcast_mined_block(new_block)
            sched.add_job(mine_from_prev_block,
                          args=[new_block],
                          kwargs={'rounds': STANDARD_ROUNDS,
                                  'start_nonce': 0},
                          id='mining')
        else:
            print(event.retval)
            sched.add_job(mine_for_block,
                          kwargs={'rounds': rounds,
                                  'start_nonce': start_nonce + rounds,
                                  'timestamp': timestamp},
                          id='mining')
        sched.print_jobs()


def broadcast_mined_block(new_block):
    '''
        send mined_block info to each peer so they can update their shit
    '''
    block_info_dict = new_block.to_dict()
    for peer in PEERS:
        try:
            requests.post(peer + 'mined', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            print("Peer %s is not connected" % peer)
            continue
    return True


def validate_possible_block(possible_block_dict):
    '''
        validate block, and save if valid
    '''
    possible_block = Block(possible_block_dict)
    if possible_block.is_valid():
        # this means someone else won
        possible_block.self_save()
        # kill and restart mining block so it knows it lost
        try:
            sched.remove_job('mining')
            print('removed running mine job in validating possible block')
        except apscheduler.jobstores.base.JobLookupError:
            print("mining job didn't exist when validating possible block")
        print('re-adding mine for block validating_possible_block')
        sched.add_job(
            mine_for_block,
            kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
            id='mining'
        )
        return True
    return False


# pylint: disable-msg = C0103
if __name__ == '__main__':
    kwargs = {'rounds': STANDARD_ROUNDS, 'start_nonce': 0}
    sched.add_job(mine_for_block, kwargs=kwargs, id='mining')
    sched.add_listener(mine_for_block_listener,
                       apscheduler.events.EVENT_JOB_EXECUTED)
    sched.start()
