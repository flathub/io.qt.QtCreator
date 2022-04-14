#!/usr/bin/env python
import os
from string import Template
import xml.etree.ElementTree as ET

sdks = []

for directory in os.listdir('/app/extensions'):
    if directory.startswith('Qt') and directory[2].isdigit():
        sdks.append(directory)

try:
    expandedPath = os.path.expanduser('~/.var/app/io.qt.QtCreator/config/QtProject/qtcreator/qtversion.xml')
    tree = ET.parse(expandedPath)
    root = tree.getroot()

    # Add section for extension if it does not yet exist
    pathTemplate = Template('/app/extensions/$dir/bin/qmake')
    for sdk in sdks:
        sdkPath = pathTemplate.substitute(dir=sdk)
        exists = False
        dataElemsLen = sum(1 for _ in root.iter('data'))
        for data in root.iter('data'):
            elements = data.findall(".//*[@key='QMakePath']")
            if len(elements) > 0:
                lastElement = data
                if elements[0].text == sdkPath:
                    exists = True
                    break
        if not exists:
            section = ET.Element('data')
            variable = ET.SubElement(section, 'variable')
            variable.text = 'QtVersion.' + str(int(lastElement.find('variable').text[10]) + 1)
            valuemap = ET.SubElement(section, 'valuemap')
            valuemap.set('type', 'QVariantMap')
            idValue = ET.SubElement(valuemap, 'value')
            idValue.set('type', 'int')
            idValue.set('key', 'Id')
            idValue.text = str(int(lastElement.find('.//*[@key="Id"]').text) + 1)
            qmakePathValue = ET.SubElement(valuemap, 'value')
            qmakePathValue.set('type', 'QString')
            qmakePathValue.set('key', 'QMakePath')
            qmakePathValue.text = sdkPath
            qtVersionTypeValue = ET.SubElement(valuemap, 'value')
            qtVersionTypeValue.set('type', 'QString')
            qtVersionTypeValue.set('key', 'QtVersion.Type')
            qtVersionTypeValue.text = 'Qt4ProjectManager.QtVersion.Desktop'
            autodetectionSourceValue = ET.SubElement(valuemap, 'value')
            autodetectionSourceValue.set('type', 'QString')
            autodetectionSourceValue.set('key', 'autodetectionSource')
            isAutodetectedValue = ET.SubElement(valuemap, 'value')
            isAutodetectedValue.set('type', 'bool')
            isAutodetectedValue.set('key', 'isAutodetected')
            isAutodetectedValue.text = 'false'
            root.insert(dataElemsLen - 1, section)

    # Remove sections of uninstalled extensions
    for data in root.iter('data'):
        elements = data.findall(".//*[@key='QMakePath']")
        if len(elements) > 0:
            elText = elements[0].text
            if elText.startswith('/app/extensions/') and elText[16:19] not in sdks:
                root.remove(data)

    tree.write(expandedPath)
except FileNotFoundError:
    print('Could not find qtversion.xml!')

os.system('qtcreator')
