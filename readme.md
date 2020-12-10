
# Presentation

This tool is a self-contained tool in Python that can be used for secure messaging. The tool is able to apply a One-Time Pad cipher to a given message.

The idea is simple: we have a sequence of cryptographically secure
random numbers, of which only two copies exist. These are called
pads.

The sender and the recipient each have one of the copies.
When you send a message, you take each number of the message and
“shift” it by the corresponding number of the random sequence, in the same way you’d do with a
dumb caesar cipher. The spent random sequence is then shredded so it can’t be used again. Upon the
reception, the only remaining copy of the random sequence is used to undo the shift resulting in the
cleartext message, after which it is also shredded.

# Usage

The program has three modes (generate, send, receive) specified through the -g,
-s, -r switches. If the switch is not provided generate mode is assumed.  
The program takes a mandatory positional argument: the name of a directory that will
be used to store the pads.

## Generate mode

The program will generate 100 pads. Each batch of 100 pads will reside in a subfolder of the
directory specified through the positional argument. For example after two runs with "dir"
as positional argument you should have dir/0000 and dir/0001 each containing 100
pads.  
Each individual pad is a set of three files: (00p, 00c, 00s up to 99p, 99c, 99s).

Exemple:
```
./main.py dir/ 
```

## Send mode

The text to send should be specified by one of three methods:
 - if neither -f nor -t is specified : read from standard input
 - if -f filename is specified : read from the file filename.
 - If -t "some text" is specified : read from the command line.

If the message is too long to fit in one pad, the program will exit with an error message.

Exemples:
```
cat secret.txt | ./main.py dir/0000/ -s
./main.py dir/0000/ -s -f secret.txt
./main.py dir/0000/ -s -t "This is a very secret message"
```

## Receive mode

The transmission to decrypt should be specified as a second positional argument
filename.

Exemple
```
./main.py dir/0000/ dir-0000-00t -r
```

# Full exemple

> In this exemple, we will use the argument `--verbose` to show more info about what's going on. We will also use `--no-shred` to pred the program to delete 00c, therefore saving us from having to copy it.

## Pad creation

I create my pads in the folder `dir/` using :
```
./main.py dir/ -g --verbose
```
Output : 
```
[G] Creating folder dir/0000/
[G] Generating random pads in dir/0000/
[G] Genetrated pads in dir/0000/
```

## Encrypt

Then, using the created pads, I encrypt the message using :
```
./main.py dir/0000/ -s -t "This is a very secret message" --verbose --no-shred
```
Output : 
```
[S] Using pad : 00c in dir/0000/
[S] Encrypted data is b'\xa9\x04\xfd\xaai\xbb\xe9\x7fs\x0e\xa8\x80\x82\xce\x13\xd0\x9d\x81R>>\x85\xd14\xf8\x13\xb2N{'
[S] Wrote encrypted text in dir-0000-00t
```

Now, i got my encrypted message in `dir-0000-00t`

## Decrypt

Now, since we use `--no-shred` I can decypher the message with :
```
./main.py dir/0000/ dir-0000-00t -r --verbose --no-shred
```
Output :
```
[R] Read 125 bytes from dir-0000-00t
[R] Found idx from prefix : idx=0
[R] Suffix validated with idx=0
[R] Found message 'This is a very secret message'
[R] Wrote message in 'dir-0000-00m'
```

My clear message is in `dir-0000-00m`