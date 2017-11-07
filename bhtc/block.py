'''
    blockchains need blocks yo
'''

import hashlib
import json

from config import BLOCK_VAR_CONVERSIONS, CHAINDATA_DIR, NUM_ZEROS


class Block(object):
    '''
        i already said this, blockchains need blocks yo
    '''

    def __init__(self, dictionary):
        '''
          We're looking for index, data, nonce, timestamp, prev_hash
        '''
        self.index = BLOCK_VAR_CONVERSIONS['index'](dictionary['index'])
        self.data = BLOCK_VAR_CONVERSIONS['data'](dictionary['data'])
        self.nonce = BLOCK_VAR_CONVERSIONS['nonce'](dictionary['nonce'])
        self.timestamp = BLOCK_VAR_CONVERSIONS['timestamp'](
            dictionary['timestamp'])
        self.prev_hash = BLOCK_VAR_CONVERSIONS['prev_hash'](
            dictionary['prev_hash'])

        if not hasattr(self, 'hash'):
            self.hash = self.update_self_hash()
        if not hasattr(self, 'nonce'):
            self.nonce = 0

    def header_string(self):
        '''
            generate header string for an instantiated block object
        '''
        return str(self.index) + self.prev_hash + self.data + str(self.timestamp) + str(self.nonce)

    def update_self_hash(self):
        '''
            generate hash for instantiated block object (used a bunch as nonce increments)
        '''
        sha = hashlib.sha256()
        sha.update(self.header_string().encode('utf-8'))
        new_hash = sha.hexdigest()
        self.hash = new_hash
        return new_hash

    def self_save(self):
        '''
            write block state to txt file
        '''
        index_string = str(self.index).zfill(6)
        filename = '%s/%s.json' % (CHAINDATA_DIR, index_string)
        with open(filename, 'w') as block_file:
            json.dump(self.to_dict(), block_file)

    def to_dict(self):
        '''
            quality of life utility to deal with dictionary representation of
            instantiated block object
        '''
        info = {}
        info['index'] = str(self.index)
        info['timestamp'] = str(self.timestamp)
        info['prev_hash'] = str(self.prev_hash)
        info['hash'] = str(self.hash)
        info['data'] = str(self.data)
        info['nonce'] = str(self.nonce)
        return info

    def is_valid(self):
        '''
            currenty validity is only that the hash begins with at least NUM_ZEROS
        '''
        self.update_self_hash()
        return str(self.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS

    def __repr__(self):
        return "Block<index: %s>, <hash: %s>" % (self.index, self.hash)

    def __eq__(self, other):
        return (self.index == other.index and
                self.timestamp == other.timestamp and
                self.prev_hash == other.prev_hash and
                self.hash == other.hash and
                self.data == other.data and
                self.nonce == other.nonce)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.timestamp < other.timestamp

    def __lt__(self, other):
        return self.timestamp > other.timestamp
