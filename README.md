# SMRT Importer
Tool to import SMRT files into a database.

On startup, the tool creates a `data` directory, containing an SQLite database
(`db`), and three subdirectories: `incoming`, `processed` and `failed`.

When running, the tool will constantly monitor the `incoming` directory and
process any SMRT files which are placed in it. If the file is processed 
successfully, it is moved to the `processed` directory. If an error occurs
whilst processing, or the file has previously been processed, it is moved to
the `failed` directory.

The database contains two tables:
* Each row in `file` contains information about a file which has been 
  successfully processed:
    * Filename
    * Creation time
    * Imported time
    * Generation number
* Each row in `record` contains information about a single record received:
    * Which `file` it originated from
    * Meter number
    * Measurement time
    * Consumption

If a file is placed into `incoming` which has already been processed (by 
filename), it will be skipped and moved to `failed`.

If a file (with a different name) contains a record for a meter number and
measurement time combination which has already been received, the old data
is overwritten.

## Running

This tool may be executed directly using Python >=3.7, or with Docker.

### Running with Python

It is strongly recommended to run this in a virtual environment so the 
correct dependencies can be installed and avoid polluting your global 
environment.

1.  Clone this repo.
2.  Change directory to the repo and create a virtual environment:

        # Windows
        python.exe -m venv venv
        venv\Scripts\activate

        # *nix
        python -m venv venv
        . venv/bin/activate

3.  Install:

        pip install -e .

4.  Run:

        smrt-importer

### Running with Docker

1.  Clone this repo.

2.  Run from within the repo to build and run the Docker image:

        docker compose up

This mounts the `data` directory in the container, so shares the DB and
input/output directories with the host.

Please note that in some circumstances, no output will be shown from the 
application when run with Docker.

If you have made changes to configuration/code etc., you can rebuild by 
running:

    docker compose up --build

To clean up:

    docker compose down --rmi all

## Configuration

`config.ini` contains configuration options for the locations of DB and 
directories.

Please note that the Docker Compose configuration mounts the `data` directory,
so assumes the DB and directories will be within it.
