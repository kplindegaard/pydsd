# pydsd
Distributed spring-damper system simulation in Python with Redis streams.

# Installation

Should use Python 3.7.x.
In addition you need Docker installed.

```
docker pull redis
pip install < requirements.txt
```

# How to run

Fire three consoles. You need one for redis-cli and two for the velocity and position modules respectively.

In console 1 you start Redis as a daemon and also exec redis-cli
```
docker run -d --rm -p 6379:6379 redis
docker docker exec -it <insert container id from above> redis-cli
```

In console 2 and 3 you start the `velocity.py` and `position.py` apps:

```
python velocity.py
```

```
python position.py
```

Now the position and velocity apps listen to the output from one another to start integrating. Nothing will happen until something is posted on one of the streams. As of now, that "trigger" has to be posted from Redis' cli.

Thus, go back to console #1 and post a full payload to the `position` stream to get the
velocity consumer to kickstart the ping-pong effect.

```
xadd positions * name mymodel in "{\"x\": 0, \"v\": 1, \"t\": 0.0}" out "{\"x\": 0, \"v\": 1, \"t\": 0.0}"
```

This sparks an infinitely long simulation of the mass-spring-damper system, but `velocity.py` is designed to only do 1000 interations be default. When 1000 cycles are done, it shuts itself down. Eventually `position.py` will time out and die since there are no incoming velocity messages any longer.


# Settings

You can play with different settings in `config.py`, for example how many cycles the `velocity.py` app will perform before it terminates. It's also possible to tweak the physical
properties of the system.
