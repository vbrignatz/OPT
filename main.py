#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" main.py: 
usage: main.py [-h] [-f FILENAME] [-t TEXT] [-s] [-r] [-g] directory [filename]

Generate, send or recieve a message throught a OTP cypher.

positional arguments:
  directory             The directory containing the pads
  filename              The filename to read the message from (receive mode only)

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        A file containing text to send (send mode only)
  -t TEXT, --text TEXT  Text to send (send mode only)
  -s, --send            If specified, will set script in send mode (default is generate)
  -r, --receive         If specified, will set script in receive mode (default is generate)
  -g, --generate        If specified, will set script in generate mode (default is generate)
Author : Vincent Brignatz
"""


import argparse
import subprocess
import os

def generate(dir):

    os.makedirs(f"{dir}", exist_ok=True)

    # find what name to create dir with
    ldir = []
    for d in os.listdir(dir):
        try:
            ldir.append(int(d))
        except:
            pass
    
    if len(ldir) <= 0:
        # if no folder are present in dir, folder is 0000 dir
        folder = "0000/"
    else:
        folder = "{:04d}/".format(max(ldir)+1)

    # Create dir XXXX
    os.mkdir(f"{dir}{folder}")

    for i in range(100):
        for letter, n_bytes in {"p":48, "s":48, "c":2000}.items():
            # with open(F"{dir}{folder}/{i:02d}{letter}", "w") as fout:
            #     subprocess.run(f"hexdump -n {n_bytes} /dev/random".split(" "), stdout=fout)
            # TODO : remove display
            subprocess.run(f"dd if=/dev/urandom of={dir}{folder}/{i:02d}{letter} bs=1 count={n_bytes}".split(" "))

    print(f"Genetrated files in {dir}{folder}")

def send(dir, text):
    # TODO: check that dir exist

    # find smallest nb dir
    ldir = []
    for d in os.listdir(dir):
        try:
            ldir.append(int(d))
        except:
            pass

    if len(ldir) <= 0:
        raise Warning(f"No suitable pads folder found in '{dir}'")

    folder = f"{min(ldir):04d}/"

    first_available_pad = sorted([filename for filename in os.listdir(f"{dir}{folder}") if filename.endswith("c")])[0]

    output_filename = dir.replace('/', '-')+folder.replace('/', '-')+first_available_pad.replace('c', 't')
    with open(output_filename, "wb") as fout:
        # write preffix
        with open(dir+folder+first_available_pad.replace('c', 'p'), "rb") as prefix:
            fout.write(prefix.read(48))

        # append cypher msg
        with open(dir+folder+first_available_pad, "rb") as cypher:
            for char in text:
                code = int.from_bytes(cypher.read(1), "big")
                byte = (ord(char) + code) % 256
                fout.write(int.to_bytes(byte, 1, "big"))

        # append suffix
        with open(dir+folder+first_available_pad.replace('c', 's'), "rb") as suffix:
            fout.write(suffix.read(48))

    # TODO: destroy first_available_pad
    print(f"Wrote OPT text in {output_filename}")


def receive(dir, filename):
    # TODO: implement receive mode
    pass

if __name__=="__main__":

    # TODO : detect if network interface is up

    parser = argparse.ArgumentParser(description='Generate, send or recieve a message throught a OTP cypher.')
    parser.add_argument("directory", type=str,
                    help="The directory containing the pads")
    parser.add_argument("filename", nargs='?', type=str,
                    help="The filename to read the message from (receive mode only)")
    parser.add_argument('-f', "--filename", type=str,
                        help='A file containing text to send (send mode only)')
    parser.add_argument('-t', "--text", type=str,
                        help='Text to send                   (send mode only)')
    parser.add_argument('-s', "--send", action="store_true",
                        help='If specified, will set script in send mode     (default is generate)')
    parser.add_argument('-r', "--receive", action="store_true",
                        help='If specified, will set script in receive mode  (default is generate)')
    parser.add_argument('-g', "--generate", action="store_true",
                        help='If specified, will set script in generate mode (default is generate)')

    args = parser.parse_args()

    if args.directory[-1] != "/":
        args.directory += "/"

    print(args.filename)

    if sum([args.send, args.receive, args.generate]) > 1:
        raise Warning("User specified more than one mode, please select only one mode using -s, -r or -g")

    if args.send:
        if args.filename:
            text = args.filename
        elif args.text:
            text = args.text
        else:
            text = "test message" # TODO : use standar input
        send(args.directory, text)
    elif args.receive:
        if not args.filename:
            raise Warning("User should specify a filename when using receive mode")
        receive(args.directory, args.filename)
    else:
        generate(args.directory)