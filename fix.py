from xml.dom import minidom

xmldoc = minidom.parse("hello2.svg")

tags = xmldoc.getElementsByTagName("svg")

tags[0].attributes["version"] = "1.0"
tags[0].attributes["xmlns"] = "http://www.w3.org/2000/svg"

with open("hello2.svg", "w") as f:
    xmldoc.writexml(f)