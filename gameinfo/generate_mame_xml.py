import secret
import xml.etree.cElementTree as ET
import xml.dom.minidom

m_encoding = "UTF-8"

try:
    curs = secret.conn.cursor()
    curs.execute(
        "select c.name, c.description, m.cloneof, c.year, m.year, c.players, m.players, c.ctrltype, c.manufacturer, m.manufacturer, r.category, m.rotate, m.type, m.ways, m.buttons "
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
            ET.SubElement(game, "cloneof").text = row[2]
        if row[4]:
            ET.SubElement(game, "year").text = row[4]
        elif row[3]:
            ET.SubElement(game, "year").text = row[3]
        if row[6]:
            ET.SubElement(game, "players").text = row[6]
        elif row[5]:
            ET.SubElement(game, "players").text = row[5]
        if row[7]:
            ET.SubElement(game, "ctrltype").text = (
                row[7].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            )
        if row[8] and not row[8].lower()=="other":
            ET.SubElement(game, "manufacturer").text = row[8]
        elif row[9]:
            ET.SubElement(game, "manufacturer").text = row[9]
        if row[10]:
            ET.SubElement(game, "category").text = row[10]
        if row[3] and not row[3]=='Swap' and not row[3]=='theme':
            if row[11] and (row[11] == "90" or row[11] == "270"):
                ET.SubElement(game, "orientation").text = "vertical"
            else:
                ET.SubElement(game, "orientation").text = "horizontal"
        if row[12]:
            ET.SubElement(game, "ctrltype2").text = row[12]
        if row[13]:
            ET.SubElement(game, "joyways").text = row[13]
        if row[14]:
            ET.SubElement(game, "buttons").text = row[14]

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
