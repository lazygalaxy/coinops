@setlocal enableextensions & "%~dp0python/python.exe" -x "%~f0" %* & goto :EOF

import os
import sys

build = sys.argv[1] 
print(f'Adjusting mame.ini on "{build}"')
ini_file = f'../{build}/emulators/mame/mame.ini'

if os.path.isfile(ini_file):
    modified_lines = []
    with open(ini_file,'r') as io:
        for line in io.readlines():
            
            split = line.strip().lower().split()
            if split:
                if split[0] == 'artwork_crop':
                    line = 'artwork_crop              1\n'
        
            modified_lines.append(line)
                   
    # write file back to disk
    with open(ini_file,'w') as io:
        io.writelines(modified_lines)
else:
    print('Failed Adjusting mame ini')
        
    