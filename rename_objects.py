#!/bin/bash
#!/cvmfs/sft.cern.ch/lcg/views/LCG_101_ATLAS_26/x86_64-centos7-gcc11-opt/bin/python

'''
Script to quickly investigate root file content using the pyROOT interface
Additionally there are collections of functions which may be useful to 
import to other scripts
author: Russell Bate
email: russell.bate@cern.ch, russellbate@phas.ubc.ca
'''

import argparse, sys, os
import ROOT
from pathlib import Path

r21_extras = ['jetTileScinMax', 'pt',  'RunNumber',   
'eventNumber',  'phi', 'eta']
r21_branches = ['jettiming', 'jetHECFrac', 'jetHECQuality', 'jetEMFrac',
'jetJVT', 'jetLArQuality', 'jetNegativeE', 'normjetAverageLArQF', 'jetNtrk',
'jetFracSamplingMax']
r22_branches = ['Timing', 'HECFrac', 'HECQuality', 'EMFrac', 'Jvt',
'LArQuality', 'NegativeE', 'normAverageLArQF', 'NumTrkPt500PV',
'FracSamplingMax']
r22_extras = ['BchCorrCell',
'E', 'AverageLArQF', 'N90Constituents', 'LArBadHVEnergyFrac',
'LArBadHVNCell', 'ChargedFraction', 'OotFracClusters5',
'OotFracClusters10', 'LeadingClusterPt', 'LeadingClusterSecondLambda',
'LeadingClusterCenterLambda', 'LeadingClusterSecondR',
'CentroidR', 'LowEtConstituentsFrac', 'GhostMuonSegmentCount',
'Width', 'NumTrkPt1000PV', 'SumPtTrkPt1000PV', 'TrackWidthPt1000PV',
 'SumPtTrkPt500PV', 'TrackWidthPt500PV', 'JVFPV',
'JvtJvfcorr', 'JvtRpt',  'NPV']
same_branches = ['pt', 'phi', 'eta']
event_branches = ['RunNumber', 'eventNumber']


## FUNCTIONS ##
def open_rfile(rfilename):
	''' Handles error if opening fails (In python OSError) 
	returns None if ROOT cannot open the file. '''
	try:
		f = ROOT.TFile.Open(rfilename)
		return f
	except OSError as ose:
		print('Caught OSError: \n{} \n'.format(ose))
		return None

## ARGPARSING ##
parser = argparse.ArgumentParser(
					prog = 'rename_objects', #epilog = ''
					description = 'Create new snapshot with .') 
parser.add_argument('rootfile', # positional argument
					help='ROOT file to change.')
parser.add_argument('--verbose', action='store_true',
					help='ROOT file to change.')
parser.add_argument('--r21-to-r22', dest='r21tor22', action='store_true',
					help='Default naming convention for Athena release 21 \
					jets to release 22.')
parser.add_argument('--leading', dest='leading', action='store_true',
					help='Use flag if naming convention uses trailing 0 to \
					indicate the leading jet.')
parser.add_argument('--subleading', dest='subleading', action='store_true',
					help='Use flag if naming convention uses trailing 1 to \
					indicate the sub-leading jet.')
tree_group = parser.add_argument_group('tree_group')
tree_group.add_argument('--tree-name', dest='tree_name', action='store',
					default='tree', type=str,
					help='Name of which tree to inspect.')
tree_group.add_argument('--list-aliases', dest='list_aliases',
					action='store_true',
					help='List existing aliases for the tree.')
tree_group.add_argument('--old-branches', dest='old_branches', action='store',
					type=str, nargs='+',
					help='Names of branches to change to.')
tree_group.add_argument('--new-branches', dest='new_branches', action='store',
					type=str, nargs='+',
					help='Names of branches to change to.')
args = parser.parse_intermixed_args()

TreeName = args.tree_name
Verbose = args.verbose
RootFile = args.rootfile
R21toR22 = args.r21tor22
Leading = args.leading
SubLeading = args.subleading
OldBranches = args.old_branches
NewBranches = args.new_branches
ListAliases = args.list_aliases

							##############
							## BRANCHES ##
							##############
#=============================================================================#
if R21toR22:
	OldBranches = r21_branches
	NewBranches = r22_branches

if Leading and not SubLeading:
	r21_leading_branches = []
	r22_leading_branches = []
	new_same_branches = []

	for i, branch in enumerate(OldBranches):
		r21_leading_branches.append(branch + '0')
	OldBranches = r21_leading_branches

	for i, branch in enumerate(NewBranches):
		r22_leading_branches.append(branch + '0')
	NewBranches = r22_leading_branches

	for i, branch in enumerate(same_branches):
		new_same_branches.append(branch + '0')
	same_branches = new_same_branches

