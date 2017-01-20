#! /usr/bin/env python2

"""Interactive client for imagej-server."""

from imagej_server import *
import argparse
import cmd
import json
import os
import re
import shlex
import sys


class InteractiveParser(argparse.ArgumentParser):
    """ArgumentParser that does not quit at parse errors."""

    def __init__(self, **kwargs):
        # change default value for add_help to False
        if 'add_help' not in kwargs:
            kwargs['add_help'] = False
        argparse.ArgumentParser.__init__(self, **kwargs)

    def error(self, message):
        # raise exception instead of exit at errors
        self.print_usage()
        raise Exception(message)


class InteractiveClient(cmd.Cmd):

    COMMANDS = frozenset(['list', 'detail', 'iterate', 'run', 'upload',
                          'download'])

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '(Client) '

        self.iter_idx = 0

        self.parsers = {command: InteractiveParser(prog=command)
                        for command in self.COMMANDS}
        ps = self.parsers

        p = ps['list']
        p.description = 'Lists available modules.'
        p.add_argument('-r', '--regex', metavar='PATTERN',
                       help='only list modules that match PATTERN')
        p.add_argument('-c', '--count', metavar='NUM', type=int, default=10,
                       help='list first NUM modules (default: 10)')

        p = ps['detail']
        p.description = 'Shows details of a module.'
        p.add_argument('id', metavar='ID',
                       help='Index of a module in the last "list", '
                       'or its full name.')

        p = ps['iterate']
        p.description = 'Iterates modules in last "list."'
        p.add_argument('count', metavar='NUM', nargs='?', type=int, default=10,
                       help='iterate the next NUM modules')
        p.add_argument('-r', '--reverse', action='store_true',
                       help='reverse the iteration order')

        p = ps['run']
        p.description = 'Runs a module.'
        p.add_argument('id', metavar='ID',
                       help='Index of a module in the last "list", '
                       'or its full name.')
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument('-i', '--inputs',
                           help='inputs to the module in JSON format')
        group.add_argument('-f', '--file', metavar='FILENAME',
                           help='file that contains the inputs in JSON format')
        p.add_argument('-n', '--no-process', action='store_true',
                       help='do not do pre/post processing')

        p = ps['upload']
        p.description = 'Uploads a file.'
        p.add_argument('data', metavar='FILENAME',
                       help='file to be uploaded')

        p = ps['download']
        p.description = 'Downloads a file.'
        p.add_argument('-f', '--format', metavar='FORMAT',
                       help='file format to be saved with')
        p.add_argument('-c', '--config',
                       help='configuration for saving the file')
        p.add_argument('source', metavar='SOURCE',
                       help='object ID if "format" is set, or filename otherwise')
        p.add_argument('-d', '--dest', default='.',
                       help='destination to save the file')

    def do_list(self, arg):
        """Lists available modules.

        Usage: list [-r PATTERN] [-c NUM]

        -r, --regex=PATTERN
            only list modules that match PATTERN

        -c, --count=[COUNT]
            List first COUNT modules (default: 10)

        Indices in the list could be used in "detail" and "run" commands.
        """

        try:
            arg = vars(self.parsers['list'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        if arg['regex'] is not None:
            try:
                pattern = re.compile(arg['regex'])
            except Exception:
                print('Illegal regex string')
                return

        try:
            self.modules = get_modules()
        except Exception as e:
            print(e)
            return

        if arg['regex'] is not None:
            self.modules = filter(pattern.search, self.modules)

        self.iter_idx = 0
        self.do_iterate(str(arg['count']))

    def do_detail(self, arg):
        """Shows details of a module.

        usage:  detail ID

        ID
            index of a module in the last "list", or its full name
        """

        try:
            arg = vars(self.parsers['detail'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        try:
            id = int(arg['id'])
            id = self.modules[id]
        except ValueError:
            id = arg['id']
        except IndexError:
            print('Index out of range. Try to call "list" with new query')
            return
        try:
            rsp = get_module(id)
            print(json.dumps(rsp, indent=4))
        except Exception as e:
            print(e)

    def do_iterate(self, arg):
        """Iterates modules in last "list."

        usage:  iterate [-r] [NUM]

        [NUM]
            iterate the next NUM modules (default: 10)

        -r, --reverse
            reverse the iteration order
        """

        try:
            arg = vars(self.parsers['iterate'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        if arg['count'] == 0:
            return
        if not arg['reverse']:
            end = min(self.iter_idx + arg['count'], len(self.modules))
            for i in xrange(self.iter_idx, end):
                print('%d: %s' % (i, self.modules[i]))
            if end == len(self.modules):
                self.iter_idx = 0
            else:
                self.iter_idx = end
                print('--use "it" to show more--')
        else:
            if self.iter_idx == 0:
                self.iter_idx = len(self.modules)
            start = max(self.iter_idx - arg['count'], 0)
            for i in reversed(xrange(start, self.iter_idx)):
                print('%d: %s' % (i, self.modules[i]))
            self.iter_idx = start

    do_it = do_iterate

    def do_run(self, arg):
        """Runs a module.

        usage:  run (-i INPUTS | -f FILENAME) [-n] ID

        ID
            index of a module in the last "list", or its full name

        -i, --inputs=INPUTS
            inputs to the module in JSON format

        -f, --file=FILENAME
            file that contains the inputs in JSON format

        -n, --no-process
            do not do pre/post processing
        """

        try:
            arg = vars(self.parsers['run'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        try:
            id = int(arg['id'])
            id = self.modules[id]
        except ValueError:
            id = arg['id']
        except IndexError:
            print('Index out of range. Try to call "ls" with new query')
            return

        if arg['file'] is not None:
            try:
                with open(arg['file']) as input_file:
                    inputs = input_file.read()
            except IOError:
                print('Cannot open file %s' % arg['file'])
                return
        else:
            inputs = arg['inputs']
        try:
            inputs = json.loads(inputs)
        except ValueError:
            print('Invalid JSON string')
            return

        try:
            rsp = run_module(id, inputs, not arg['no_process'])
            print(json.dumps(rsp, indent=4))
        except Exception as e:
            print(e)

    def do_upload(self, arg):
        """Uploads a file.

        usage: upload FILENAME

        FILENAME
            file to be uploaded
        """

        try:
            arg = vars(self.parsers['upload'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        try:
            with open(arg['data']) as data_file:
                rsp = upload_file(data_file)
            print(json.dumps(rsp, indent=4))
        except IOError:
            print('Cannot open file %s' % arg['data'])
        except Exception as e:
            print(e)

    def do_download(self, arg):
        """Downloads a file.

        usage:  download [-f FORMAT] [-c CONFIG] [-d DEST] SOURCE

        SOURCE
            object ID obtained from "upload" or "run" if "format" is set, or
            filename obtained from "download" otherwise

        -f, --format=FORMAT
            file format to be saved with

        -c, --config=CONFIG
            configuration in JSON format for saving the file (only used if
            "format" is set)

        -d, --dest=DEST
            destination for saving the file (default: current directory)
        """

        try:
            arg = vars(self.parsers['download'].parse_args(shlex.split(arg)))
        except Exception as e:
            print('Fail to parse arguments: %s' % e)
            return

        if arg['format'] is not None:
            config = None
            if arg['config'] is not None:
                try:
                    config = json.loads(arg['config'])
                except Exception:
                    print('Fail to parse config')
                    return

            try:
                rsp = request_file(arg['source'], arg['format'], config)
                print(json.dumps(rsp, indent=4))
            except Exception as e:
                print(e)
                return
            filename = rsp['filename']
        else:
            filename = arg['source']

        if os.path.isdir(arg['dest']):
            dest = os.path.join(arg['dest'], filename)
        else:
            dir = os.path.dirname(arg['dest'])
            if not os.path.isdir(dir):
                print('Directory does not exist: %s' % dir)
                return
            dest = arg['dest']
        if os.path.isfile(dest):
            print('File already exists: %s' % dest)
            return

        try:
            with open(dest, 'wb') as d:
                content = retrieve_file(filename)
                d.write(content)
        except IOError:
            print('Cannot write to %s' % dest)
        except Exception as e:
            print(e)

    def do_stop(self, arg):
        """Stops imagej-server gracefully.

        usage: stop
        """

        stop()

    def do_quit(self, arg):
        return 1

    do_q = do_quit
    do_exit = do_quit
    do_EOF = do_quit


def main():
    InteractiveClient().cmdloop()

if __name__ == '__main__':
    main()
