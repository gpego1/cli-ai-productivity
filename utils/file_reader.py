def file_reader(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        return lines