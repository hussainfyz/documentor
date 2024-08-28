import os
import subprocess
from pathlib import Path

# Define the Sphinx docs directory
DOCS_ROOT = Path("docs/source")  # Adjust this path if necessary
CONF_FILE = DOCS_ROOT / "conf.py"  # The path to the conf.py file
DOC_PATHS_CONFIG = "doc_paths.txt"  # Path to the config file with the paths to document


def run_sphinx_quickstart():
    """
    Runs sphinx-quickstart if it hasn't been run already.
    """
    if not CONF_FILE.exists():
        print("Sphinx quickstart has not been run. Running sphinx-quickstart...")
        subprocess.run(["sphinx-quickstart", "docs"], check=True)
        print("Sphinx quickstart completed.")
    else:
        print("Sphinx quickstart has already been run. Continuing...")

#os.path.absp
def update_conf_py1():
    """
    Updates the conf.py file to include the necessary extensions and paths.
    """
    extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
        "sphinx.ext.todo"
    ]

    paths_to_add = []

    # Read paths from config file
    with open(DOC_PATHS_CONFIG, "r") as f:
        paths_to_add = [line.strip() for line in f if line.strip()]

    # Add extensions and paths to conf.py
    with open(CONF_FILE, "r+") as f:
        conf_content = f.read()

        # Ensure all necessary extensions are included
        if "extensions = [" not in conf_content:
            conf_content = conf_content.replace(
                "# extensions = []",
                f"extensions = {extensions}\n"
            )

        # Add paths to sys.path
        sys_path_lines = ""
        for path in paths_to_add:
            sys_path_lines += f"sys.path.insert(0, os.path.abspath('{path}'))\n"

        # Replace existing sys.path insertions or add new ones
        if "sys.path.insert(0, os.path.abspath('.'))" in conf_content:
            conf_content = conf_content.replace(
                "sys.path.insert(0, os.path.abspath('.'))",
                sys_path_lines
            )
        else:
            # Add sys.path insertions if not present
            conf_content = conf_content.replace(
                "import os\nimport sys\n\n",
                "import os\nimport sys\n\n" + sys_path_lines
            )

        # Write back the updated conf.py content
        f.seek(0)
        f.write(conf_content)
        f.truncate()


def create_index_rst(directory, parent_rst=None):
    """
    Creates an index.rst for a given directory and appends the directory to the parent .rst file.
    """
    module_name = directory.name
    index_rst_path = directory / "index.rst"

    # Write the index.rst for this directory
    with open(index_rst_path, "w") as f:
        f.write(f"{module_name.capitalize()} Module\n")
        f.write("=" * (len(module_name) + 7) + "\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Contents:\n\n")

        # List all Python files in this directory
        for file in directory.glob("*.py"):
            if file.name == "__init__.py":
                continue
            module_doc = file.stem
            f.write(f"   {module_doc}\n")

        # List all subdirectories
        for sub_dir in sorted(directory.iterdir()):
            if sub_dir.is_dir():
                f.write(f"   {sub_dir.name}/index\n")
                create_index_rst(sub_dir, parent_rst)

    # Append the current directory to the parent's .rst file
    if parent_rst:
        with open(parent_rst, "a") as f:
            f.write(f"   {directory.name}/index\n")


def create_module_rst(module_path):
    """
    Creates a .rst file for a given module.
    """
    module_name = module_path.stem
    module_rst_path = DOCS_ROOT / module_path.relative_to(Path(module_path.anchor))

    # Ensure the parent directory exists
    module_rst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp1=str(module_rst_path)
    module_rst_path=tmp1.replace('.py','.rst')
    print(module_rst_path, "module_rst_path")
    with open(module_rst_path, "w") as f:
        f.write(f"{module_name.capitalize()} Module\n")
        f.write("=" * (len(module_name) + 7) + "\n\n")
        f.write(f"This module contains functions and classes related to {module_name}.\n\n")

        # Add automodule directive
        f.write(".. automodule:: myutils." + module_name + "\n")
        f.write("   :members:\n")
        f.write("   :undoc-members:\n")
        f.write("   :show-inheritance:\n")


def generate_sphinx_docs():
    # Ensure sphinx-quickstart has been run
    run_sphinx_quickstart()

    # Update the conf.py file
    #update_conf_py()

    # Create the initial index.rst for the main project
    root_index_rst = DOCS_ROOT / "index.rst"

    with open(root_index_rst, "w") as f:
        f.write("Welcome to logger's documentation!\n")
        f.write("===================================\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Modules:\n\n")

        # Read paths from config file
        with open(DOC_PATHS_CONFIG, "r") as config_file:
            paths = [line.strip() for line in config_file if line.strip()]

        # Add specified files and directories to the index
        for path in paths:
            path_obj = Path(path)
            # Create the necessary nested directory structure inside docs/source
            nested_dir = DOCS_ROOT / path_obj.relative_to(Path(path).anchor)
            nested_dir.mkdir(parents=True, exist_ok=True)

            if path_obj.is_dir():
                f.write(f"   {path_obj.name}/index\n")
                create_index_rst(nested_dir, root_index_rst)
            elif path_obj.is_file() and path_obj.suffix == '.py':
                create_module_rst(path_obj)
                f.write(f"   {path_obj.stem}\n")

    # Run sphinx-apidoc to generate .rst files for specified paths
    for path in paths:
        path_obj = Path(path)
        output_dir = DOCS_ROOT / path_obj.relative_to(Path(path).anchor)
        subprocess.run([
            "sphinx-apidoc", "-o", str(output_dir), str(path),
            "--separate", "--module-first"
        ])

    # Build HTML documentation
    #subprocess.run(["make", "html"], cwd=DOCS_ROOT.parent)
    os.listdir()

if __name__ == "__main__":
    generate_sphinx_docs()
