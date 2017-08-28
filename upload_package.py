#!/usr/bin/env python

import argparse
import os
import conanfile


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('remote')
    arg_parser.add_argument('user')
    arg_parser.add_argument('channel')

    args = arg_parser.parse_args()

    remote = args.remote
    user = args.user
    channel = args.channel
    name = conanfile.Hdf5Conan.name
    version = conanfile.Hdf5Conan.version

    cmd = """conan upload --all --remote {} {}/{}@{}/{}""".format(
        remote,
        name,
        version,
        user,
        channel
    )

    os.system(cmd)
