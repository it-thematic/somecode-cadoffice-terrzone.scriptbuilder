from docx import Document
import os
import zipfile

def docx_replace(old_file,new_file,rep):
    zin = zipfile.ZipFile (old_file, 'r')
    zout = zipfile.ZipFile (new_file, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename == 'word/document.xml'):
            res = buffer.decode("utf-8")
            for r in rep:
                res = res.replace(r, rep[r])
            buffer = res.encode("utf-8")
        zout.writestr(item, buffer)
    zout.close()
    zin.close()


def fill_docx(file, path_to_tempalate, path_to_save=os.getcwd(), **kwargs):
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)
    temp = {'number': "{номер}",
            'name': '{наименование}',
            'name_file': '<имя файла>',
            'size': '<размер>'}
    rep = {temp[d]:kwargs[d] for d in temp.keys()}
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
              path_to_tempalate='Заявление в ГКНШаблон.docx',
              path_to_save='stat_docx',
              number='sdf',
              name=33,
              name_file='43',
              size='ee')
