import os
import urllib.request
from cgi import valid_boundary
from urllib.parse import quote
import json
from lxml import etree
from lxml.etree import ElementTree, SubElement
import math
import uuid
import datetime
import sys
import shutil
from convert2es import mgisxy2esnode
from getCadDist import CadastralDistrict
from fill_statement_docx import fill_docx
import config
from pathlib import Path

ns_TerritoryToGKN = {
            'xmlns': "urn://x-artefacts-rosreestr-ru/incoming/territory-to-gkn/1.0.4",
            'xmlns_ki3': "urn://x-artefacts-rosreestr-ru/commons/complex-types/cadastral-engineer/4.1.1",
            'xmlns_fio': "urn://x-artefacts-smev-gov-ru/supplementary/commons/1.0.1",
            'xmlns_spat2': "urn://x-artefacts-rosreestr-ru/commons/complex-types/entity-spatial/2.0.1",
            'xmlns_doci2': "urn://x-artefacts-rosreestr-ru/commons/complex-types/document-info/5.0.1",
        }

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


cTerritoryToGKN = config.cTerritoryToGKN
cZoneToGKN = config.cZoneToGKN
cXMLext = config.cXMLext
cTZmask = config.cTZmask
cTempalate_doc = config.cTempalate_doc
cTypeUnit = config.cTypeUnit
cGeopointZacrep = config.cGeopointOpred
cDeltaGeopoint = config.cDeltaGeopoint
cGeopointOpred = config.cGeopointOpred
cTAppliedFiles = config.cTAppliedFiles
cZAppliedFiles = config.cZAppliedFiles


def set_node_value(node, value, attname=None):
    if isinstance(value, tuple):
        if attname:
            node.set(attname, node.get(attname).format(*value))
        else:
            node.text = node.text.format(*value)
    else:
        if attname:
            node.set(attname, node.get(attname).format(value))
        else:
            node.text = node.text.format(value)


def build_territory_to_gkn(data, template_dir, out_dir):
    """
    Формирование документа TerritoryToGKN
    """
    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
    doc_guid = str(uuid.uuid4())
    csr_guid = 'Id'+str(uuid.uuid4())


    #DataManager
    doc_dir = os.path.join(out_dir, data['parent_dir'])
    doc_file = os.path.join(doc_dir, '{0}_{1}{2}'.format(cTerritoryToGKN, doc_guid, cXMLext))
    doc_app = os.path.join(doc_dir, doc_guid)
    shutil.copytree(os.path.join(template_dir, cTerritoryToGKN), doc_app)
    shutil.copyfile(os.path.join(template_dir, cTerritoryToGKN+cXMLext), doc_file)
    # os.rename(os.path.join(doc_dir, cTerritoryToGKN), doc_app)
    # os.rename(os.path.join(doc_dir, cTerritoryToGKN+cXMLext), doc_file)
    for i in cTAppliedFiles:
        shutil.copyfile(os.path.join(os.path.dirname(data['sys_file']), i.format(data['sys_number_for_file'])), os.path.join(doc_app, i.format(data['sys_number_for_file'])))


    #xml data writer
    tree = etree.parse(doc_file, parser)
    root = tree.getroot()

    root.set('GUID', doc_guid)

    set_node_value(root.xpath('//xmlns:AttorneyDocument/xmlns_doci2:AppliedFile', namespaces=ns_TerritoryToGKN)[0],doc_guid,'Name')

    set_node_value(root.xpath('//xmlns:EntitySpatial', namespaces=ns_TerritoryToGKN)[0], csr_guid, 'EntSys')

    set_node_value(root.xpath('//xmlns:Area/xmlns:AreaMeter/xmlns:Area', namespaces=ns_TerritoryToGKN)[0], data['area'])
    value = str(int(round(math.sqrt(int(data['area'])) * float(data['DeltaGeopoint']) * 2, 0)))
    set_node_value(root.xpath('//xmlns:Area/xmlns:AreaMeter/xmlns:Inaccuracy', namespaces=ns_TerritoryToGKN)[0], value)

    set_node_value(root.xpath('//xmlns:CoordSystems/xmlns_spat2:CoordSystem', namespaces=ns_TerritoryToGKN)[0],csr_guid, 'CsId')

    set_node_value(root.xpath('//xmlns:Diagram/xmlns:AppliedFile', namespaces=ns_TerritoryToGKN)[0],
                   value=(doc_guid, data['sys_number']), attname='Name')

    mgisxy2esnode(mgisxyfile=data['sys_file'], es=root.xpath('//xmlns:EntitySpatial', namespaces=ns_TerritoryToGKN)[0],
                  d=data['DeltaGeopoint'], gopr=data['GeopointOpred'])

    etree.ElementTree(root).write(doc_file, pretty_print=True, xml_declaration=True, encoding='utf-8')

    return doc_guid


