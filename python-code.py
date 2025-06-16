import os

def list_and_save_python_files(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as out:
        for foldername, subfolders, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    file_path = os.path.join(foldername, filename)
                    out.write(f"\n{'='*80}\n")
                    out.write(f"File: {filename}\nPath: {file_path}\n")
                    out.write(f"{'='*80}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as py_file:
                            code = py_file.read()
                            out.write(code + "\n")
                    except Exception as e:
                        out.write(f"[Error reading file: {e}]\n")

# Update this to the directory you want to scan
ROOT_DIR = r'F:\prj\booking_system\users'
OUTPUT_FILE = 'users.txt'

list_and_save_python_files(ROOT_DIR, OUTPUT_FILE)
print(f"Python code exported to: {OUTPUT_FILE}")
