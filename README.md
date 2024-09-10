
# pyarmy

pyarmy is a module that lets workers and a manager communicate across a local network. It can send data and other requests over one network.



## Tech Stack

The workers and managers are built on Python, with asynchronous FastAPI servers integrated.


## Installation

To install the project, clone the repository from GitHub.

```bash
  $ git clone https://github.com/jackjtaylor/pyarmy
```

Then, open the project and create a local virtual environment with fastapi, aiohttp, tinydb, ifaddr and ipaddress installed.
## Usage

To run a worker or manager, simply invoke the relevant file.

```python
python3 worker.py 
```


## Optimisations

The code has been written and refactored to meet PEP8 standards, as well as meet performance standards.

The workers and managers are being written with asynchronous FastAPI servers, which is essential for performance. When scanning a local network, the most costly performance loss comes from waiting for an API repsonse.
