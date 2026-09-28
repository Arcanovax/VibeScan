import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from jev import Jev, Question
import argparse


def get_api_key():
    load_dotenv()
    key = os.getenv("KEY")
    if key is None:
        raise ValueError("No key")
    return key


def find_files_paths(path, allowed_ext):
    files_paths = []
    for ext in allowed_ext:
        files_paths += [
            file for file in path.rglob(f"*{ext}")
            if not any(part.startswith(".") for part in file.parts)
        ]
    return files_paths

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--code",
        default=".",
    )
    args = parser.parse_args()
    
    ext = [".py", ".md", ".txt"]
    
    jev = Jev(get_api_key())
    
    
    
    
    
    files_paths = find_files_paths(Path(args.code), ext)

    for path in files_paths:
        with open(path, "r", encoding="utf-8") as f:
            file = f.read()
        if file is None:
            return
        answers = jev.scan(file)
        print(path)
        for name, content in answers.items():
            print(f"{name}: {content.answer} ({content.confidence*100}%)")
        print("\n")
        
    

if __name__ == "__main__":
    main()
