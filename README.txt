How to Run:
    # please run code in windows

    please make sure all input path and output path are correctly
    1. building the index
        python run.py [trec-files-directory-path] [index-type] [output-dir]
        eg.:
        python run.py ./BigSample/ single ./indexes/my-indexes/
        python run.py ./BigSample/ stem ./indexes/my-indexes/
        python run.py ./BigSample/ phrase ./indexes/my-indexes/
        python run.py ./BigSample/ positional ./indexes/my-indexes/

        outputType:
        {indexType}Lex.json to store inverted index
        {indexType}Term.json to store termList


    ## make sure run 1. to build index first or below will raise exception
    2. static query processing

        python run.py ./indexes/my-indexes/ ./data/queryfile.txt bm25 stem ./results/results-bm2
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt dirichlet stem ./results/results-bm2
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt vsm stem ./results/results-bm2
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt bm25 single ./results/results-bm2
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt dirichlet single ./results/results-bm2
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt vsm single ./results/results-bm2


        in this project, the code will automatically run "treceval.exe qrel.txt results.txt" after scores are calculated
        to test the result for other dataset, change qrelfile, run below instead:
            -- treceval.exe [qrel.txt] [results.txt]

    3. dynamic query processing
        python run.py ./indexes/my-indexes/ ./data/queryfile.txt ./results/results-bm25

        in this project, the code will automatically run "treceval.exe qrel.txt results.txt" after scores are calculated
        to test the result for other dataset, change qrelfile, run below instead:
            -- treceval.exe [qrel.txt] [results.txt]

    use command (sh test.sh) to see all test case
    command output are stored in testcaseResult.txt