elif SubLeading and not Leading:
	r21_subleading_branches = []
	r22_subleading_branches = []
	new_same_branches = []

	for i, branch in enumerate(OldBranches):
		r21_subleading_branches.append(branch + '1')
	OldBranches = r21_subleading_branches

	for i, branch in enumerate(NewBranches):
		r22_subleading_branches.append(branch + '1')
	NewBranches = r22_subleading_branches

	for i, branch in enumerate(same_branches):
		new_same_branches.append(branch + '1')
	same_branches = new_same_branches

elif Leading and SubLeading:
	r21_leading_branches = []
	r21_subleading_branches = []
	r22_leading_branches = []
	r22_subleading_branches = []
	new_subleading_branches = []
	new_leading_branches = []

	for i, branch in enumerate(OldBranches):
		r21_leading_branches.append(branch + '0')
		r21_subleading_branches.append(branch + '1')
	OldBranches = r21_leading_branches + r21_subleading_branches

	for i, branch in enumerate(NewBranches):
		r22_leading_branches.append(branch + '0')
		r22_subleading_branches.append(branch + '1')
	NewBranches = r22_leading_branches + r22_subleading_branches

	for i, branch in enumerate(same_branches):
		new_leading_branches.append(branch + '0')
		new_subleading_branches.append(branch + '1')

	same_branches = new_leading_branches + new_subleading_branches

if R21toR22:
	inclusive_branches = same_branches + OldBranches + event_branches
else:
	inclusive_branches = OldBranches
#=============================================================================#


## MAIN ##
print('\n'+'-'*80)
print('-- Changing Branches For: {}'.format(RootFile))
print('-'*80+'\n')

TFile = open_rfile(RootFile)
if TFile is None:
	sys.exit('\nCannot open TFile, exiting program..\n')
RootFileName = Path(RootFile).name
RootFileParent = Path(RootFile).parent


## Catch for treename
if len(TreeName.split('/')) > 2:
	raise ValueError('Nesting of trees beyond depth of 2 not supported'\
		+' (yet): {}.'.format(Treename))

## Open Tree ##
try:
	if '/' in TreeName:
		TDirectory = TFile.GetKey(TreeName.split('/')[0]).ReadObj()
		Tree = TDirectory.GetKey(TreeName.split('/')[1]).ReadObj()
	else:
		Tree = TFile.GetKey("{}".format(TreeName)).ReadObj()
	file_branchnames = []
	Branches = Tree.GetListOfBranches()

	if Verbose:
		print('Number of branches in file: {}\n'.format(len(Branches)))
		for branch in Branches:
			file_branchnames.append(str(branch.GetFullName()))
			print('    {}'.format(file_branchnames[-1]))
	else:
		for branch in Branches:
			file_branchnames.append(str(branch.GetFullName()))

except ReferenceError as re:
	print('TFile.GetKey({})'.format(TreeName))
	print('Returned a null pointer. Tree with name {}'.format(TreeName))
	print('does not exist in file {}\n'.format(RootFileName))
	sys.exit()


							###################
							## COPY BRANCHES ##
							###################
#=============================================================================#
leftover_branches = []
for filebranch in file_branchnames:
	FoundBranch = False
	for branch in inclusive_branches:
		if branch == filebranch:
			FoundBranch = True
			break
	if FoundBranch == False:
		leftover_branches.append(filebranch)
#=============================================================================#

print('\n'+'-'*54)
print('-- Creating Copy Trees with the following variables --')
print('-'*54)
print(' .. loading dataframe ..')
df = ROOT.RDataFrame(Tree)
branches_not_in = []
save_cols = []

print('\n -- changes')
for oldbranch, newbranch in zip(OldBranches, NewBranches):
	if not oldbranch in file_branchnames:
		branches_not_in.append(oldbranch)
		continue
	print('	{:25s} ==> {}'.format(oldbranch, newbranch))
	save_cols.append(newbranch)
	df = df.Define(newbranch, oldbranch)

print('\n -- copying branches')
for branch in same_branches:
	save_cols.append(branch)
	print('	{}'.format(branch))

print('\n -- left over branches not copied')
for branch in leftover_branches:
	print('	{}'.format(branch))

print('\n -- branches not in original tree')
for branch in branches_not_in:
	print('	{}'.format(branch))

NewRootFileName = RootFile.replace('.root', '')
NewRootFileName += '_NewBranches.root'
print('\nSaving new tree to: {}'.format(NewRootFileName))

usr_input = input('\nWould you like to continue? (y/n)\n')
if usr_input != 'y':
	sys.exit('\nExiting early.\n')

df.Snapshot(TreeName, NewRootFileName, save_cols)
print('\nFinished saving copy.\n')

