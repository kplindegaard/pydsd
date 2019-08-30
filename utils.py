import redis
import json


def get_client(host='127.0.0.1'):
    client = redis.StrictRedis(host=host, decode_responses=True)
    return client


def group_exists(client, stream_name, group):
    try:
        res = client.xinfo_groups(stream_name)
        print(res)
        groups = list(map(lambda x: x['name'], res))
        print(groups)
        return group in groups
    except redis.exceptions.RedisError:
        return False


def push_stream(client, stream_name, model_name, input, output):
    payload = {
        'name': model_name,
        'in': json.dumps(input),
        'out': json.dumps(output)
        }
    client.xadd(stream_name, payload)


def get_all(client, stream_name):
    # client = get_client()
    return client.xrange(stream_name)


def deserialize_payload(payload):
    model_name = payload['name']
    input = json.loads(payload['in'])
    output = json.loads(payload['out'])
    return model_name, input, output
