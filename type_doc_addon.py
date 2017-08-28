import lxml.etree as etree
from config_types import config_RT


ns_ZoneToGKN = {
            'xmlns': "urn://x-artefacts-rosreestr-ru/incoming/zone-to-gkn/5.0.8",
            'xmlns_loc3': "urn://x-artefacts-rosreestr-ru/commons/complex-types/address-input/6.0.1",
            'xmlns_org3': "urn://x-artefacts-rosreestr-ru/commons/complex-types/organization/4.0.1",
            'xmlns_zone2': "urn://x-artefacts-rosreestr-ru/commons/complex-types/zone/4.2.2",
            'xmlns_fl3': "urn://x-artefacts-rosreestr-ru/commons/complex-types/person/5.0.2",
            'xmlns_fio': "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1",
            'xmlns_doci2': "urn://x-artefacts-rosreestr-ru/commons/complex-types/document-info/5.0.1",
            'xmlns_dcl2': "urn://x-artefacts-rosreestr-ru/commons/complex-types/sender/5.0.1",
        }


class AdderDoc:
    def __init__(self, pnode):
        self.xmlName = "Document"
        self.pnode = pnode
        self.xmlNode = None
        self.command = None

    def write(self, command):
        self.command = command
        self.xmlNode = etree.SubElement(self.pnode, "{" + ns_ZoneToGKN['xmlns'] + "}" + self.xmlName)
        if self.command == 'RT':
            return AdderUnderDocRT(self.xmlNode)


class AdderUnderDocRT:
    def __init__(self, pnode):
        self.xmlNames = ['CodeDocument', 'Name', 'Series', 'Number', 'Date', 'IssueOrgan', 'AppliedFile']
        self.pnode = pnode
        self.xmlNode = None
        self.AppliedFile = None

    def write(self, Number, Date, doc_guid):
        self.xmlNames_dict = {'CodeDocument': config_RT.CodeDocument,
                              'Name': config_RT.Name,
                              'Number': Number,
                              'Date': Date,
                              'IssueOrgan': config_RT.IssueOrgan,
                              'AppliedFile': [config_RT.AppliedFile_Kind, config_RT.AppliedFile_Name.format(doc_guid)]}
        for xmlName in self.xmlNames:
            if xmlName == 'AppliedFile':
                self.xmlNode = etree.SubElement(self.pnode, '{' + ns_ZoneToGKN['xmlns_doci2'] + '}' + xmlName)
                self.xmlNode.set('Kind', self.xmlNames_dict[xmlName][0])
                self.xmlNode.set('Name', self.xmlNames_dict[xmlName][1])
            elif xmlName == 'Series':
                self.xmlNode = etree.SubElement(self.pnode, '{' + ns_ZoneToGKN['xmlns_doci2'] + '}' + xmlName)
            else:
                self.xmlNode = etree.SubElement(self.pnode, '{' + ns_ZoneToGKN['xmlns_doci2'] + '}' + xmlName)
                self.xmlNode.text = self.xmlNames_dict[xmlName]


# Определяем добавление документа RT в xml
def addDoc(file_txt, elem, command, doc_guid):
    f = open(file_txt, 'r')
    text = f.readlines()
    if command == 'RT':
        number = text[0].strip('\n')
        print(text[1])
        date_arr = text[1].split('.')
        date_arr.reverse()
        date = '-'.join(date_arr)
        doc = AdderDoc(elem)
        type_doc = doc.write(command)
        type_doc.write(Number=number, Date=date, doc_guid=doc_guid)



