import fuddly.cli.argparse_wrapper as argparse
from fuddly.cli.error import CliException
import sys
import os.path




def get_scripts() -> list():
    import fuddly.framework.global_resources as gr
    from importlib.metadata import entry_points
    import pkgutil

    paths = []
    script_dir = os.path.join(gr.fuddly_data_folder, "projects_scripts")
    if os.path.isdir(script_dir):
        path, _, files = next(os.walk(script_dir))
        for f in files:
            paths.append("fuddly.project_scripts." + f.removesuffix(".py"))


    for ep in entry_points(group=gr.ep_group_names["projects"]):
        p = pkgutil.get_loader(ep.module).path
        if os.path.basename(p) == "__init__.py":
            p=os.path.dirname(p)
        else:
            # Ignoring old single-files projects
            continue
        if os.path.isdir(os.path.join(p, "scripts")):
            for f in next(os.walk(os.path.join(p, "scripts")))[2]:
                if f.endswith(".py")  and f != "__init__.py":
                    paths.append(ep.module + ".script." + f.removesuffix(".py"))

    return paths

# TODO why does this not work 😥
def script_argument_completer(prefix, parsed_args, **kwargs):
    print(parsed_args, file=out)
    return ["HAAAAAA"]

def start(args: argparse.Namespace):
    sys.argv=[]
    sys.argv.append(args.script)
    sys.argv.extend(args.args[0]) # Why is this an array, that weird - someting to do with nargs

    script_dir = "/tmp"
    sys.path.append(script_dir)

    if args.list:
        for i in get_scripts():
            print(i)
        return 0

    if args.script is None:
        raise CliException("Missing tool name")

    # TODO execute the script from the script directory
    raise NotImplementedError("Not implemented yet")
