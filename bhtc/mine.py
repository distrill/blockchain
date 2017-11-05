from block import Block
import sync

import datetime as date
import time
import json
import hashlib

NUM_ZEROS = 5


def generate_header(index, prev_hash, data, timestamp, nonce):
    return str(index) + prev_hash + data + str(timestamp) + str(nonce)


def calculate_hash(index, prev_hash, data, timestamp, nonce):
    header_string = generate_header(index, prev_hash, data, timestamp, nonce)
    sha = hashlib.sha256()
    sha.update(header_string.encode('utf-8'))
    return sha.hexdigest()


def mine(last_block):
    index = int(last_block.index) + 1
    timestamp = date.datetime.now().timestamp()
    data = "I'm block #%s" % (index)
    prev_hash = last_block.hash
    nonce = 0

    block_hash = calculate_hash(index, prev_hash, data, timestamp, nonce)
    while str(block_hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        nonce += 1
        block_hash = calculate_hash(index, prev_hash, data, timestamp, nonce)

    print("winning nonce: %s" % (nonce))

    block_data = {}
    block_data['index'] = index
    block_data['timestamp'] = timestamp
    block_data['data'] = data
    block_data['prev_hash'] = prev_hash
    block_data['hash'] = block_hash
    block_data['nonce'] = nonce

    return Block(block_data)


if __name__ == '__main__':
    # something is fucky and my array comes back in backwards or inconsistent order
    # sort as a workaround for now to ensure proper order
    node_blocks = sorted(sync.sync().blocks,
                         key=lambda block: int(block.timestamp))
    prev_block = node_blocks[-1]
    new_block = mine(prev_block)
    new_block.self_save()
