# -*- coding: utf-8 -*-

import copy
import os
import glob
import subprocess
import bots.botslib as botslib
import bots.botsglobal as botsglobal
import bots.inmessage as inmessage
import bots.outmessage as outmessage


def comparenode(node1, node2org):
    node2 = copy.deepcopy(node2org)
    if node1.record is not None and node2.record is None:
        print('node2 is "None"')
        return False
    if node1.record is None and node2.record is not None:
        print('node1 is "None"')
        return False
    return comparenodecore(node1, node2)


def comparenodecore(node1, node2):
    if node1.record is None and node2.record is None:
        pass
    else:
        for key, value in node1.record.items():
            if key not in node2.record:
                print('key not in node2', key, value)
                return False
            elif node2.record[key] != value:
                print('unequal attr', key, value, node2.record[key])
                return False
        for key, value in node2.record.items():
            if key not in node1.record:
                print('key not in node1', key, value)
                return False
            elif node1.record[key] != value:
                print('unequal attr', key, value, node1.record[key])
                return False
    if len(node1.children) != len(node2.children):
        print('number of children not equal')
        return False
    for child1 in node1.children:
        for i, child2 in enumerate(node2.children):
            if child1.record['BOTSID'] == child2.record['BOTSID']:
                if comparenodecore(child1, child2) is not True:
                    return False
                del node2.children[i:i+1]
                break
        else:
            print('Found no matching record in node2 for', child1.record)
            return False
    return True


def readfilelines(bestand):
    fp = open(bestand, 'rU')
    terug = fp.readlines()
    fp.close()
    return terug


def readfile(bestand):
    fp = open(bestand, 'rU')
    terug = fp.read()
    fp.close()
    return terug


def readwrite(filenamein='', filenameout='', **args):
    inn = inmessage.parse_edi_file(filename=filenamein, **args)
    inn.checkforerrorlist()
    # make outmessage object
    out = outmessage.outmessage_init(filename=filenameout, divtext='', topartner='', **args)
    out.checkforerrorlist()
    assert hasattr(inn, 'root')
    assert hasattr(out, 'root')
    out.root = inn.root
    out.writeall()


def getdirbysize(path):
    ''' read files in directory path, return as a sorted list. '''
    lijst = getdir(path)
    lijst.sort(key=lambda s: os.path.getsize(s))
    return lijst


def getdir(path):
    ''' read files in directory path, return incl length. '''
    return [f for f in glob.glob(path) if os.path.isfile(f)]


def getreportlastrun():
    for row in botslib.query(
        '''SELECT * FROM report
         ORDER BY idta DESC'''
     ):
        return row
    raise Exception('no report')


def geterrorlastrun():
    for row in botslib.query(
        '''SELECT * FROM filereport
           ORDER BY idta DESC'''
    ):
        return row['errortext']
    raise Exception('no filereport')


def getlastta(status):
    for row in botslib.query(
        '''SELECT * FROM ta
            WHERE status=%(status)s
            ORDER BY idta DESC''',
        {'status': status}
    ):
        return row
    raise Exception('no ta')


def comparedicts(dict1, dict2):
    for key, value in dict1.items():
        assert value == dict2[str(key)], 'error comparing "%s": should be %s but is %s (in db),' % (key, value, dict2[key])


def removeWS(string):
    return ' '.join(string.split())


def RunTestCompareResults(command, comparedict):
    # run bots
    assert not subprocess.call(command), 'error running command: "%s"' % ' '.join(map(str, command))
    botsglobal.db.commit()

    # check report
    comparedicts(comparedict, getreportlastrun())