@setlocal enableextensions & "%~dp0python/python.exe" -x "%~f0" %* & goto :EOF

import os
import sys

build = sys.argv[1]
setup = sys.argv[2]

print(f'Applying game setup on "{build}" for "{setup}" ...')

setup_file = 'game_setup.csv'

if os.path.isfile(setup_file):
    modified_lines = []
    with open(setup_file,'r') as setup_file_io:
        header = setup_file_io.readline()  # Read header line
        columns = header.strip().split(',')
        if len(columns) > 1 and columns[0] == 'name':
            for setup_line in setup_file_io.readlines():
                setup_line = setup_line.strip().split(',')
                print(f'Processing line: {setup_line}')
               
                if len(setup_line) > 1:
                    game_name = setup_line[0].strip()
                    game_ini_file = f'../{build}/emulators/mame/ini/{game_name}.ini'
                    value_map = {}
                    
                    # Iterate through the game_setup.csv columns and map the values based on the setup
                    for i, column in enumerate(columns[1:], start=1):
                        column = column.strip().split('_')
                        col_prop = column[0].strip()
                        col_setup = column[1].strip() 
                        value = setup_line[i].strip()

                        if (col_setup==setup):
                            value_map[col_prop] = value
                        
                        if not col_prop in value_map:
                            value_map[col_prop] = ''

                    print(f'Value map for {game_name}: {value_map}')

                    new_lines = []
                    # Read the existing game ini file and combine it with the values from the value_map
                    with open(game_ini_file,'r') as game_ini_file_io:
                        for game_line in game_ini_file_io.readlines():
                            game_line = game_line.strip()
                            if game_line:
                                print(game_line)
                                game_line = game_line.split()
                                prop = game_line[0].strip()
                                value = game_line[1].strip()
                                if prop in value_map:
                                    value = value_map.pop(prop)
                                    if value:
                                        new_lines.append(f'{prop} {value}\n')
                                elif not prop in value_map:
                                    new_lines.append(f'{prop} {value}\n')
                        for prop, value in value_map.items():
                            if value:
                                new_lines.append(f'{prop} {value}\n')
                            
                    with open(game_ini_file,'w') as game_ini_file_io:
                        game_ini_file_io.writelines(new_lines)

                else:
                    print('Invalid line format')
        else:
            print('Invalid line format')

else:
    print('Failed applying game setup')
