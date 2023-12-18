import os
import sys  
import re
import shutil
from pathlib import Path 


documents = ".doc .docx .txt .pdf .xlsx .pptx".split()
images = ".jpeg .png .jpg .svg".split()
audio = ".mp3 .ogg .wav .amr".split()
video = ".avi .mp4 .mov .mkv".split()
archives = ".zip .gz .tar".split()

dict_suffixes = {
    'documents' : documents,
    'images' : images,
    'audio' : audio,
    'video' : video,
    'archives' : archives,
}

dict_suffixes_reverse = {}
all_files = []
known_extensions = set()
unknown_extensions = set()

for categ, suffs in dict_suffixes.items():
    dict_suffixes_reverse.update(dict.fromkeys(suffs, categ))    

def transliterate_cyrillic_to_latin(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    result = ''
    for char in text:
        is_upper = char.isupper()
        char_lower = char.lower()

        if char_lower in translit_dict:
            result += translit_dict[char_lower].capitalize() if is_upper else translit_dict[char_lower]
        else:
            result += char

    return result

def normalize(name):
    name_translit = transliterate_cyrillic_to_latin(name)

    normalized_name = re.sub(r'[^a-zA-Z0-9]+', '_', name_translit)

    return normalized_name

def write_list_to_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}\n")

def unpack(archive_path: Path, path_to_unpack): 
    archive_name = os.path.splitext(os.path.basename(archive_path))[0]
    path_to_unpack = os.path.join(os.path.dirname(archive_path), archive_name)
    try:
        shutil.unpack_archive(archive_path, path_to_unpack)
        archive_path.unlink()
    except Exception as e:
        archive_path.unlink()

def move_file(root_path: Path, path_file: Path):
    name = normalize(path_file.stem)
    suff = path_file.suffix.lower() #
    
    category = dict_suffixes_reverse.get(suff, 'others')

    new_path_dir = root_path / category

    if not new_path_dir.exists():
        new_path_dir.mkdir()

    
    original_suffix = path_file.suffix    
    new_path_file = new_path_dir / (name + original_suffix)
    path_file.replace(new_path_file)

    if category == 'archives':
        unpack(new_path_file, new_path_dir)

def sort_folder(root_path: Path, path: Path):      

    for item in path.iterdir():
        if item.is_file():
            all_files.append(str(item.name))
            _, extension = os.path.splitext(item.name)
            extension_lower = extension.lower()

            if extension_lower in dict_suffixes_reverse:
                known_extensions.add(extension_lower)
            else:
                unknown_extensions.add(extension)

            if extension in dict_suffixes_reverse:
                known_extensions.add(extension)
            else:
                unknown_extensions.add(extension)

            move_file(root_path, item)

        if item.is_dir() and not item.name in dict_suffixes.keys():
            sort_folder(root_path, item)
            item.rmdir()
            

    write_list_to_file(root_path / 'all_files.txt', all_files)
    write_list_to_file(root_path / 'known_extensions.txt', known_extensions)
    write_list_to_file(root_path / 'unknown_extensions.txt', unknown_extensions)

def main():  
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])    
    else:
        path = Path("sort-goit")
    sort_folder(path, path)

if __name__ == '__main__':
    main()
