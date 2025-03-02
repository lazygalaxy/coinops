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
        + "WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS) OR c.year in ('Swap','theme') order by LOWER(name) ASC"
    )

    # get column names from cursor.description
    sqlColumnNames = [desc[0] for desc in curs.description]
    print(sqlColumnNames)

    # iterate through each sql row and add the info in a dictionary
    gameInfo = {}
    otherInfo = {}
    csvFieldNames = []
    for sqlQueryRow in curs.fetchall():
        theInfo = {}
        gameKey = sqlQueryRow[sqlColumnNames.index('NAME')].strip()
        if not gameKey:
            print('no gameKey exists')
            sys.exit(1)

        for sqlColumnName in sqlColumnNames:
            value = None

            match sqlColumnName:
                case "MANUFACTURER2":
                    if (
                        not "manufacturer" in theInfo
                        or theInfo["manufacturer"].lower() == "other"
                    ):
                        value = sqlQueryRow[sqlColumnNames.index(sqlColumnName)]
                        sqlColumnName = "manufacturer"
                case 'ORIENTATION':
                    year = theInfo["year"]
                    if year and not year == 'Swap' and not year == 'theme':
                        orientation = sqlQueryRow[sqlColumnNames.index(sqlColumnName)]
                        if orientation and (orientation == '90' or orientation == '270'):
                            value = 'vertical'
                        else:
                            value = 'horizontal'
                case 'PLAYERS2':
                    if not "players" in theInfo or theInfo["players"] == "0":
                        value = sqlQueryRow[sqlColumnNames.index(sqlColumnName)]
                        sqlColumnName = 'players'
                case 'YEAR2':
                    if not "year" in theInfo:
                        value = sqlQueryRow[sqlColumnNames.index(sqlColumnName)]
                        sqlColumnName = 'year'
                case _:
                    value = sqlQueryRow[sqlColumnNames.index(sqlColumnName)]

            if value:
                sqlColumnName = sqlColumnName.lower()
                value = value.strip()
                value = value.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
                theInfo[sqlColumnName] = value
                csvFieldNames.append(sqlColumnName)

        if theInfo['year'] == 'theme' or theInfo['year'] == 'Swap':
            otherInfo[gameKey] = theInfo
        else:
            gameInfo[gameKey] = theInfo

    # gameInfo = dict(
    #     sorted(gameInfo.items(), key=lambda item: (item[1]['year'], item[1]['name'].lower()))
    # )

    # iterate through the dictionary and create the xml elements
    menuElement = ET.Element('menu')
    for gameKey in gameInfo:
        gameElement = ET.SubElement(menuElement, 'game', name=gameKey)
        for field in gameInfo[gameKey]:
            if not field == 'name':
                ET.SubElement(gameElement, field).text = gameInfo[gameKey][field]

    for gameKey in otherInfo:
        gameElement = ET.SubElement(menuElement, "game", name=gameKey)
        for field in otherInfo[gameKey]:
            if not field == "name":
                ET.SubElement(gameElement, field).text = otherInfo[gameKey][field]

    # save the xml
    dom = xml.dom.minidom.parseString(ET.tostring(menuElement))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split('?>')

    with open('gameinfo/generate_files/MAME.xml', 'w') as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()

    # save the csv
    with open('gameinfo/generate_files/GameList.csv', mode='w', newline='') as file:
        csvFieldNames = [
            'name',
            'description',
            'cloneof',
            'year',
            'players',
            'ctrltype',
            'manufacturer',
            'category',
            'orientation',
            'ctrltype2',
            'joyways',
            'buttons'
        ]

        writer = csv.DictWriter(file, delimiter="\t", fieldnames=csvFieldNames)
        writer.writeheader()
        writer.writerows(gameInfo.values())

    print('finito!')

finally:
    curs.close()
    secret.conn.close()
