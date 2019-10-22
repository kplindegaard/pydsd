# pydsd
Distributed spring-damper system simulation in Python with Redis streams.

# Installation

Should use Python 3.7.x.
In addition you need Docker installed.

```
docker pull redis
pip install < requirements.txt
```


# Settings

You can play with different settings in `config.py`, for example how many cycles the `velocity.py` app will perform before it terminates. It's also possible to tweak the physical properties of the system.


# Step 1: How to run locally

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


# Step 2: Run with docker-compose

Let's agree it's a hassle to go through the steps in the previous section.
Wouldn't it be better to containerize the two solvers `position` and `velocity`
and start them up all in one go? Furthermore, let's already now jump a little
bit ahead and imagine that we will add additional consumer of the produced
streams and prepare for that.

For now we will settle for this:
1. Create Docker containers for the `positiion` and `velocity` "services".
2. Launch Redis, `position` and `velocity` together using **docker-compose**.

*Note:* To keep things simple, we will just create one container image that hosts
both position and velocity. To launch we will just provide different entry points.

It's a goal to keep images as small as possible, thus we use Alpine as root image. If not already installed, docker and docker-compose pull them automatically.

```bash
# Fist build the image and call it pydsd
docker build -t pydsd .

# Then start Redis, and two copies of pydsd
docker-compose up --force-recreate
```

As before, you should have a `redis-cli` available to trigger the system:

```
xadd positions * name mymodel in "{\"x\": 0, \"v\": 1, \"t\": 0.0}" out "{\"x\": 0, \"v\": 1, \"t\": 0.0}"
```

You should now see time and positions be dumped in the docker-compose console.
Terminate with Ctrl-C and if necessary remove stopped images with

```
docker-compose rm -f
```

# Future steps

Ideas for further work:
* Append a suitable consumer for storage, e.g. something that listens to the
position stream and writes to a timeseries DB like Influx.
* Get rid of the manual trigger. Let's make a simple web page with a UI.
