import os
import shutil

print("start cleaning up workspace...")

# set up directory paths
base_dir = os.getcwd()
data_dir = os.path.join(base_dir, 'data')
archive_dir = os.path.join(base_dir, 'archive_scripts')

# 1. create archive folder
os.makedirs(archive_dir, exist_ok=True)

# 2. list of old scripts that need to be archived
old_scripts = [
    'data_pipeline.py',
    'logistics_check.py',
    'compliance_check.py',
    'routing_engine.py'
]

# 3. move files
for script in old_scripts:
    src_path = os.path.join(data_dir, script)
    dest_path = os.path.join(archive_dir, script)
    
    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)
        print(f"moved: {script} -> archive_scripts/")
    else:
        print(f"skip: {script} not found in data/ (maybe already moved)")

print("workspace cleanup complete. check your left panel!")