def build_zone_to_gkn(data, tz_guid, template_dir, out_dir):
    """
        Парсинг по шаблону ZoneToGKN
    """
    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
    doc_guid = str(uuid.uuid4())
    zone_title = 'Охранная зона {0}, адрес (местоположение): {1}'.format(data['name_zone'], data['address'])

    # DataManager
    doc_dir = os.path.join(out_dir, data['parent_dir'])
    doc_file = os.path.join(doc_dir, '{0}_{1}{2}'.format(cZoneToGKN, doc_guid, cXMLext))
    doc_app = os.path.join(doc_dir, doc_guid)
    shutil.copytree(os.path.join(template_dir, cZoneToGKN), doc_app)
    shutil.copyfile(os.path.join(template_dir, cZoneToGKN + cXMLext), doc_file)
    for i in cZAppliedFiles:
        shutil.copyfile(os.path.join(os.path.dirname(data['sys_file']), i.format(data['sys_number_for_file'])),
                        os.path.join(doc_app, i.format(data['sys_number_for_file'])))


    tree = etree.parse(doc_file, parser)
    root = tree.getroot()
    root.set('GUID', doc_guid)
    set_node_value(root.xpath('//xmlns:Title/xmlns_doci2:Name', namespaces=ns_ZoneToGKN)[0], doc_guid)
    set_node_value(root.xpath('//xmlns:Title/xmlns_doci2:Number', namespaces=ns_ZoneToGKN)[0], data['sys_number'])
    set_node_value(root.xpath('//xmlns:Title/xmlns_doci2:Date', namespaces=ns_ZoneToGKN)[0], str(datetime.date.today()))
    for node in root.xpath('//xmlns:Documents/xmlns:Document/xmlns_doci2:AppliedFile', namespaces=ns_ZoneToGKN):
        set_node_value(node, value=(doc_guid, data['sys_number']), attname='Name')
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:CadastralDistrict', namespaces=ns_ZoneToGKN)[0], data['cad_dis'])
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:CodeZoneDoc', namespaces=ns_ZoneToGKN)[0], zone_title)
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:OKATO',
                   namespaces=ns_ZoneToGKN)[0], str(data['okato']))
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:KLADR',
                              namespaces=ns_ZoneToGKN)[0], str(data['kladr']))
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:OKTMO',
                              namespaces=ns_ZoneToGKN)[0], str(data['oktmo']))
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:PostalCode',
                              namespaces=ns_ZoneToGKN)[0], str(data['postal_code']))
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:Region',
                              namespaces=ns_ZoneToGKN)[0], str(data['region']))
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns_zone2:Locations/xmlns_zone2:Location/xmlns_loc3:District',
                              namespaces=ns_ZoneToGKN)[0], str(data['district']), 'Name')

    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns:SpecialZone/xmlns_zone2:ProtectedObject',
                              namespaces=ns_ZoneToGKN)[0], zone_title)
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns:SpecialZone/xmlns:Territory/xmlns_doci2:AppliedFile',
                             namespaces=ns_ZoneToGKN)[0], tz_guid, 'GUID')
    set_node_value(root.xpath('//xmlns:NewZones/xmlns:Zone/xmlns:SpecialZone/xmlns:Territory/xmlns_doci2:AppliedFile',
                              namespaces=ns_ZoneToGKN)[0], tz_guid, 'Name')

    etree.ElementTree(root).write(doc_file, pretty_print=True, xml_declaration=True, encoding='utf-8')

    return doc_guid

# def request_location_data()


