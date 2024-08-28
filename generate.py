import os
import sys
from pathlib import Path

# Configuration paths
DOCS_ROOT = Path('docs/source')
DOC_PATHS_FILE = 'doc_paths.txt'
CONF_FILE=DOCS_ROOT / 'conf.py'
import subprocess
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


def read_doc_paths(file_path):
    """Read top-level directories from doc_paths file."""
    with open(file_path, 'r') as file:
        paths = [line.strip() for line in file if line.strip()]
    return paths


def create_index_rst(directory, parent_rst=None):
    """Create index.rst for a given directory and update the parent .rst file."""
    module_name = directory.name
    print(module_name)
    print(directory)
    parent_dir="docs/source"/ directory
    parent_dir.mkdir(parents=True, exist_ok=True)
    index_rst_path ="docs/source"/ directory / "index.rst"
    print(index_rst_path)


    # Write the index.rst for this directory
    with open(index_rst_path, "w") as f:
        f.write(f"{module_name.capitalize()} Module\n")
        f.write("=" * (len(module_name) + 7) + "\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Contents:\n\n")

        # List all Python files in this directory
        for file in sorted(directory.glob("*.py")):
            if file.name == "__init__.py":
                continue
            module_doc = file.stem
            f.write(f"   {module_doc}\n")

        # List all subdirectories and create index.rst for them
        for sub_dir in sorted(directory.iterdir()):
            if sub_dir.is_dir():
                f.write(f"   {sub_dir.name}/index\n")
                create_index_rst(sub_dir, parent_rst=index_rst_path)

    # Append the current directory to the parent's .rst file
    if parent_rst:
        with open(parent_rst, "a") as f:
            f.write(f"   {directory.name}/index\n")


def create_module_rst(module_path):
    """Create a .rst file for a given module."""
    module_name = module_path.stem
    module_rst_path = DOCS_ROOT / module_path.relative_to(Path(module_path.anchor)).with_suffix('.rst')

    # Ensure the parent directory exists
    module_rst_path.parent.mkdir(parents=True, exist_ok=True)

    with open(module_rst_path, "w") as f:
        f.write(f"{module_name.capitalize()} Module\n")
        f.write("=" * (len(module_name) + 7) + "\n\n")
        f.write(f"This module contains functions and classes related to {module_name}.\n\n")

        # Add automodule directive
        module_path_str = str(module_path.relative_to(Path(module_path.anchor).parent)).replace('.py', '').replace('/','.').replace("\\",".")
        f.write(f".. automodule:: {module_path_str}\n")
        f.write("   :members:\n")
        f.write("   :undoc-members:\n")
        f.write("   :show-inheritance:\n")


def main():
    doc_paths = read_doc_paths(DOC_PATHS_FILE)

    # Clean the old build
    if DOCS_ROOT.exists():
        for item in DOCS_ROOT.iterdir():
            if item.is_dir():
                for sub_item in item.iterdir():
                    sub_item.unlink()
                item.rmdir()

    # Create initial index.rst
    print(DOCS_ROOT)
    with open(DOCS_ROOT / "index.rst", "w") as f:
        f.write("Project Documentation\n")
        f.write("====================\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Contents:\n\n")

    for top_level_dir in doc_paths:
        top_level_path = Path(top_level_dir)
        create_index_rst(top_level_path)

    # Add necessary `index.rst` references to the root index.rst
    with open(DOCS_ROOT / "index.rst", "a") as f:
        for top_level_dir in doc_paths:
            f.write(f"   {Path(top_level_dir).name}/index\n")

    # Create .rst files for all modules
    for root_dir in doc_paths:
        for dirpath, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    module_path = Path(dirpath) / file
                    create_module_rst(module_path)

    # Build documentation
    os.system('make html')


if __name__ == "__main__":
    run_sphinx_quickstart()
    main()
