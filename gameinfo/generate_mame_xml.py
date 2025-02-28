import secret
import xml.etree.cElementTree as ET
import xml.dom.minidom

m_encoding = "UTF-8"

try:
    curs = secret.conn.cursor()
    curs.execute(
        "select c.name, c.description, c.year, c.players, c.ctrltype, c.manufacturer, m.manufacturer, r.category, m.rotate, m.type, m.ways, m.buttons "
        + "from COINOPS_MAME_FLAT as c "
        + "LEFT OUTER JOIN COINOPS_DELUXE_MAX_ROMS AS r ON c.name = r.file "
        + "LEFT OUTER JOIN REF_MAME_274_FLAT AS m ON c.name = m.name "
        + "WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS) OR c.year in ('Swap','theme') order by c.year,c.name ASC"
    )

    # Get column names from cursor.description
    columns = [desc[0] for desc in curs.description]
    menu = ET.Element("menu")

    # Iterate through each row and create XML elements
    for row in curs.fetchall():
        game = ET.SubElement(menu, "game", name=row[0])
        if row[1]:
            ET.SubElement(game, "description").text = row[1]
        if row[2]:
            ET.SubElement(game, "year").text = row[2]
        if row[3]:
            ET.SubElement(game, "players").text = row[3]
        if row[4]:
            ET.SubElement(game, "ctrltype").text = (
                row[4].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            )
        if row[5] and not row[5].lower()=="other":
            ET.SubElement(game, "manufacturer").text = row[5]
        elif row[6]:
            ET.SubElement(game, "manufacturer").text = row[6]
        if row[7]:
            ET.SubElement(game, "category").text = row[7]
        if row[2] and not row[2]=='Swap' and not row[2]=='theme':
            if row[8] and (row[8] == "90" or row[8] == "270"):
                ET.SubElement(game, "orientation").text = "vertical"
            else:
                ET.SubElement(game, "orientation").text = "horizontal"
        if row[9]:
            ET.SubElement(game, "type").text = row[9]
        if row[10]:
            ET.SubElement(game, "joyways").text = row[10]
        if row[11]:
            ET.SubElement(game, "buttons").text = row[11]

    # save the .xml
    dom = xml.dom.minidom.parseString(ET.tostring(menu))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split("?>")

    with open("gameinfo/MAME.xml", "w") as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()
        
    print("finito!")
finally:
    curs.close()
    secret.conn.close()
