import json

import preprocess
import tempfile
import os
import time
import statistics
from pathlib import Path

menoryConstraint = 0
termDict = {}
lexicon = {}
count = 0


def getAllTokens(folderPath, inputFiles, outputPath, indexType, memory, pro1Res1):
    """This method iterates through the files in the folder, sends them
    to the document iterator, and then handles the final temp writing and merging."""

    startTime = time.time()

    global menoryConstraint
    menoryConstraint = memory
    global lexicon
    lexicon = {}
    global termDict
    termDict = {}
    global count
    count = 0

    tempFiles = []

    for filename in inputFiles:
        tempFiles = traverseFiles(tempFiles, folderPath, filename, indexType)

    endTime = time.time()

    numT, maxT, minT, meanT, medianT = calculateTermList()
    pro1Res1[indexType] = {'lexicon': numT, 'size': 0, 'max_df': maxT, 'min_df': minT, 'mean_df': meanT,
                           'median_df': medianT, 'time': (endTime - startTime)}

    writeFile(outputPath, indexType)
    return termDict, lexicon, pro1Res1


def traverseFiles(tempFiles, folder, singleFile, indexType):
    """This method reads in a file and stores each document as an item in a list (collection).
    Then it sends each document within the collection to be added to the index."""

    doc_collection = preprocess.readCollection(folder + singleFile)
    for document in doc_collection:
        docID = preprocess.getDocID(document)
        if indexType == 'single':
            tempFiles = buildSingleIndex(tempFiles, document, docID)
        elif indexType == 'phrase':
            tempFiles = buildPhraseIndex(tempFiles, document, docID)
        elif indexType == 'stem':
            tempFiles = buildStemIndex(tempFiles, document, docID)
        elif indexType == 'positional':
            tempFiles = buildPositionalIndex(tempFiles, document, docID)
    return tempFiles


def buildSingleIndex(tempFiles, document, docID):
    """This method controls the processing of a document and the adding of the terms
    to the single index."""
    terms = preprocess.processing(document, 'single')
    appendToIndex(terms, docID)
    tempFiles = checkMemConstraint(tempFiles)
    return tempFiles


def buildStemIndex(tempFiles, document, docID):
    """This method controls the processing of a document and the adding
    of the terms to the stem index."""

    stems = preprocess.processing(document, 'stem')
    appendToIndex(stems, docID)
    tempFiles = checkMemConstraint(tempFiles)
    return tempFiles


def buildPhraseIndex(tempFiles, document, docID):
    """This method controls the processing of a document and the adding
    of the terms to the phrase index."""

    phrases = preprocess.processing(document, 'phrase')
    appendToIndex(phrases, docID)
    tempFiles = checkMemConstraint(tempFiles)
    return tempFiles


def buildPositionalIndex(tempFiles, document, docID):
    """This method controls the processing of a document and the adding
    of the terms to the phrase index."""

    tokens = preprocess.processing(document, 'positional')
    appendToIndexPosition(tokens, docID)

    global count
    global menoryConstraint

    if count > menoryConstraint and menoryConstraint != 0:
        tempFiles = writeTempPosition(tempFiles)
        count = 0
    return tempFiles


def checkMemConstraint(tempFiles):
    """This method checks if the memory has reached the constraint, if it has
    then the method calls writeTemp to write to disk memory."""

    global count
    global menoryConstraint

    if count > menoryConstraint and menoryConstraint != 0:
        tempFiles = writeTemp(tempFiles)
        count = 0
    return tempFiles


def appendToIndex(terms, docID):
    """"This method iterates through the terms and sends each
    key to be added to the index."""

    global count
    for term in terms:
        addToIndex(term, docID)
        count += 1


def appendToIndexPosition(terms, docID):
    """"This method iterates through the terms and sends each
    key to be added to the POSITIONAL index."""

    global lexicon
    global termDict
    global count
    for idx, token in enumerate(terms):
        addToIndexPosition(token, idx, docID)
        count += 1


def addToIndex(term, docID):
    """This method checks if the term is already in the term list
    and if the docID is already in the posting list of that term. 
    Then it either updates the df, the tf, and/or adds new document.
    Increments the count when a new document added to the posting list."""

    global lexicon
    global count
    global termDict
    if term in lexicon and docID in lexicon[term]:
        # Second+ time term seen in document, add one to tf
        lexicon[term][docID] += 1
    elif term in lexicon and docID not in lexicon[term]:
        # term seen in another document, add to posting list and update df
        lexicon[term][docID] = 1
        termDict[term] += 1
    elif term not in lexicon and term in termDict:
        # add term to lexicon and update df
        lexicon[term] = {docID: 1}
        termDict[term] += 1
    elif term not in lexicon and term not in termDict:
        # add term to lexicon and to the term list
        lexicon[term] = {docID: 1}
        termDict[term] = 1


def addToIndexPosition(term, position, docID):
    """This method does the same as addToIndex except for the
    POSITIONAL index. In the posting list instead of storing tf, the 
    document maps to a list of the positions. The tf could be found
    by finding the length of the list. """

    global lexicon
    global count
    global termDict
    if term in lexicon and docID in lexicon[term]:
        lexicon[term][docID].append(position)
    elif term in lexicon and docID not in lexicon[term]:
        lexicon[term][docID] = [position]
        termDict[term] += 1
    elif term not in lexicon and term in termDict:
        lexicon[term] = {docID: [position]}
        termDict[term] += 1
    elif term not in lexicon and term not in termDict:
        lexicon[term] = {docID: [position]}
        termDict[term] = 1


