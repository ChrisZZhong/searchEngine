import os
from indexing import buildIndexByType
from pathlib import Path


def run():
    """
    entrance of the whole program
    :return:
    """
    inputFilePaths = []
    inputPath = "./BigSample"

    for filename in os.listdir(inputPath):
        inputFilePaths.append(f"{inputPath}/{filename}")

    Types = ["term", "phrases", "stem", "position"]  # "phrases" "term"
    # Types = ["phrases", "stem", "position"]  # "phrases" "term"
    # tempFile store temp file
    if not Path("./tempFile").exists():
        Path("./tempFile").mkdir()
    # index store the final invert index map
    if not Path("./index").exists():
        Path("./index").mkdir()

    for Type in Types:
        buildIndexByType(inputFilePaths, Type)

run()




