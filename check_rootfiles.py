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
					prog = 'check_rootfiles', #epilog = ''
					description = 'Helpful root utilities with the pyROOT '\
					+'interface. Also contains useful functions.') 
parser.add_argument('rootfile', # positional argument
					help='ROOT file to investigate.')
parser.add_argument('--interactive', dest='interactive', action='store_true',
					default=False,
					help='Prompts for user input.')
parser.add_argument('--list-content', dest='list_content', action='store_true',
					default=False,
					help='Show all content within root file.')
parser.add_argument('--full-inspect', dest='inspect',
					action='store_true',
					help='Calls inspect_rootfile function. Unfinished.')

tree_group = parser.add_argument_group('tree_group')

tree_group.add_argument('--show-branches', dest='show_branches', action='store_true',
					default=False,
					help='Show branches in tree. Can specify tree name.')
tree_group.add_argument('--get-nevents', dest='get_nevents', action='store_true',
					default=False,
					help='Simply get the number of events in the tree.')
tree_group.add_argument('--tree-name', dest='tree_name', action='store',
					default='tree', type=str,
					help='Name of which tree to inspect.')

hist_group = parser.add_argument_group('hist_group')
hist_group.add_argument('--draw-histogram', dest='check_histogram',
					action='store_true',
					help='Draws given histogram. Unfinished.')
hist_group.add_argument('--hist-name', dest='hist_name', action='store',
					default=None, type=str,
					help='Name of histogram to draw. Unfinished.')
hist_group.add_argument('--save-hist', dest='save_hist', action='store_true',
					default=False,
					help='Save drawn histogram. Unfinished.')

args = parser.parse_intermixed_args()

Interactive = args.interactive
ListContent = args.list_content
Inspect = args.inspect
ShowBranches = args.show_branches
TreeName = args.tree_name
CheckHistogram = args.check_histogram
HistName = args.hist_name
SaveHist = args.save_hist
RootFile = args.rootfile
GetNEvents = args.get_nevents

## MAIN ##
print('\n'+'-'*80)
print('-- Inspecting ROOT file: {}'.format(RootFile))
print('-'*80+'\n')


TFile = open_rfile(RootFile)
if TFile is None:
	sys.exit('\nCannot open TFile, exiting program..\n')
RootFileName = Path(RootFile).name
RootFileParent = Path(RootFile).parent

def print_obj_info(obj, nspc=4):
	print(' '*nspc+'Object: {}'.format(obj.ClassName()))
	print(' '*nspc+'Title: {}'.format(obj.GetTitle()))
	print(' '*nspc+'Name: {}'.format(obj.GetName()))
	print(' '*nspc+'Size: {} (NBytes)'.format(key.GetNbytes()))
	return None

def inspect_keys(keylist, nspc=4):
	print(' '*nspc+'Listing content of keys')
	for j, key in enumerate(keylist):
		obj = key.ReadObj()
		print_obj_info(obj, nspc=nspc)
	return None

key_list = TFile.GetListOfKeys()

if ListContent:
	print('Listing content:')
	print('Number of objects in file: {}'.format(len(key_list)))

	for j, key in enumerate(key_list):
		obj = key.ReadObj()
		print('\nkey: {}'.format(j))
		print_obj_info(obj, nspc=4)
		if obj.ClassName() == 'TDirectoryFile':
			inspect_keys(obj.GetListOfKeys(), nspc=6)
	print()
		
if ShowBranches:
	print('Showing Branches for tree name: {}'.format(TreeName))
	
	if len(TreeName.split('/')) > 2:
		raise ValueError('Nesting of trees beyond depth of 2 not supported'\
			+' (yet): {}.'.format(Treename))
	
	try:
		if '/' in TreeName:
			TDirectory = TFile.GetKey(TreeName.split('/')[0]).ReadObj()
			Tree = TDirectory.GetKey(TreeName.split('/')[1]).ReadObj()
		else:
			Tree = TFile.GetKey("{}".format(TreeName)).ReadObj()
		Branches = Tree.GetListOfBranches()
		print('Number of branches in file: {}\n'.format(len(Branches)))
		for branch in Branches:
			print('    {}'.format(branch.GetFullName()))
		print()

	except ReferenceError as re:
		print('TFile.GetKey({})'.format(TreeName))
		print('Returned a null pointer. Tree with name {}'.format(TreeName))
		print('does not exist in file {}\n'.format(RootFileName))

if GetNEvents:
	print('Showing number of events for tree name: {}'.format(TreeName))

	if len(TreeName.split('/')) > 2:
		raise ValueError('Nesting of trees beyond depth of 2 not supported'\
			+' (yet): {}.'.format(Treename))

	try:
		if '/' in TreeName:
			TDirectory = TFile.GetKey(TreeName.split('/')[0]).ReadObj()
			Tree = TDirectory.GetKey(TreeName.split('/')[1]).ReadObj()
		else:
			Tree = TFile.GetKey("{}".format(TreeName)).ReadObj()
		
		Entries = Tree.GetEntries()
		print('Number of entries in file: {}\n'.format(Entries))
	
	except ReferenceError as re:
		print('TFile.GetKey({})'.format(TreeName))
		print('Returned a null pointer. Tree with name {}'.format(TreeName))
		print('does not exist in file {}\n'.format(RootFileName))

