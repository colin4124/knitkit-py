# See LICENSE for license details.

import argparse
import os
import sys
import pkg_resources
import tarfile
import shutil
import yaml
import mill_bin
import mill_cache
import glob

# Check if this is run from a local installation
knitkitdir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
if os.path.exists(os.path.join(knitkitdir, "knitkit")):
    sys.path[0:0] = [knitkitdir]

from knitkit import __version__

def read_lines(path):
    with open(path,'r') as f:
        return f.readlines()

def get_resource_name(name):
    return pkg_resources.resource_filename(__name__, name)

def get_resource_string(name):
    return pkg_resources.resource_string(__name__, name)

class ScratChip:
    prj_name = "None"
    prj_path = "None"
    knitkit_path = '.knitkit'
    cfg = None

    def __init__(self, prj_name, cfg):
        self.prj_name = prj_name
        self.prj_path = os.path.abspath(self.prj_name)
        with open(cfg) as file:
            if sys.version_info.major == 3 and sys.version_info.minor >= 6:
                self.cfg = yaml.load(file, Loader=yaml.FullLoader)
            else:
                print(sys.version_info)
                self.cfg = yaml.load(file)

    def create(self):
        if self.prj_name != '.':
            os.mkdir(self.prj_name)

        self.create_dir(self.prj_path, self.cfg["hierarchy"])

        # shutil.copyfile(get_resource_name("assets/default.yaml"), os.path.join(self.prj_path, "config.yaml"))

    def init(self):
        cache_path = os.path.join(self.prj_path, self.knitkit_path)
        mill_path = os.path.join(self.prj_path, self.knitkit_path + '/mill')
        jars_path = os.path.join(self.prj_path, self.knitkit_path + '/jars')
        knitkit_jar_path = os.path.join(jars_path, 'knitkit.jar')

        if not os.path.exists(cache_path):
            self.extract_cache(mill_cache.source, cache_path)
        if not os.path.exists(mill_path):
            shutil.copyfile(mill_bin.source, mill_path)
        if not os.path.exists(jars_path):
            os.makedirs(jars_path)
        if not os.path.exists(knitkit_jar_path):
            knitkit_src = get_resource_name("jars/knitkit.jar")
            shutil.copyfile(knitkit_src, knitkit_jar_path)

    def dump_default_cfg(self, cfg, dump_name):
       shutil.copyfile(cfg, dump_name)

    def create_dir(self, path, dir_tree):
        for (k, v) in dir_tree.items():
            sub_dir = os.path.join(path, k)
            if isinstance(v, dict):
                os.mkdir(sub_dir)
                self.create_dir(sub_dir, v)
            elif 'project.mk' in v:
                self.gen_project_mk(v, sub_dir)
            elif 'Main.scala' in v:
                self.gen_demo_chisel(v, sub_dir)
            elif v == '':
                os.mkdir(sub_dir)
            else:
                f = get_resource_name(v)
                shutil.copyfile(f, sub_dir)

    def gen_project_mk(self, template, dest):
        dest_path = os.path.dirname(os.path.join(self.prj_path, dest))
        orig = get_resource_string(template).decode("utf-8")
        res = orig.format(
            mill_path = self.knitkit_path + '/mill',
            mill_lib_path = self.knitkit_path + '/jars',
            mill_cache_path = self.knitkit_path + '/.cache',
        )
        with open(dest, 'w') as f:
            f.write(res)

    def gen_demo_chisel(self, template, dest):
        dest_path = os.path.dirname(os.path.join(self.prj_path, dest))
        rel_path = os.path.relpath(self.prj_path, dest_path)
        res = get_resource_string(template).decode("utf-8")
        with open(dest, 'w') as f:
            f.write(res)

    def extract_cache(self, src, dest):
        tar = tarfile.open(src, "r:gz")
        tar.extractall(dest)
        tar.close()

    def read_yaml(self, cfg_path):
        with open(cfg_path) as file:
            if sys.version_info.major == 3 and sys.version_info.minor >= 6:
                return yaml.load(file, Loader=yaml.FullLoader)
            else:
                return yaml.load(file)

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.set_defaults(prj_name='.')
    # Global actions
    parser.add_argument(
        "--version",
        help="Show the ScratChip version",
        action="version",
        version=__version__,
    )

    parser.add_argument(
        "--config",
        help="ScratChip Configure",
        nargs=1,
        default=get_resource_name("assets/default.yaml"),
        type=str,
    )

    # create subparser
    parser_create = subparsers.add_parser(
        "create", help="Create the project"
    )

    parser_create.add_argument(
        'prj_name', metavar='project name', type=str, nargs='?',
        default='.', help='Create Project with name')

    parser_create.set_defaults(func=create)

    # init subparser
    parser_init = subparsers.add_parser(
        "init", help="Initialize the project"
    )

    parser_init.add_argument(
        'prj_name', metavar='project name', type=str, nargs='?',
        default='.', help='Initialize Project specify by name')
    parser_init.set_defaults(func=init)

    # dump cfg subparser
    parser_dump_cfg = subparsers.add_parser(
        "dump_cfg", help="Dump configuare with YAML"
    )

    parser_dump_cfg.add_argument(
        'dump_name', type=str, nargs='?',
        default='config.yml', help='Dump Configure file name ')
    parser_dump_cfg.set_defaults(func=dump_cfg)

    # generate filelist
    parser_filelist = subparsers.add_parser("filelist", help="""
        is_library_file: -v, is_library_dir: -y is_include_dir: +incdir+
    """
    )
    parser_filelist.add_argument(
        'project_cfg', type=str, nargs='?',
        default='project.yml', help='Project configure file path')
    parser_filelist.add_argument(
        '--target', '-t', type=str, nargs='?',
        default='all', help='filelist target, default is all')

    parser_filelist.set_defaults(func=gen_filelist)

    args = parser.parse_args()

    if hasattr(args, "func"):
        return args
    if hasattr(args, "subparser"):
        args.subparser.print_help()
    else:
        parser.print_help()
        return None

def create(args):
    prj_name = args.prj_name
    cfg = args.config
    if isinstance(args.config, list):
        cfg = args.config[0]
    sc = ScratChip(prj_name, cfg)
    sc.create()
    sc.init()

def init(args):
    prj_name = args.prj_name
    cfg = args.config
    if isinstance(args.config, list):
        cfg = args.config[0]
    sc = ScratChip(prj_name, cfg)
    sc.init()

def dump_cfg(args):
    cfg = get_resource_name("assets/default.yaml")
    dump_name = args.dump_name
    shutil.copyfile(cfg, dump_name)

def gen_filelist(args):
    cfg = get_resource_name("assets/default.yaml")
    prj_cfg = args.project_cfg
    target = args.target
    if isinstance(args.config, list):
        cfg = args.project_cfg[0]
    sc = ScratChip('.', cfg)
    sc.gen_filelist(prj_cfg, target)

def main():
    args = parse_args()
    if not args:
        exit(0)

    # Run the function
    args.func(args)

if __name__ == "__main__":
    main()