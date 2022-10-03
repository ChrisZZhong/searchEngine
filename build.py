import os
from indexing import buildIndexByType
from pathlib import Path
import sys


def run(argv):
    """
    entrance of the whole program
    :return:
    """
    inputFilePaths = []
    # inputPath = "./BigSample"
    inputPath = argv[1]
    inputArgs = argv[2:]
    Types = [inputArgs[i:i + 2] for i in range(0, len(inputArgs), 2)]

    for filename in os.listdir(inputPath):
        inputFilePaths.append(f"{inputPath}/{filename}")

    mapping = {"single": "term",
               "stem": "stem",
               "phrase": "phrases",
               "positional": "position"}
    # Types = ["term", "phrases", "stem", "position"]  # "phrases" "term"
    # Types = ["phrases"]  # "phrases" "term"
    # tempFile store temp file
    if not Path("./tempFile").exists():
        Path("./tempFile").mkdir()

    for Type in Types:
        if len(Type) != 2:
            print("invalid input")
        else:
            if not os.path.exists(Type[1]):
                os.makedirs(Type[1])
            print(f"now building index {mapping[Type[0]]}")
            buildIndexByType(inputFilePaths, mapping[Type[0]], Type[1])


if __name__ == "__main__":
    run(sys.argv)