def tz_build(input, output, template, fias_service, cd=CadastralDistrict, hierarchy=False):
    """
    Главная функция
    """
    list_dirs = os.listdir(input)
    print(list_dirs)
    if len(list_dirs) > 0:
        for directory in list_dirs:
            try:
                list_files = os.listdir(os.path.join(input, directory))
            except NotADirectoryError:
                continue
            print(list_files)
            if len(list_files) > 0:
                for file in list_files:
                    if file.startswith(cTZmask):
                        data_dict = {}
                        with open(os.path.join(input, directory, file), 'r') as txt:
                            result_directory = output + '\\' + directory
                            # if not os.path.exists(result_directory):
                            #     os.mkdir(result_directory)
                            read_lines = txt.readlines()
                            text_semi_norm_arr = list(map(lambda x: x.replace('\n', ''), read_lines))
                            text_norm_arr = list(map(lambda x: x.replace('\t', ' '), text_semi_norm_arr))

                            # info = text_norm_arr[0].split(' ')
                            data_dict['sys_file'] = os.path.realpath(txt.name)
                            parent_dir = os.path.splitext(file)[0][len(cTZmask):]

                            data_dict['parent_dir'] = parent_dir

                            if hierarchy:
                                data_dict['sys_number_for_file'] = '{0}_КТП_{1}'.format(os.path.split(input)[-1],
                                                                               parent_dir)
                                data_dict['sys_number'] = '{0}/{1}'.format(os.path.split(input)[-1],
                                                                                parent_dir)
                            else:
                                data_dict['sys_number'] = parent_dir
                                data_dict['sys_number_for_file'] = parent_dir

                            data_dict['address'] = text_norm_arr[1]

                            list_district = text_norm_arr[1].split(',')
                            if len(list_district) > 2:
                                data_dict['address_for_request'] = list_district[0].strip()
                                data_dict['district_for_request'] = data_dict['address_for_request'].split(' ')[0]

                            else:
                                print(list_district)
                                data_dict['address_for_request'] = text_norm_arr[1]
                                data_dict['district_for_request'] = text_norm_arr[1].split(',', maxsplit=1)[1].strip().split(' ')[0]

                            data_dict['district'] = text_norm_arr[1].split(',', maxsplit=1)[1].strip()

                            # data_dict['number'] = info[3]
                            data_dict['name_zone'] = text_norm_arr[0]
                            data_dict['file_name'] = str(dir)
                            data_dict['area'] = text_norm_arr[2]
                            data_dict['ordinate'] = [item for item in text_norm_arr[4:]]
                            data_dict['ordinate'].append(text_norm_arr[4])

                            ordinate_data = {}
                            if ordinate_data == {}:
                                data_dict['TypeUnit'] = cTypeUnit
                                data_dict['GeopointZacrep'] = cGeopointZacrep
                                data_dict['DeltaGeopoint'] = cDeltaGeopoint
                                data_dict['GeopointOpred'] = cGeopointOpred

                            # print('data_dict: ', data_dict)

                            """
                                Получение данных из локальной базы базы ФИАС
                            """
                            name_line = data_dict['address_for_request'].replace(',', '').replace(' ', '_')
                            text = quote('{0}'.format(name_line))
                            r = urllib.request.urlopen(fias_service.format(text))
                            data = json.loads(r.read().decode('utf-8'))
                            print(data)
                            data.update(data_dict)
                            print(data['region'], data['district_for_request'])

                            data['cad_dis'] = cd.get_code(data['region'], data['district_for_request'])
                            # data = json.loads('{}')
                            # data.update(data_dict)

                            #TerritoryToGKN
                            tz_guid = build_territory_to_gkn(data=data, template_dir=template, out_dir=output)
                            #ZoneToGKN
                            z_guid = build_zone_to_gkn(data=data, tz_guid=tz_guid, template_dir=template, out_dir=output)

                            # Заполнение DOCX файла
                            zone_title = 'Охранная зона {0}, адрес (местоположение): {1}'.format(data['name_zone'],
                                                                                                 data['address'])
                            fill_docx(file=data['sys_number_for_file'],
                                      path_to_tempalate=os.path.join(template, 'Заявление в ГКН.docx'),
                                      path_to_save=os.path.join(output, data['parent_dir']),
                                      number=str(data['sys_number']),
                                      name=str(zone_title),
                                      name_file='ZoneToGKN_{0}.zip'.format(z_guid),
                                      date=str(datetime.date.today().strftime('%d.%m.%Y')),
                                      size='<size>')
                            print(zone_title)


def tz_build_run(input, output, template, fias_service, cd=CadastralDistrict, hierarchy=False):
    if not os.path.exists(output):
        os.mkdir(output)
    if hierarchy:
        list_dirs = os.listdir(input)
        print(list_dirs)
        if len(list_dirs) > 0:
            for dirs in list_dirs:
                input_dirs = os.path.join(input, dirs)
                output_dirs = os.path.join(output, dirs)
                print(input_dirs, output_dirs)
                print(dirs)
                tz_build(input_dirs, output_dirs, template, fias_service, cd=cd, hierarchy=True)
    else:
        tz_build(input, output, template, fias_service, cd=cd, hierarchy=False)

if __name__ == '__main__':
    tz_build_run(input='исх данные\\',
                 output='исх данные\\!result\\',
                 template=cTempalate_doc,
                 fias_service='http://192.168.2.76:8000/api/addr_obj/{0}/',
                 cd=CadastralDistrict('CadastralDistrict\\'),
                 hierarchy=False)






