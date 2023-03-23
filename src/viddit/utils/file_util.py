import os

def make_dir_if_not_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def delete_content_of_dir(dir_name):
    if os.path.exists(dir_name):
        for file in os.listdir(dir_name):
            os.remove(os.path.join(dir_name, file))