"""SMRT Importer directory processor."""


from smrt_importer.loader import SMRTLoader
from smrt_importer.db import insert_file


def process_file(path):
    loader = SMRTLoader()
    file = loader.load_file(path)
    insert_file(file)
