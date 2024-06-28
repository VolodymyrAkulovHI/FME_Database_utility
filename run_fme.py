import subprocess
import os

def run_fme_environment(mode='file'):
    # Define the path to your FME executable, workspace, and the input/output connections
    fme_executable = r"C:\Program Files\FME\fme.exe"  # Adjust the path to your FME installation
    workspace_path = r"1 GIS to HIS Vertex work 2.fmw"

    # Define the database connection parameters (these should match the names defined in FME Workbench)
    db_connection_1 = "main"
    db_connection_2 = "main"

    # Define the output geodatabase file paths and feature class names
    
    output_gdb_1 = r"Vertex_Points.gpkg"
    output_gdb_2 = r"Vertex_Lines.gpkg"

    if os.path.exists(output_gdb_1):
        os.remove(output_gdb_1)

    if os.path.exists(output_gdb_2):
        os.remove(output_gdb_2)

    # Construct the FME command with explicit parameter names as per FME Workbench
    if mode == 'file':
        command = [
            fme_executable,
            workspace_path,
            "--DBConnection1", db_connection_1,
            "--DBConnection2", db_connection_2,
            "--DestDataset_OGCGEOPACKAGE_7", output_gdb_1,
            "--DestDataset_OGCGEOPACKAGE_6", output_gdb_2,
        ]
    elif mode == 'server':
        command = [
            fme_executable,
            workspace_path,
            "--DBConnection1", db_connection_1,
            "--DBConnection2", db_connection_2,
            "--SERVER_FLAG", "value"  # Adjust the server-specific flags accordingly
        ]
    else:
        raise ValueError("Invalid mode specified. Use 'file' or 'server'.")

    # Print the command to verify parameters
    print("Running command:", " ".join(command))

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the result and print the log
    if result.returncode == 0:
        print("Workspace ran successfully!")
        print(result.stdout)
    else:
        print("Workspace failed with status code:", result.returncode)
        print(result.stderr)

    # Save the FME log to a file for detailed inspection
    log_file_path = r"fme_log.txt"
    with open(log_file_path, 'w') as log_file:
        log_file.write(result.stdout)
        log_file.write(result.stderr)

    print(f"FME log saved to: {log_file_path}")
