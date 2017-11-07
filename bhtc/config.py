'''
    config stuffs
'''


CHAINDATA_DIR = 'chaindata/'
NUM_ZEROS = 5
STANDARD_ROUNDS = 100000

BLOCK_VAR_CONVERSIONS = {
    'index': int,
    'nonce': int,
    'hash': str,
    'prev_hash': str,
    'timestamp': int,
    'data': str,
}

PEERS = [
    'http://localhost:5000/',
    'http://localhost:5001/',
    'http://localhost:5002/',
    'http://localhost:5003/',
]
