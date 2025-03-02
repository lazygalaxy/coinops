import sys
import secret
import xml.etree.cElementTree as ET
import xml.dom.minidom
import csv

m_encoding = 'UTF-8'

try:
    # get the gameinfo from snowflake
    curs = secret.conn.cursor()
    curs.execute(
        "select c.name as name, c.description as description, COALESCE(m.cloneof,m2.cloneof) as cloneof, COALESCE(m.year,m2.year) as year, c.year as year2, COALESCE(m.players,m2.players) as players, c.players as players2, c.ctrltype as ctrltype, c.manufacturer as manufacturer, COALESCE(m.manufacturer,m2.manufacturer) as manufacturer2,"
        + "r.category as category, COALESCE(m.rotate,m2.rotate) as orientation, COALESCE(m.type,m2.type) as ctrltype2, COALESCE(m.ways, m2.ways) as joyways, COALESCE(m.buttons,m2.buttons) as buttons "
        + "from COINOPS_MAME_FLAT as c "
        + "LEFT OUTER JOIN COINOPS_DELUXE_MAX_ROMS AS r ON c.name = r.file "
        + "LEFT OUTER JOIN REF_MAME_274_FLAT AS m ON r.file = m.name "
        + "LEFT OUTER JOIN REF_MAME_274_FLAT AS m2 ON r.rom = m2.name "
        + "WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS) OR c.year in ('Swap','theme') order by c.year,c.name ASC"
    )

    # get column names from cursor.description
    columns = [desc[0] for desc in curs.description]
    print(columns)

    # iterate through each sql row and add the info in a dictionary
    gameinfo = {}
    for row in curs.fetchall():
        gameKey = None

        for column in columns:
            value = None

            match column:
                case "MANUFACTURER2":
                    if (
                        not "manufacturer" in gameinfo[gameKey]
                        or gameinfo[gameKey]["manufacturer"].lower() == "other"
                    ):
                        value = row[columns.index(column)]
                        column = "manufacturer"
                case 'NAME':
                    # for each row we expect a name which is actually the game key
                    gameKey = row[columns.index(column)].strip()
                    if not gameKey:
                        print('no gameKey exists')
                        sys.exit(1)
                    gameinfo[gameKey] = {}
                case 'ORIENTATION':
                    year = gameinfo[gameKey]['year']
                    if year and not year == 'Swap' and not year == 'theme':
                        orientation = row[columns.index(column)]
                        if orientation and (orientation == '90' or orientation == '270'):
                            value = 'vertical'
                        else:
                            value = 'horizontal'
                case 'PLAYERS2':
                    if (
                        not 'players' in gameinfo[gameKey]
                        or gameinfo[gameKey]['players'] == '0'
                    ):
                        value = row[columns.index(column)]
                        column = 'players'
                case 'YEAR2':
                    if not 'year' in gameinfo[gameKey]:
                        value = row[columns.index(column)]
                        column = 'year'
                case _:
                    value = row[columns.index(column)]

            if value:
                value = value.strip()
                value = value.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
                gameinfo[gameKey][column.lower()] = value

    gameinfo = dict(
        sorted(gameinfo.items(), key=lambda item: (item[1]["year"], item[1]["description"]))
    )

    # iterate through the dictionary and create the xml elements
    menuElement = ET.Element('menu')
    for gameKey in gameinfo:
        gameElement = ET.SubElement(menuElement, 'game', name=gameKey)
        for field in gameinfo[gameKey]:
            ET.SubElement(gameElement, field).text = gameinfo[gameKey][field]

    # save the xml
    dom = xml.dom.minidom.parseString(ET.tostring(menuElement))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split('?>')

    with open('gameinfo/generate_files/MAME.xml', 'w') as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()

    # save the csv
    for gameKey in list(gameinfo):
        year = gameinfo[gameKey]['year']
        if year == 'theme' or year == 'Swap':
            gameinfo.pop(gameKey)

    with open("gameinfo/generate_files/GameList.csv", mode="w", newline="") as file:
        fieldnames = [
            "description",
            "cloneof",
            "year",
            "players",
            "ctrltype",
            "manufacturer",
            "category",
            "orientation",
            "ctrltype2",
            "joyways",
            "buttons",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(gameinfo.values())

    print('finito!')
finally:
    curs.close()
    secret.conn.close()
