import os
from pathlib import Path

project_name = "article_text_analysis"


list_of_files = [

    f"{project_name}/__init__.py",
    f"{project_name}/src/__init__.py",
    f"{project_name}/src/extractor.py",
    f"{project_name}/src/text_cleaner.py",
    f"{project_name}/src/analyzer.py",
    f"{project_name}/src/pipeline.py",
    f"{project_name}/exceptions/__init__.py",
    f"{project_name}/exceptions/exception.py",
    f"{project_name}/logger/__init__.py",
    f"{project_name}/logger/logging.py",
    "data/raw_data/",
    "data/raw_articles/dictionaries/",
    "data/raw_articles/StopWords/",
    "output/",
    "logs/",
    "main.py",
    "setup.py"
    

]

for item in list_of_files:
    path = Path(item)
    
    # 1. If the item ends with a slash, treat it explicitly as a Directory
    if item.endswith("/") or item.endswith("\\"):
        os.makedirs(path, exist_ok=True)
        print(f"Directory created/exists at: {path}")
        
    # 2. Otherwise, treat it as a File
    else:
        filedir, filename = os.path.split(path)

        if filedir != "":
            os.makedirs(filedir, exist_ok=True)

        if (not os.path.exists(path)) or (os.path.getsize(path) == 0):
            with open(path, "w") as f:
                pass
            print(f"File created at: {path}")
        else:
            print(f"File already exists at: {path}")