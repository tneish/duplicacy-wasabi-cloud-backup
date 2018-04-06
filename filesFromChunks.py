#!/usr/bin/python3
import json
import sys
import pdb

# this is a list of chunks that duplicacy reports as missing.
missingChunks = ['0061beab88965b442e5d621a22dcd2b77f8dd359a2d353bd29dedd8c7595bb28',
            ]  
# do 'duplicacy cat -r <n> > dcat' for this file.
fname = 'dcat'  

# the following might need to be done a different way to handle snapshots with many files & chunks
fptr = open(fname, 'r')
fbuff = fptr.read()
fdecoded = json.loads(fbuff)

if not 'chunks' in fdecoded.keys():
    print('Error: Could not find chunklist in decoded output, exiting')
    sys.exit(1)

missingChunkNumbers = []

for c in missingChunks:
    try:
        missingChunkNumbers.append(fdecoded['chunks'].index(c))
    except ValueError:
        print('Warning: Could not find missing chunk ' + \
                str(c) + ' in snapshot content, continuing')

excludeFileList = []

for f in fdecoded['files']:
    try:
        s = f['content'].split(':')
        if (int(s[0]) in missingChunkNumbers) or (int(s[2]) in missingChunkNumbers):
            excludeFileList.append(f['path'])
    except KeyError:
        # a directory has no 'content' key (since size is 0, nothing to store in chunks)
        pass

print('\n'.join(excludeFileList))


