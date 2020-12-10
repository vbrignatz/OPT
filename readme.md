
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

## Send mode
The text to send should be specified by one of three methods:
 - if neither -f nor -t is specified, it should be read from standard input
 - if -f filename is specified it should be read from the file filename.
 - If -t "some text" is specified it should be read from the command line.

If the message is too long to fit in one pad, the program will exit with an error message.


## Receive mode

The transmission to decrypt should be specified as a second positional argument
filename.


