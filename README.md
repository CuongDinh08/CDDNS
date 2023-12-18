# CDDNS

CDDNS is an open-source dynamic Domain Name System (DDNS). Currently, this project is supporting Cloudflare.

## Pre-requirement

- Python 3.10.12
- pip 22.0.2

## Installation

### (Optional) Create virtual environment

Create virtual environment to manage installed modules and libraries for each project.

```bash
python3 -m venv env
source env/bin/activate
```

### Install require libraries

Install libraries and modules which are required for CDDNS.

```bash
pip3 install -r requirements.txt
```

### Create setting file

You need to create setting file before run CDDNS. Create ```settings.py```, follow structure and instructions in ```sample-settings.py```.

### Run CDDNS

Run CDDNS in background mode.

```bash
nohup python3 cddns.py &
```
