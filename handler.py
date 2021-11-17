import sys
import os
import hashlib


def get_file_paths():
    root_directory = sys.argv[1]  # specify root directory
    # create a list of files in specified directory
    file_paths = []
    for root, dirs, files in os.walk(root_directory):
        for name in files:
            file_paths.append(root + '/' + name)
    return file_paths


def get_file_extension(file_paths):
    # read user input that specifies the file format. Empty input should match any file format

    file_format = input('Enter file format: ')
    if file_format == '':
        format_match = file_paths
    else:
        format_match = [file for file in file_paths if os.path.splitext(file)[1] == '.' + file_format.lower()]
    return format_match


def get_dict_of_duplicates(format_match):
    # create dictionary with potentially duplicated files and their sizes
    format_match_size = [{os.path.getsize(file): [file]} for file in format_match]
    res = {}
    for dictionary in format_match_size:
        for size, file in dictionary.items():
            if size not in res:
                res[size] = file
            else:
                res[size] += (dictionary[size])
    duplicated_files = {key: value for key, value in res.items() if len(value) > 1}
    return duplicated_files


def apply_sorting_option(duplicated_files):
    # define user input for sorting order and print sorted dictionary with potentially duplicated files
    print('''Size sorting options:
    1. Descending
    2. Ascending''')
    sorting_option = str(input('Enter a sorting option: '))
    while sorting_option not in ['1', '2']:
        print('Wrong option')
        sorting_option = input('Enter a sorting option: ')
    sorted_duplicated_files = sorted(duplicated_files.items(), reverse=True if sorting_option == '1' else False)
    for size, file_list in sorted_duplicated_files:
        print(str(size) + ' bytes')
        for file in file_list:
            print(file)
    return sorting_option, sorted_duplicated_files


def md5(fname):
    #  get hash key of the file
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def print_info_duplicate_hash(hash_check):

    for size, hashkeys_dict in hash_check.items():
        print('\n' + str(size) + ' bytes')
        for hashkey, files in hashkeys_dict.items():
            print('Hash: ' + hashkey)
            for file in files:
                print(file)


def apply_duplicate_check_option(sorted_duplicated_files):
    # Ask for duplicates check
    dupl_check_option = str(input('Check for duplicates? '))
    while dupl_check_option.lower() not in ['yes', 'no']:
        print('Wrong option')
        dupl_check_option = input('Check for duplicates? yes or no?')
    if dupl_check_option.lower() == 'no':
        sys.exit()
    else:

        #  create nested dictionary
        hash_check = {}
        for size, values in sorted_duplicated_files:
            hash_check[size] = {}
            for file in values:
                if md5(file) not in hash_check[size]:
                    hash_check[size][md5(file)] = [file]
                else:
                    hash_check[size][md5(file)] += [file]

        hash_check = {key: {hashkey: file_list for hashkey, file_list in value.items() if len(file_list) > 1}
                      for key, value in hash_check.items()}
        hash_check = {key: value for key, value in hash_check.items() if len(value) > 0}

        #  add files numeration
        count = 0
        hash_check_numerated = {}
        for size, value in hash_check.items():
            hash_check_numerated[size] = {}
            for hashkey, files in value.items():
                for file in files:
                    count += 1
                    if hashkey not in hash_check_numerated[size]:
                        hash_check_numerated[size][hashkey] = [str(count) + '. ' + file]
                    else:
                        hash_check_numerated[size][hashkey] += [str(count) + '. ' + file]
        print_info_duplicate_hash(hash_check_numerated)
        return hash_check_numerated, count


def delete_duplicate_files(hash_check_numerated, file_count):
    #     ask whether delete the files
    delete_option = str(input('Delete files? '))
    while delete_option.lower() not in ['yes', 'no']:
        print('Wrong option')
        delete_option = input('Delete files? yes or no?')

    if delete_option.lower() == 'no':
        sys.exit()

    else:
        file_count_range = list(range(1, file_count + 1))
        files_to_delete = input('Enter file numbers to delete: ')

        while not files_to_delete.strip() or files_to_delete == '':
            print('Wrong format')
            files_to_delete = input('Enter file numbers to delete: ')
        try:
            files_to_delete = [int(number) for number in files_to_delete.strip().split(' ')]
        except ValueError:
            files_to_delete = [number for number in files_to_delete.strip().split(' ')]
        check = all(item in file_count_range for item in files_to_delete)

        while not check:
            print('Wrong format')
            files_to_delete = input('Input should contain only file numbers separated by spaces. '
                                    'Enter file numbers to delete: ')
            files_to_delete = [int(number) for number in files_to_delete.strip().split(' ')]
            check = all(item in file_count_range for item in files_to_delete)

#        pick the files for deletion
        picked_files = []
        for size, value in hash_check_numerated.items():
            for hashkey, files in value.items():
                for file in files:
                    if int(file.split('. ')[0]) in files_to_delete:
                        picked_files.append({size: file.split('. ')})
                        os.remove(file.split('. ')[1])

        freed_up_space = sum([list(dictionary.keys())[0] for dictionary in picked_files])
        print(f'Total freed up space: {freed_up_space} bytes')


def check_and_handle_duplicates():
    try:
        file_paths = get_file_paths()
        format_match = get_file_extension(file_paths)
        duplicated_files = get_dict_of_duplicates(format_match)
        sorting_option, sorted_duplicated_files = apply_sorting_option(duplicated_files)
        hash_check_numerated, file_count = apply_duplicate_check_option(sorted_duplicated_files)
        delete_duplicate_files(hash_check_numerated, file_count)

    except IndexError:
        print('Directory is not specified ')


check_and_handle_duplicates()










