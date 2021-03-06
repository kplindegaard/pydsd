from config import h
from utils import get_client, group_exists, push_stream, serialize_payload, deserialize_payload
import os

OUTPUT_STREAM = 'positions'
INPUT_STREAM = 'velocities'
GROUP_NAME = 'pos_group'
CONSUMER_NAME = 'pos_consumer'
BLOCK_TIME = 10000


def update_position(u, y, h):
    y_next = dict(u)
    y_next['x'] = u['x'] + h * u['v']
    return y_next


if __name__ == "__main__":
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    print("Starting {0}. Connect to Redis on {1}".format(__file__, host))
    c = get_client(host=host)
    if not group_exists(c, INPUT_STREAM, GROUP_NAME):
        c.xgroup_create(INPUT_STREAM, GROUP_NAME, mkstream=True)
    block_count = 0
    stream_id = {INPUT_STREAM: '>'}  # Start reading incoming messages
    while block_count < 10:
        response = c.xreadgroup(GROUP_NAME, CONSUMER_NAME, stream_id, block=BLOCK_TIME)
        if len(response) > 0:
            for data in response:
                id = data[1][0][0]
                payload = data[1][0][1]

                # Deserialize payload
                model, y, u = deserialize_payload(payload)

                # Update the state and dump to console
                y_next = update_position(u, y, h)
                print(f"{y_next['t']},{y_next['x']}")

                # Push to output stream
                payload = serialize_payload(model, u, y_next)
                push_stream(c, OUTPUT_STREAM, payload)

                # Ack that we are done
                c.xack(INPUT_STREAM, GROUP_NAME, id)
        else:
            print('* POSITION: Timed out')
            block_count += 1

    c.xgroup_delconsumer(INPUT_STREAM, GROUP_NAME, CONSUMER_NAME)
    c.xgroup_destroy(INPUT_STREAM, GROUP_NAME)
