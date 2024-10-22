import fuddly.cli.argparse_wrapper as argparse
import os
from pathlib import Path

from fuddly.framework import global_resources as gr

conf = {}


# For DMs
# <args.name>/
# ├── dm.py
# ├── __init__.py
# ├── samples (?)
# │   └── sample_file.txt (?)
# └── strategy.py

conf["dm"] = {
    "dm": {
        "name": "dm.py",
        "interpolate": ["name"],
    },
    "strategy": {
        "name": "strategy.py",
    },
    "init": {
        "name": "__init__.py",
    },
}


# TODO project strucut will change so I won't bother doing it now
conf["project"] = {}

conf["module"] = {
    "config": {
        "name": "pyproject.toml",
        "interpolate": ["name", "target", "module_name"], 
    },
    "readme": {
        "name": "README.md",
        "interpolate": ["name", "target"],
    },
}

# TODO the way module name is defined multiple times is redundant, a better way to handle it would
# be nice

def start(args: argparse.Namespace):
    if args.dest is not None:
        target_dir=Path(args.dest).absolute()
    else:
        if args.pyproject:
            target_dir=Path(".").absolute()
        else:
            target_dir=Path(gr.user_data_models_folder).absolute()

    if target_dir.joinpath(args.name).exists():
        print(f"A {args.name} directory already exists in {target_dir}")
        return 1

    # It's nice to use dm on the cmdline, but we want it to be called data-model in the code
    args.target = "data-model" if args.target == "dm" else args.target

    module_name=args.name
    if args.pyproject:
        module_name = f"fuddly_module_{args.name}"
        # Overridding the name to reduce the risk of conflicting with an other package
        print(f"Initializing a new module '{args.name}' in {target_dir}")
        target_dir = target_dir.joinpath(args.name)
        target_dir.mkdir(parents=True)
        _create_conf(args, target_dir, conf["module"])
        # If we are in a module, the sources shoudl go in src/{name}/
        target_dir = target_dir / "src"

    target_dir = target_dir.joinpath(module_name)
    target_dir.mkdir(parents=True)

    match args.target:
        case "data-model":
            args.target="data-model"
            print(f"Creating new data-model {module_name}")
            _create_conf(args, target_dir, conf["dm"])
        case "project":
            print(f"Creating new project {args.name}")
            raise NotImplementedError()
            _create_conf(args, target_dir, conf["project"])

def _create_conf(args: argparse.Namespace, path: Path, conf: dict):
    if args.pyproject:
        module_name = f"fuddly_module_{args.name}"
    else:
        module_name = args.name

    for e in conf.values():
        f = path.joinpath(e["name"])
        # TODO copy files and interpolate the variables
        f.touch()
        f.write_text(
            e["content"].format(
                name=args.name,
                module_name=module_name,
                target=args.target.replace("-", "_")
            )
        )
