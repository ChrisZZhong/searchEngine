python run.py ./BigSample/ single ./indexes/my-indexes/ &&
python run.py ./BigSample/ stem ./indexes/my-indexes/ &&
python run.py ./BigSample/ phrase ./indexes/my-indexes/ &&
python run.py ./BigSample/ positional ./indexes/my-indexes/ &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt bm25 stem ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt dirichlet stem ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt vsm stem ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt bm25 single ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt dirichlet single ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt vsm single ./results/results-bm2 &&
python run.py ./indexes/my-indexes/ ./data/queryfile.txt ./results/results-bm25