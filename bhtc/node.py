''' communicate with other nodes, display current agreed-upon blockchain '''

import json
import argparse

from flask import Flask, jsonify, request
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

import sync
import mine
from config import STANDARD_ROUNDS, CHAINDATA_DIR

node = Flask(__name__)
sched = BackgroundScheduler(standalone=True)

# node_blocks = sync.sync()

sync.sync(save=True)


@node.route('/blockchain.json', methods=['GET'])
def blockchain():
    '''
      Shoots back the blockchain, which in our case, is a json list of hashes
      with the block information which is:
        index
        timestamp
        data
        hash
        prev_hash
    '''
    local_chain = sync.sync_local()
    json_blocks = json.dumps(local_chain.block_list_dict())
    return json_blocks


@node.route('/mined', methods=['POST'])
def mined():
    '''
        accepts incoming blocks that peers have mined
    '''
    possible_block_dict = request.get_json()
    sched.add_job(
        mine.validate_possible_block,
        args=[possible_block_dict],
        id='validate_possible_block'
    )
    return jsonify(received=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BHTC node')
    parser.add_argument('--mine', '-m', dest='mine', action='store_true')
    parser.add_argument(
        '--port', '-p', default='5000',
        help='what port we will run the node on'
    )
    args = parser.parse_args()

    filename = '%sdata.txt' % CHAINDATA_DIR
    with open(filename, 'w') as data_file:
        data_file.write('Mined by node on port %s' % args.port)

    if args.mine:
        mine.sched = sched  # override the BlockingScheduler. this seems gross and leaky af to me
        job_options = {'rounds': STANDARD_ROUNDS, 'start_nonce': 0}
        sched.add_job(mine.mine_for_block, kwargs=job_options, id='mining')
        sched.add_listener(
            mine.mine_for_block_listener,
            apscheduler.events.EVENT_JOB_EXECUTED
        )
    sched.start()

    node.run(host='127.0.0.1', port=args.port)
