import os
import shutil
from datetime import datetime


def get_latest_folders_with_file(base_dir, filename="samples-rgb.mp4", n=4):
    matching_folders = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            try:
                dt = datetime.strptime(folder, "%Y%m%d_%H%M%S")
            except ValueError:
                continue

            target_file = os.path.join(folder_path, filename)
            if os.path.isfile(target_file):
                matching_folders.append((dt, folder))

    if not matching_folders:
        print("No matching folders found.")
        return []

    matching_folders.sort(reverse=True)
    latest_n = matching_folders[:n]
    latest_n.sort()

    return [os.path.join(base_dir, folder) for _, folder in latest_n]


def clear_user_workspace(user_id):
    base_dirs = [
        'static/uploads',
        'static/fragments',
        'static/generated_videos',
        'static/final_output'
    ]

    for base_dir in base_dirs:
        user_folder = os.path.join(base_dir, f'user_{user_id}')
        if os.path.isdir(user_folder):
            try:
                shutil.rmtree(user_folder)
                print(f"Successfully deleted folder: {user_folder}")
            except Exception as e:
                print(f"Error deleting folder {user_folder}: {e}")
        else:
            print(f"Folder not found, skipping: {user_folder}")