def writeTemp(tempFiles):
    """This file writes the lexicon to a temp file and stores
    the name of the temp file in a list. It then deletes the
    contents of the lexicon."""

    global lexicon
    global count
    os_temp, temp_file_name = tempfile.mkstemp()
    for term in sorted(lexicon.keys()):
        os.write(os_temp, '<' + term + '> ')
        for docID in lexicon[term]:
            os.write(os_temp, docID + ',' + str(lexicon[term][docID]) + ' | ')
        os.write(os_temp, '\n')
    lexicon = {}
    count = 0
    if tempFiles:
        tempFiles.append(str(temp_file_name))
    else:
        tempFiles = [str(temp_file_name)]
    os.close(os_temp)
    return tempFiles


def writeTempPosition(tempFiles):
    """This file writes the POSITIONAL lexicon to a temp file and stores
    the name of the temp file in a list. It then deletes the
    contents of the lexicon."""

    global lexicon
    global count
    os_temp, temp_file_name = tempfile.mkstemp()
    for term in sorted(lexicon.keys()):
        os.write(os_temp, '<' + term + '> ')
        for docID in lexicon[term]:
            os.write(os_temp, docID)
            os.write(os_temp, str(lexicon[term][docID]))
            os.write(os_temp, ' | ')
        os.write(os_temp, '\n')
    lexicon = {}
    count = 0
    if tempFiles:
        tempFiles.append(str(temp_file_name))
    else:
        tempFiles = [str(temp_file_name)]
    os.close(os_temp)
    return tempFiles


def writeFile(outPath, indexType):
    """This method handles the case in which no temp files
    were created and the entire lexicon/pl is stored in memory
    and now is written to the final file."""

    global lexicon
    global count
    global termDict
    outputPath = f"{outPath}/{indexType}"

    if not Path(outPath).exists():
        os.makedirs(outPath)

    with open(f"{outputPath}Lex.json", "w", encoding="UTF-8") as f:
        te = {}
        for term in sorted(lexicon.keys()):
            te[term] = lexicon[term]
        f.write(json.dumps(te, indent=4))
    f.close()

    with open(f"{outputPath}Term.json", "w", encoding="UTF-8") as f:
        te = {}
        for term in sorted(termDict.keys()):
            te[term] = termDict[term]
        f.write(json.dumps(te, indent=4))
    f.close()

    termDict = {}
    lexicon = {}
    count = 0


def writeFilePosition(outPath):
    """This method handles the case in which no temp files
    were created and the entire lexicon/pl is stored in memory
    and now is written to the final file for POSITIONAL."""

    global lexicon
    global count
    with open(outPath, 'w') as outFile:
        for term in sorted(lexicon.keys()):
            outFile.write('<' + term + '> ')
            for docID in lexicon[term]:
                outFile.write(docID + ' ')
                outFile.write(str(lexicon[term][docID]))
                outFile.write(' | ')
            outFile.write('\n')
        lexicon = {}
        count = 0


def calculateTermList():
    num_of_terms = len(termDict)
    max_df = max(termDict.values())
    min_df = min(termDict.values())
    mean_df = statistics.mean(termDict.values())
    median_df = statistics.median(termDict.values())

    return num_of_terms, max_df, min_df, mean_df, median_df


def writeTermList(outPath):
    """This method writes the term list containing all the
    terms and the document frequency to the final file. """

    global termDict
    with open(outPath, 'w') as outFile:
        for term in sorted(termDict):
            outFile.write('<' + term + '> ' + str(termDict[term]) + '\n')
        termDict = {}


def decoratedFile(t_file, key):
    """Helpder for merge."""

    for line in t_file:
        key_and_doc = key(line)
        yield (key_and_doc[0], key_and_doc[1])


def keyFunc(line):
    """Helper for merge."""
    line = line.replace('\n', '')
    return line.split('>', 2)


def grouper(sequence, size):
    """Taken from http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
    Returns a list broken in to items as specified by size. Using in this program to step by step merge."""
    return (sequence[pos:pos + size] for pos in range(0, len(sequence), size))


def timeResults(startTime, mergeTime, endTime, numT, maxT, minT, meanT, medianT, indexType):
    """This method prints the execution time results to the user."""

    if indexType == 'single':
        print("\nSINGLE INDEX")
    elif indexType == 'stem':
        print("\nSTEM INDEX")
    elif indexType == 'phrase':
        print("\nPHRASE INDEX")
    elif indexType == 'positional':
        print("\nPOSITIONAL INDEX")

    print("Execution Time Total: " + str(endTime - startTime))
    if mergeTime != 0:
        print("Time to Temp File Creation: " + str(mergeTime - startTime))
        print("Time to Merge Temp Files: " + str(endTime - mergeTime))

    print("Terms in lexicon: " + str(numT))
    print("Max df: " + str(maxT))
    print("Min df: " + str(minT))
    print("Mean df: " + str(meanT))
    print("Median df: " + str(medianT))
