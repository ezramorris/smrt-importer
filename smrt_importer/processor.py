"""SMRT Importer directory processor."""


from pathlib import Path
from time import sleep

from smrt_importer.config import config
from smrt_importer.loader import SMRTLoader, DecodingError
from smrt_importer.db import insert_file


def process_file(path):
    """Load data from a single file, save to DB, then move to processed dir
    (if successful) or failed dir.
    
    path: path (string or Path object) to a SMRT file.
    """

    path = Path(path)

    # Ensure processed and failed directories exist.
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.failed_dir.mkdir(parents=True, exist_ok=True)

    print(f'Processing {path}...')
    try:
        loader = SMRTLoader()
        file = loader.load_file(path)
        insert_file(file)
    except Exception as e:
        print(f'    Failed: {e}')
        dest = config.failed_dir / path.name
        raise
    else:
        print('    OK')
        dest = config.processed_dir / path.name
    finally:
        path.rename(dest)


def process_dir(path=config.incoming_dir):
    """Load all SMRT files in a directory and save to DB.

    Any erroneous files will be skipped and a message printed.
    
    path: path (string or Path object) to a directory containing SMRT files.
          Defaults to configured incoming directory.
    """

    path = Path(path)
    for filepath in path.glob('*.SMRT'):
        process_file(filepath)


def watch_dir(path=config.incoming_dir):
    """Continuously watch a directory for new SMRT files, until killed.

    The directory will be created if it does not exist.
    
    path: path (string or Path object) to a directory containing SMRT files.
          Defaults to configured incoming directory.
    """

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            process_dir(path)
            sleep(0.5)
    
    # Hide keyboard interrupt exception message and silently exit.
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    watch_dir()
