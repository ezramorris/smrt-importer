"""SMRT Importer directory processor."""


from smrt_importer.loader import SMRTLoader
from smrt_importer.db import insert_file


def process_file(path):
    """Load data from a single file and save to DB.
    
    path: path (string or Path object) to a CSV file.
    """

    loader = SMRTLoader()
    file = loader.load_file(path)
    insert_file(file)
