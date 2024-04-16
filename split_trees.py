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


## ARGPARSING ##
parser = argparse.ArgumentParser(
					prog = 'split_trees',
					description = 'Split trees uses RDataFrames to create '\
                    +'downsampled files. Unless events is given, it takes '\
                    +'10% of the existing file.',
					epilog = 'Warning: this code should be used after all '\
					+'trees have been combined!')
parser.add_argument('rootfile', # positional argument
					help='ROOT file to split to something smaller.')
parser.add_argument('--savestring', dest='savestring', action='store',
					default=None, type=str,
					help='Add additional information to saved file name. '\
					+'Ignored if --filename is given.')
parser.add_argument('--savefolder', dest='savefolder', action='store',
					default=None, type=str,
					help='Folder to place the smaller trees. The default is '\
					+'to create /downsampled_trees/ in the rootfile directory.')
parser.add_argument('--treename', dest='treename', action='store',
					default=None, type=str,
					help='Name to save output tree as. Default is \'tree\'.')
parser.add_argument('--filename', dest='filename', action='store',
					default=None, type=str,
					help='Name to save the split file as.')
parser.add_argument('--events', dest='events', action='store',
					default=None, type=int,
					help='Number events to downsample to.')
parser.add_argument('--multithreading', default=True,
                    action=argparse.BooleanOptionalAction,
                    help='Use ROOT multithreading. '\
                    +'WARNING: Will shuffle contents if enabled.')
parser.add_argument('--CPUS', action='store',
                    type=int, default=8,
                    help='Number of CPUS, maximum 10 for now.')

# argparsing
args = parser.parse_intermixed_args()

rfilename = args.rootfile
Savestring = args.savestring
SaveFolder = args.savefolder
NewFileName = args.filename
TreeName = args.treename
Events = args.events
MultiThreading = args.multithreading
CPUS = args.CPUS

ParentDir = Path(rfilename).parent
RootFile_lone = Path(rfilename).name

if MultiThreading:
    ROOT.EnableImplicitMT(CPUS)

if SaveFolder is None:
	
	SaveFolder = str(ParentDir)+'/downsampled_trees/'

	if not os.path.exists('{}'.format(SaveFolder)):
		print('Folder:')
		print('{}'.format(SaveFolder))
		print('does not exist ==> creating folder!\n')
		os.system('mkdir -p {}'.format(SaveFolder))
else:
	if not os.path.exists('{}'.format(SaveFolder)):
		raise ValueError('{} does not exist.'.format(SaveFolder))
	if SaveFolder[-1] != '/':
		SaveFolder += '/'
	print('Saving file(s) to {}'.format(SaveFolder))


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
if NewFileName is None:
	if Savestring is None:
		NewFileName = '{}{}'.format(SaveFolder,
			RootFile_lone).replace(
			'.root', '_downsampled_{}.root'.format(Events))
	else:
		NewFileName = '{}{}'.format(SaveFolder,
			RootFile_lone).replace(
			'.root', '_downsampled_{}-{}.root'.format(Events, Savestring))
else:
	NewFileName = '{}{}'.format(SaveFolder, NewFileName)
	if not '.root' in NewFileName:
		NewFileName += '.root'

if TreeName is None:
	TreeName = 'tree'

df = ROOT.RDataFrame(TreeName, rfilename)
print('saving to: {}\n'.format(NewFileName))

if not MultiThreading:
    df.Range(Events).Snapshot(TreeName, NewFileName)
    print('\n       done!\n')
else:
    df = df.Filter('rdfentry_<={}'.format(Events))
    df.Snapshot(TreeName, NewFileName)
    print('\n       done!\n')

