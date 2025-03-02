import secret
import xml.etree.cElementTree as ET
import xml.dom.minidom
import csv

m_encoding = "UTF-8"

try:
    # get the gameinfo from snowflake
    curs = secret.conn.cursor()
    curs.execute(
        "select c.name, c.description, COALESCE(m.cloneof,m2.cloneof), c.year, COALESCE(m.year,m2.year), c.players, COALESCE(m.players,m2.players), c.ctrltype, c.manufacturer, COALESCE(m.manufacturer,m2.manufacturer),"
        + "r.category, COALESCE(m.rotate,m2.rotate), COALESCE(m.type,m2.type), COALESCE(m.ways, m2.ways), COALESCE(m.buttons,m2.buttons) "
        + "from COINOPS_MAME_FLAT as c "
        + "LEFT OUTER JOIN COINOPS_DELUXE_MAX_ROMS AS r ON c.name = r.file "
        + "LEFT OUTER JOIN REF_MAME_274_FLAT AS m ON r.file = m.name "
        + "LEFT OUTER JOIN REF_MAME_274_FLAT AS m2 ON r.rom = m2.name "
        + "WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS) OR c.year in ('Swap','theme') order by c.year,c.name ASC"
    )

    # get column names from cursor.description
    columns = [desc[0] for desc in curs.description]

    gameinfo = {}
    # iterate through each sql result row and add the info in a dictionary
    menuElement = ET.Element("menu")
    for row in curs.fetchall():
        game = row[0]
        gameinfo[game] = {}
        gameElement = ET.SubElement(menuElement, "game", name=game)

        if row[1]:
            gameinfo[game]["description"] = row[1]
            ET.SubElement(gameElement, "description").text = row[1]
        if row[2]:
            gameinfo[game]["cloneof"] = row[2]
            ET.SubElement(gameElement, "cloneof").text = row[2]
        if row[4]:
            gameinfo[game]["year"] = row[4]
            ET.SubElement(gameElement, "year").text = row[4]
        elif row[3]:
            gameinfo[game]["year"] = row[3]
            ET.SubElement(gameElement, "year").text = row[3]
        if row[6] and not row[6]=='0':
            gameinfo[game]["players"] = row[6]
            ET.SubElement(gameElement, "players").text = row[6]
        elif row[5]:
            gameinfo[game]["players"] = row[5]
            ET.SubElement(gameElement, "players").text = row[5]
        if row[7]:
            ctrltype = row[7].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            gameinfo[game]["ctrltype"] = ctrltype
            ET.SubElement(gameElement, "ctrltype").text = ctrltype
        if row[8] and not row[8].lower()=="other":
            gameinfo[game]["manufacturer"] = row[8]
            ET.SubElement(gameElement, "manufacturer").text = row[8]
        elif row[9]:
            gameinfo[game]["manufacturer"] = row[9]
            ET.SubElement(gameElement, "manufacturer").text = row[9]
        if row[10]:
            gameinfo[game]["category"] = row[10]
            ET.SubElement(gameElement, "category").text = row[10]
        if row[3] and not row[3]=='Swap' and not row[3]=='theme':
            if row[11] and (row[11] == "90" or row[11] == "270"):
                gameinfo[game]["orientation"] = "vertical"
                ET.SubElement(gameElement, "orientation").text = "vertical"
            else:
                gameinfo[game]["orientation"] = "horizontal"
                ET.SubElement(gameElement, "orientation").text = "horizontal"
        if row[12]:
            gameinfo[game]["ctrltype2"] = row[12]
            ET.SubElement(gameElement, "ctrltype2").text = row[12]
        if row[13]:
            gameinfo[game]["joyways"] = row[13]
            ET.SubElement(gameElement, "joyways").text = row[13]
        if row[14]:
            gameinfo[game]["buttons"] = row[14]
            ET.SubElement(gameElement, "buttons").text = row[14]

    # iterate through the dictionary and create the xml and csv file
    for key in gameinfo:
        print(key, "->", gameinfo[key])

    # save the .xml
    dom = xml.dom.minidom.parseString(ET.tostring(menuElement))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split("?>")

    with open("gameinfo/MAME.xml", "w") as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()

    print("finito!")
finally:
    curs.close()
    secret.conn.close()
