from config import h, m, k, d, MAX_CYCLES
from utils import get_client, group_exists, push_stream, serialize_payload, deserialize_payload
import os

OUTPUT_STREAM = 'velocities'
INPUT_STREAM = 'positions'
GROUP_NAME = 'vel_group'
CONSUMER_NAME = 'vel_consumer'
BLOCK_TIME = 10000
MAX_CYCLES = 1000


def update_velocity(u, y, h, m, k, d):
    ma = -k * u['x'] - d * u['v']
    y_next = dict(u)
    y_next['v'] = u['v'] + h * 1.0 / m * ma
    y_next['t'] += h
    return y_next


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    print("Starting {0}. Connect to Redis on {1}".format(__file__, host))
    c = get_client(host=host)
    if not group_exists(c, INPUT_STREAM, GROUP_NAME):
        c.xgroup_create(INPUT_STREAM, GROUP_NAME, mkstream=True)
    block_count = 0
    handled = 0
    stream_id = {INPUT_STREAM: '>'}  # Start reading incoming messages
    while block_count < 10 and handled < MAX_CYCLES:
        response = c.xreadgroup(GROUP_NAME, CONSUMER_NAME, stream_id, block=BLOCK_TIME)
        if len(response) > 0:
            for data in response:
                id = data[1][0][0]
                payload = data[1][0][1]

                # Deserialize payload
                model, y, u = deserialize_payload(payload)

                # Update the state
                y_next = update_velocity(u, y, h, m, k, d)

                # Push to output stream
                payload = serialize_payload(model, u, y_next)
                push_stream(c, OUTPUT_STREAM, payload)

                # Ack that we are done
                c.xack(INPUT_STREAM, GROUP_NAME, id)
                handled += 1
        else:
            print('* VELOCITY: Timed out')
            block_count += 1

    c.xgroup_delconsumer(INPUT_STREAM, GROUP_NAME, CONSUMER_NAME)
    c.xgroup_destroy(INPUT_STREAM, GROUP_NAME)
