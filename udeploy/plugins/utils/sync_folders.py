from logger import logger

import os
import shutil


def sync(src, dst):

    categorization = _categorize_files(src, dst)

    logger.debug('New files: %s' % categorization['new_files'])
    logger.debug('Updated files: %s' % categorization['to_be_updated'])
    logger.debug('Deleted files: %s' % categorization['missing_files'])
    logger.debug('Unchanged files: %s' % categorization['without_changes'])

    _copy_file_list(src, dst,
                    categorization['new_files'] +
                    categorization['to_be_updated'])

    _delete_file_list(dst, categorization['missing_files'])
    _delete_empty_folders(dst)


def _get_file_list(folder):
    file_list = [
        os.path.join(dirpath.replace(folder, ''), f)
        for dirpath, dirnames, filenames in os.walk(folder)
        for f in filenames
    ]

    return file_list


def _categorize_files(src, dst):
    categorization = dict()

    src_file_list = _get_file_list(src)
    dst_file_list = _get_file_list(dst)

    categorization['new_files'] = [f for f in src_file_list
                                   if f not in dst_file_list]
    categorization['missing_files'] = [f for f in dst_file_list
                                       if f not in src_file_list]

    comparison_list = [f for f in src_file_list if f in dst_file_list]

    categorization['to_be_updated'] = [
        f for f in comparison_list
        if not _are_same_file(
            os.path.join(src, f),
            os.path.join(dst, f)
        )]

    categorization['without_changes'] = [f for f in comparison_list
                                         if f not in
                                         categorization['to_be_updated']]

    return categorization


def _are_same_file(file1, file2):
    stats1 = os.stat(file1)
    stats2 = os.stat(file2)

    return (stats1.st_size is stats2.st_size and
            stats1.st_mtime is stats2.st_mtime)


def _copy_file_list(src, dst, file_list):
    for f in file_list:
        src_abs_path = os.path.join(src, f)
        dst_abs_path = os.path.join(dst, f)

        os.makedirs(src_abs_path, exist_ok=True)
        os.makedirs(dst_abs_path, exist_ok=True)

        shutil.copy2(src_abs_path, dst_abs_path)


def _delete_file_list(parent_path, file_list):
    for f in file_list:
        os.remove(os.path.join(parent_path, f))


def _delete_empty_folders(root_path):
    subfolder_list = [
        dirpath
        for dirpath, dirnames, filenames in os.walk(root_path)
        if len(dirnames) is 0]

    for folder in subfolder_list:
        try:
            os.rmdir(folder)
        except OSError:
            pass
