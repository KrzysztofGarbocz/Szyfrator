"""Application to encrypt and decrypt single txt file or all select directory ( only txt file)"""

import argparse
import getpass
import pathlib
from time import time
from argparse import ArgumentParser, Namespace, ArgumentError
from typing import Any
from tqdm import tqdm
from os import walk
from crypto import Decryption, Encryption, Append
from cryptography.fernet import InvalidToken


def invalid_name(value: str):
    if value.endswith(('.txt', '.secret')):
        return value
    raise argparse.ArgumentError


class Password(argparse.Action):
    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string) -> None:
        if values is None:
            values = getpass.getpass()
            setattr(namespace, self.dest, values)


def list_file_to_process(dir_name: str):
    to_file_process = []
    for path, dirs, files in walk(dir_name):
        for file in files:
            if file.endswith(('.txt', '.secret')):
                to_file_process.append(f'{path}\{file}')
    return to_file_process

    
def main(args):
    try:
        if args.dir:
            to_file_process = list_file_to_process(args.dir)
        elif args.file:
            to_file_process = args.file
        else:
            raise argparse.ArgumentError()

        if args.verbose > 2 and args.file:
            to_file_process = tqdm(args.file)

        if args.verbose > 2 and args.dir:
            to_file_process = tqdm(list_file_to_process(args.dir))

        for file in to_file_process:
            before = time()
            path = pathlib.Path(file)
            if 'encrypt' == args.mode:
                action = Encryption(path)
            elif args.mode == 'decrypt':
                action = Decryption(path)
            elif args.mode == 'append':
                text = input(' What you need to append? ')
                action = Append(path, text)

            action.verbosity = args.verbose
            action.execute(str(args.password))
            after = time()

            if 3 > args.verbose > 0:
                print(file + '  ', end='')
                if args.verbose > 1:
                    times = after-before
                    print(f'Encrypt/Decrypt time is: {times:.3f}')
                print()
            if args.verbose > 2:
                to_file_process.set_description(file)


    except InvalidToken:
        print('Wrong password!')
    except ArgumentError:
        print("Not define file or directory")


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description='Keep my secrets safe!!!',
                                    formatter_class=argparse.RawTextHelpFormatter)
    parse.add_argument('-m', '--mode', choices=['encrypt', 'decrypt', 'append'], required=True,
                       help='''encrypt --> file encrypt
    decrypt --> decryption file decryption
    append --> append text to encrypted file''')

    group = parse.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', action='append', type=invalid_name, help='Choose file')
    group.add_argument('-d', '--dir', help='path to file process')

    group1 = parse.add_mutually_exclusive_group()
    group1.add_argument('-v', '--verbose', default=0, action='count', help='Verbose')
    group1.add_argument('-q', '--quiet', default=False, action='store_true', help='Quiet')

    parse.add_argument('-p', '--password', required=True, help='Enter password', nargs='?',
                       dest='password', action=Password)

    arg = parse.parse_args()

    main(arg)

