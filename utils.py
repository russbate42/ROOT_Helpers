import ROOT
import numpy as np

def print_obj_info(obj, key, nspc=4):
    print(' '*nspc+'Object: {}'.format(obj.ClassName()))
    print(' '*nspc+'Title: {}'.format(obj.GetTitle()))
    print(' '*nspc+'Name: {}'.format(obj.GetName()))
    print(' '*nspc+'Size: {} (NBytes)'.format(key.GetNbytes()))
    return None

def inspect_keys(keylist, nspc=4):
    print(' '*nspc+'Listing content of keys')
    for j, key in enumerate(keylist):
        obj = key.ReadObj()
        print_obj_info(obj, key, nspc=nspc)
    return None

def return_tdir(keys):
    tdir = None
    for key in keys:
        obj = key.ReadObj()
        if obj.ClassName() == 'TDirectoryFile':
            tdir = obj
        break
    return tdir

