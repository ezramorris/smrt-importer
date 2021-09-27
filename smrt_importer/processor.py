"""SMRT Importer directory processor."""


from pathlib import Path
from sqlalchemy.exc import IntegrityError
from time import sleep

from smrt_importer.config import config
from smrt_importer.loader import SMRTLoader
from smrt_importer.db import insert_file


def move_file(path: Path, dest: Path):
    """Move a file, adding a suffix if necessary.
    
    path: file path
    dest: destination directory
    """

    newpath = dest / path.name
    i=1
    while newpath.exists():
        newpath = dest / f'{path.stem}_{i}{path.suffix}'
        i+=1

    path.rename(newpath)


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
    except IntegrityError:  # Most likely a unique constraint on File failed.
        print(f'    Already imported, skipping')
        dest = config.failed_dir
    except Exception as e:
        print(f'    Failed: {e}')
        dest = config.failed_dir
    else:
        print('    OK')
        dest = config.processed_dir
    finally:
        move_file(path, dest)


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

    print(f'Watching {path}...')
    try:
        while True:
            process_dir(path)
            sleep(0.5)
    
    # Hide keyboard interrupt exception message and silently exit.
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    watch_dir()
