import secret
import xml.etree.cElementTree as ET
import xml.dom.minidom

m_encoding = "UTF-8"

try:
    curs = secret.conn.cursor()
    curs.execute(
        "select c.name,c.description,c.year,c.players,c.ctrltype,c.manufacturer,m.rotate from COINOPS_MAME_FLAT as c LEFT OUTER JOIN REF_MAME_274_FLAT AS m ON m.name = c.name WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS) OR c.year in ('Swap','theme') order by c.year,c.name ASC"
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
            ET.SubElement(game, "ctrltype").text = row[4]
        if row[5]:
            ET.SubElement(game, "manufacturer").text = row[5]
        if row[2] and not row[2]=='Swap' and not row[2]=='theme':
            if row[6] and (row[6] == "90" or row[6] == "270"):
                ET.SubElement(game, "orientation").text = "vertical"
            else:
                ET.SubElement(game, "orientation").text = "horizontal"

    # save the .xml
    dom = xml.dom.minidom.parseString(ET.tostring(menu))
    xml_string = dom.toprettyxml()
    part1, part2 = xml_string.split("?>")

    with open("gameinfo/MAME.xml", "w") as xfile:
        xfile.write(part1 + 'encoding="{}"?>\n'.format(m_encoding) + part2)
        xfile.close()
finally:
    curs.close()
    secret.conn.close()
