import os
import configparser
import sqlite3
import pandas as pd



def get_vnstat_conf():
    configpath = ''
    if os.path.isfile(os.path.expanduser('~/.vnstatrc')):
        configpath = os.path.expanduser('~/.vnstatrc')
        #print('if', configpath)
    else:
        configpath = './vnstat.conf'
        print('using the config in this dir ', configpath)

    #configpath = './vnstat.conf'

    parser = configparser.ConfigParser(comment_prefixes='#', delimiters=' ', interpolation=configparser.ExtendedInterpolation())
    parser.optionxform = str

    parser.read(configpath)
    return parser


def get_db_loc():
    configdata = get_vnstat_conf()
    
    #print(configdata.sections())

    db_loc = configdata.get('vnstat', 'DatabaseDir')
    db_loc = (db_loc.strip('"') + '/vnstat.db')

    #print('Using the database at :', db_loc)
    #db_loc = ('./vnstat.db')

    return db_loc
    

def get_data(params, interf='wlan0'):
    if interf == 'All':
        interf = getinterfaces()
    else:
        interf = [interf]



    db_loc = get_db_loc()

    conn = sqlite3.connect(db_loc)
    
    data = pd.read_sql_query(f"SELECT * from {params}", conn)
    iface = pd.read_sql_query("SELECT * FROM interface", conn)
    pd.options.display.float_format = "{:,.2f}".format

    data['rx'] = data['rx'] / 1024 ** 2
    data['tx'] = data['tx'] / 1024 ** 2

    data['total'] = (data['rx'] + data['tx'])
    data['interface'] = data.interface.replace(iface.set_index('id')['name'])
   
    data.columns = ['id', 'Interface', 'Date', 'Download', 'Upload', 'Total']

    conn.close

    data = data.loc[data['Interface'].isin(interf)]
    #print(data)

    return data


def getinterfaces():
    interface_list = []

    db_loc = get_db_loc()
    conn = sqlite3.connect(db_loc)
    
    iface = pd.read_sql_query("SELECT * FROM interface", conn)

    conn.close

    interface_list = iface['name'].tolist()
    #print(interface_list)

    return interface_list

#get_data('day', 'All')

default_conf = {
    'vnstat': {
                'Interface': '""',
                'DatabaseDir': '"/var/lib/vnstat"',
                'Locale': '"-"',
                'DayFormat': '"%Y-%m-%d"',
                'MonthFormat': '"%Y-%m"',
                'TopFormat': '"%Y-%m-%d"',
                'RXCharacter': '"%"',
                'TXCharacter': '":"',
                'RXHourCharacter': '"r"',
                'TXHourCharacter': '"t"',
                'UnitMode': '0',
                'RateUnit': '1',
                'RateUnitMode': '1',
                'OutputStyle': '3',
                'DefaultDecimals': '2',
                'HourlyDecimals': '1',
                'HourlySectionStyle': '2',
                'Sampletime': '5',
                'QueryMode': '0',
                'List5Mins': '24',
                'ListHours': '24',
                'ListDays': '30',
                'ListMonths': '12',
                'ListYears': '0',
                'ListTop': '10'},
    'vnstatd': {
                'DaemonUser': '""',
                'DaemonGroup': '""',
                'BandwidthDetection': '1',
                'MaxBandwidth': '1000',
                '5MinuteHours': '-1',
                'HourlyDays': '-1',
                'DailyDays': '-1',
                'MonthlyMonths': '-1',
                'YearlyYears': '-1',
                'TopDayEntries': '-1',
                'UpdateInterval': '20',
                'PollInterval': '5',
                'SaveInterval': '5',
                'OfflineSaveInterval': '30',
                'MonthRotate': '1',
                'MonthRotateAffectsYears': '0',
                'CheckDiskSpace': '1',
                'BootVariation': '15',
                'TrafficlessEntries': '1',
                'TimeSyncWait': '5',
                'BandwidthDetectionInterval': '5',
                'SaveOnStatusChange': '1',
                'UseLogging': '2',
                'CreateDirs': '1',
                'UpdateFileOwner': '1',
                'LogFile': '"/var/log/vnstat/vnstat.log"',
                'PidFile': '"/run/vnstat/vnstat.pid"',
                '64bitInterfaceCounters': '-2',
                'DatabaseWriteAheadLogging': '0',
                'DatabaseSynchronous': '-1'},
    'vnstati': {
                'HeaderFormat': '"%Y-%m-%d %H:%M"',
                'HourlyRate': '1',
                'SummaryRate': '1',
                'TransparentBg': '0',
                'CBackground': '"FFFFFF"',
                'CEdge': '"AEAEAE"',
                'CHeader': '"606060"',
                'CHeaderTitle': '"FFFFFF"',
                'CHeaderDate': '"FFFFFF"',
                'CText': '"000000"',
                'CLine': '"B0B0B0"',
                'CLineL': '"-"',
                'CRx': '"92CF00"',
                'CTx': '"606060"',
                'CRxD': '"-"',
                'CTxD': '"-"'}}


