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

def generate(dir, verbose=False):

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

def send(dir, text, verbose=False):
    """
    dir should be /pads/0000/
    """

    # TODO: check that dir exist

    available_pads = [filename for filename in os.listdir(dir) if filename.endswith("c")]
    if len(available_pads) <= 0:
        raise Warning(f"No available pads found in {dir}")
    first_available_pad = sorted(available_pads)[0]

    if verbose:
        print(f"[S] Using pad : {first_available_pad} in {dir}{folder}")

    output_filename = dir.replace('/', '-')+first_available_pad.replace('c', 't')
    output_data = b''
    
    # write preffix
    with open(dir+first_available_pad.replace('c', 'p'), "rb") as prefix:
        output_data += prefix.read(48)

    # append cypher msg
    with open(dir+first_available_pad, "rb") as cypher:
        cypher_data = cypher.read(len(text))
    
    for char, code in zip(text, cypher_data):
        # code = int.from_bytes(cypher.read(1), "big")
        byte = (ord(char) + code) % 256
        output_data += int.to_bytes(byte, 1, "big")

    if verbose:
        print(f"[S] Encrypted data is {output_data[48:]}")

    # append suffix
    with open(dir+first_available_pad.replace('c', 's'), "rb") as suffix:
        output_data += suffix.read(48)

    with open(output_filename, "wb") as fout:
        fout.write(output_data)

    if verbose:
        print(f"[S] Wrote encrypted text in {output_filename}")

    # TODO: destroy first_available_pad


def receive(dir, filename, verbose=False):
    """
    dir should be /pads/0000/
    """

    # read the data from the file
    with open(filename, "rb") as fin:
        data = fin.read()

    if verbose:
        print(f"[R] Red {len(data)} bytes from {filename}")

    # Get prefix and suffix
    prefix, suffix = data[:48], data[-48:]

    idx = None
    for pad in [filename for filename in os.listdir(dir) if filename.endswith("p")]:
        with open(dir+pad, "rb") as file_preffix:
            if file_preffix.read(48) == prefix:
                idx = int(pad.replace('p', ''))
                break

    if idx is None:
        raise Warning(f"Could not find prefix in {dir}")

    if verbose:
        print(f"[R] Found idx from prefix : idx={idx}")

    # TODO: also check suffix

    if verbose:
        print(f"[R] Suffix validated with idx={idx}")

    n_data = len(data) - 48*2
    with open(dir+f"{idx:02d}c", "rb") as file_cypher:
        cypher = file_cypher.read(n_data)
    
    text = ""
    for char, code in zip(data[48:-48], cypher):
        text += chr((char - code) % 256)

    if verbose:
        print(f"[R] Found message '{text}'")

    with open(filename.replace("t", "m"), "w") as fout:
        fout.write(text)

    if verbose:
        print(f"[R] Wrote message in '{filename.replace('t', 'm')}'")

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
    parser.add_argument('-v', "--verbose", action="store_true",
                        help='If specified, will print informations about the process')

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
        send(args.directory, text, args.verbose)
    elif args.receive:
        if not args.filename:
            raise Warning("User should specify a filename when using receive mode")
        receive(args.directory, args.filename, args.verbose)
    else:
        generate(args.directory)