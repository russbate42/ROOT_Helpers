#!/bin/bash
#!/cvmfs/sft.cern.ch/lcg/views/LCG_101_ATLAS_26/x86_64-centos7-gcc11-opt/bin/python

'''
Script to create smaller trees using Snapshot
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca
'''

import ROOT
import argparse, sys, os
import numpy as np
from pathlib import Path

print('\n' + '='*25)
print('== DOWNSIZE ROOT FILES ==')
print('='*25 + '\n')

## FUNCTIONS ##
def open_rfile(rfilename):
	success = True
	try:
		f = ROOT.TFile.Open(rfilename)
		return f
	except OSError as ose:
		print('Caught OSError: \n{} \n'.format(ose))
		return None

def inspect_rootfile(rootfile, keys=True, obj=True, rootmap=True):
	TFile = open_rfile(rootfile)

	print('\n'+'-'*80)
	print('-- Inspecting ROOT file: {}'.format(rootfile))
	print('-'*80+'\n')

	print(' -- key list -- ')
	if keys:
		key_list = TFile.GetListOfKeys()
		print('key list: {}'.format(key_list))
		print('length of key list: {}'.format(len(key_list)))
		print('key list type: {}\n'.format(type(key_list)))

		if obj:
			print(' -- showing keys and their respective objects --')
		else:
			print(' -- showing keys in list --')

		for key in key_list:
			print('\nkey: {}'.format(key))
			print('key type: {}'.format(type(key)))
			print('key title: {}'.format(key.GetTitle()))
			print('key size: {} (NBytes)'.format(key.GetNbytes()))

			if obj:
				obj = key.ReadObj()
				print('object: {}'.format(obj))
				print('object type: {}'.format(type(obj)))

	if rootmap:
		print('\n -- Printing ->Map() function --')
		TFile.Map()

	print('\n'+'-'*80+'\n')
	return None

## ARGPARSING ##
parser = argparse.ArgumentParser(
					prog = 'split_trees',
					description = '.',
					epilog = 'Warning: this code should be used after all '\
					+'trees have been combined!')
parser.add_argument('rootfile', # positional argument
					help='ROOT file to split to something smaller.')
parser.add_argument('--savestring', dest='savestring', action='store',
					default=None, type=str,
					help='Add additional information to saved file name.')
parser.add_argument('--savefolder', dest='savefolder', action='store',
					default='downsampled_trees/', type=str,
					help='Folder to place the smaller trees.')
parser.add_argument('--treename', dest='treename', action='store',
					default=None, type=str,
					help='Name to save output tree as.')
parser.add_argument('--events', dest='events', action='store',
					default=None, type=int,
					help='Number events to downsample to.')
parser.add_argument('--inspect-rootfile', dest='inspect',
					action='store_true',
					help='Temporary functionality to inspect root files. \
					May be removed in the future.')

# argparsing
args = parser.parse_intermixed_args()

rfilename = args.rootfile
Savestring = args.savestring
SaveFolder = args.savefolder
TreeName = args.treename
Events = args.events
Inspect = args.inspect

ParentDir = Path(rfilename).parent
RootFile_lone = Path(rfilename).name

if SaveFolder != 'downsampled_trees/':
	if SaveFolder[-1] != '/':
		SaveFolder += '/'

if not os.path.exists('{}/{}'.format(ParentDir, SaveFolder)):
	print('Folder:')
	print('{}/{}'.format(ParentDir, SaveFolder))
	print('does not exist ==> creating folder!\n')
	os.system('mkdir -p {}/{}'.format(ParentDir, SaveFolder))

#=========================#
## Inspect File Contents ##
#=========================#
if Inspect:
	inspect_rootfile(rfilename, rootmap=False)

# check if root file exists
try:
	try:
		f = ROOT.TFile.Open(rfilename)
	except OSError as ose:
		print('Caught system error:\n')
		print(ose)
		sys.exit('\n\n -- Exiting.\n')
	# check how many events are in rootfile

	try:
		tree = f.GetKey('tree').ReadObj()
		NinTree = tree.GetEntriesFast()
	
		if not Events is None:
			if Events >= NinTree:
				raise ValueError(
					'Requested too many events, '\
					+'total of {} in file.\n'.format(NinTree))

		# maybe do some user input here
		else:
			print('No number of events given, defaulting to 10%.')
			Events = int(.1 * NinTree)

	except KeyError as ke:
		print('No key with Key Name: \'tree\' exists!')
		print('Try --inspect-rootfile for list of keys.\n')
		raise ke
	f.Close()

except OSError as ose:
	print('Cannot open root file: \n{}\n'.format(rfilename)\
		+'{} \n'.format(ose))

# pull root file name from rfile
if TreeName is None:
	TreeName = '{}/{}{}'.format(ParentDir, SaveFolder,
		RootFile_lone).replace(
		'.root', '_downsampled_{}_.root'.format(Events))
else:
	TreeName = '{}/{}{}'.format(ParentDir, SaveFolder, TreeName)
	if not 'root' in TreeName:
		TreeName += '.root'

df = ROOT.RDataFrame("tree", rfilename)
print('saving to: {}\n'.format(TreeName))

df.Range(Events).Snapshot('tree', TreeName)

print('\n	 done!\n')

