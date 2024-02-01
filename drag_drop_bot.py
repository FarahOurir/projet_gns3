import os
import shutil

def move_files(source_folder, destination_pathway):
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            for root_dest, dirs_dest, files_dest in os.walk(destination_pathway):
                destination_file_path = os.path.join(root_dest,"configs", file_name)

                # Check if the file already exists in the destination folder
                if os.path.exists(destination_file_path):
                    print("exists")
                    # Replace the file in the destination folder
                    shutil.move(os.path.join(source_folder, file_name), destination_file_path)
                    print(f"Replaced '{file_name}' in the destination folder.")
                    break  # Stop searching for the file in other subfolders
        

# Replace these paths with your actual folder paths
source_folder_path = "/Users/farah/OneDrive/Bureau/projet_gns3/configs"
destination_pathway_path = "/Users/farah/GNS3/projects/gns_test/project-files/dynamips"

move_files(source_folder_path, destination_pathway_path)
