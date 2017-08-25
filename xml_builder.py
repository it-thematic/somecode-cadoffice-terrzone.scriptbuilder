import sys
import os
import argparse
from getCadDist import CadastralDistrict
from tz_builder import tz_build_run


def readable_dir(prospective_dir):
    if not os.path.isdir(prospective_dir):
        raise Exception("Ошибка обращения к директории:{0} неверно указан путь".format(prospective_dir))
    if os.access(prospective_dir, os.R_OK):
        return prospective_dir
    else:
        raise Exception("Ошибка обращения к директории:{0} нет доступа".format(prospective_dir))

parser = argparse.ArgumentParser(description='Конструктор XML')
parser.add_argument('-i',
                    dest='input',
                    help='путь к директории с исходными данными',
                    nargs='?',
                    type=readable_dir,
                    )
parser.add_argument('-o',
                    dest='output',
                    help='путь к директории результата',
                    nargs='?',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '!result')
                    )
parser.add_argument('-t',
                    dest='template',
                    help='путь к директории шаблонов',
                    nargs='?',
                    type=readable_dir,
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template-doc')
                    )
parser.add_argument('-f',
                    dest='fias',
                    help='Сервис ФИАС (для определения класс.кодов адреса)',
                    default='http://192.168.2.76:8000/api/addr_obj/{0}/'
                    )
parser.add_argument('-c',
                    dest='cad_dis',
                    help='Директория содержащая коды регионов ',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CadastralDistrict')
                    )
parser.add_argument('-m', '--multi',
                    dest='hierarchy',
                    action='store_true',
                    help='Определение структуры. True, если иерархическая. По умолчанию False'
                    )
parser.add_argument('--TerritoryToGKN',
                    dest='TerritoryToGKN',
                    help='Имя TerritoryToGKN',
                    default='TerritoryToGKN'
                    )
parser.add_argument('--ZoneToGKN',
                    dest='ZoneToGKN',
                    help='Имя ZoneToGKN',
                    default='ZoneToGKN'
                    )
parser.add_argument('--XMLext',
                    dest='XMLext',
                    help='Формат файла для парсинга',
                    default='.xml'
                    )
parser.add_argument('--TZmask',
                    dest='TZmask',
                    help='Маска файла txt',
                    default='__tz_'
                    )
parser.add_argument('--TypeUnit',
                    dest='TypeUnit',
                    help='TypeUnit',
                    default='Точка'
                    )
parser.add_argument('--GeopointZacrep',
                    dest='GeopointZacrep',
                    help='GeopointZacrep',
                    default='Закрепление отсутствует'
                    )
parser.add_argument('--DeltaGeopoint',
                    dest='DeltaGeopoint',
                    help='DeltaGeopoint',
                    default='0.1'
                    )
parser.add_argument('--GeopointOpred',
                    dest='GeopointOpred',
                    help='GeopointOpred',
                    default='692005000000'
                    )
parser.add_argument('--TAppliedFiles',
                    dest='TAppliedFiles',
                    help='TAppliedFiles',
                    nargs='+',
                    default=['{0}_графика.pdf']
                    )
parser.add_argument('--ZAppliedFiles',
                    dest='ZAppliedFiles',
                    help='ZAppliedFiles',
                    nargs='+',
                    default=('{0}.pdf', '3943 балансовая справка.pdf')
                    )

print(parser)
args = parser.parse_args()

if __name__ == '__main__':
    tz_build_run(input=args.input,
                 output=args.output,
                 template=args.template,
                 fias_service=args.fias,
                 TerritoryToGKN=args.TerritoryToGKN,
                 ZoneToGKN=args.ZoneToGKN,
                 XMLext=args.XMLext,
                 TZmask=args.TZmask,
                 TypeUnit=args.TypeUnit,
                 GeopointZacrep=args.GeopointZacrep,
                 DeltaGeopoint=args.DeltaGeopoint,
                 GeopointOpred=args.GeopointOpred,
                 TAppliedFiles=args.TAppliedFiles,
                 ZAppliedFiles=args.ZAppliedFiles,
                 cd=CadastralDistrict(args.cad_dis),
                 hierarchy=args.hierarchy
                 )
