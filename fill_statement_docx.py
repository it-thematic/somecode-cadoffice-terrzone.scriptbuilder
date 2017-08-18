from docx import Document
import os
import zipfile
from lxml import etree
from lxml.etree import QName


def docx_replace(old_file, new_file, rep):
    zin = zipfile.ZipFile(old_file, 'r')
    zout = zipfile.ZipFile(new_file, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            tree = etree.fromstring(buffer)
            ns = tree.nsmap
            it = tree.xpath('//w:r[(preceding-sibling::*/w:t="{") and following-sibling::*/w:t="}"]/w:t', namespaces=ns)
            bracets = tree.xpath('//w:t', namespaces=ns)
            for bracet in bracets:
                if bracet.text in ['{', '}']:
                    print(bracet.text)
                    bracet.text = ''
                    print(bracet.text)
            for i in it:
                if i.text in rep.keys():
                    i.text = rep[i.text]
            buffer = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8')
        zout.writestr(item, buffer)
    zout.close()
    zin.close()


def fill_docx(file, path_to_tempalate, path_to_save=os.getcwd(), **kwargs):
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)
    temp = {'number': "номер",
            'name': 'наименование',
            'name_file': 'имя файла',
            'size': 'размер'}
    rep = {temp[d]: kwargs[d] for d in temp.keys()}
    docx_replace(path_to_tempalate, os.path.join(path_to_save, '{0}.docx'.format(file)), rep=rep)
    # if os.path.exists(path_to_tempalate):
    #     doc = Document(path_to_tempalate)
    #     for i in doc.paragraphs:
    #         for key in temp.keys():
    #             if i.text.find(temp[key]) != -1:
    #                 try:
    #                     s = i.style
    #                     i.text = str(i.text).replace(temp[key], str(kwargs[key]))
    #                     i.style = s
    #                 except KeyError:
    #                     print('Не переданы нужные ключи')
    #     doc.save(os.path.join(path_to_save, '{0}.docx'.format(file)))
    # else:
    #     print('путь до шаблона неверный')


if __name__ == '__main__':
    fill_docx(file='first',
              path_to_tempalate='template-doc/Заявление в ГКНШаблон.docx',
              path_to_save='stat_docx',
              number='sdf',
              name='33',
              name_file='43',
              size='ee')

    # xpath: //w:r[(preceding-sibling::node()/w:t='{' ) and (following-sibling::node()/w:t='}')]/w:t