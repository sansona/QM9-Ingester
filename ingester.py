#!/usr/bin/python3

import sys
import os
import json
from collections import OrderedDict

import pandas as pd
from pypif import pif
from pypif.obj import *

#------------------------------------------------------------------------------


def FileToDF(fname):
    '''
    opens .xyz file from QM9 dataset, formats into two dataframes.
    Usage: df, df2_dict = FormatToDF('foo.xyz')
    '''
    # additional rows containing relevant info for vals in form (Symbol:unit)
    var_attributes = OrderedDict([('tag', None), ('A', 'GHz'), ('B', 'GHz'),
                                  ('C', 'GHz'), ('mu', 'D'),
                                  ('alpha', 'a_0^3'), ('e_HOMO', 'Ha'),
                                  ('e_LUMO', 'Ha'), ('e_gap', 'Ha'),
                                  ('R^2', 'a_0^2'), ('zpve', 'Ha'),
                                  ('U_0', 'Ha'), ('U', 'Ha'),
                                  ('H', 'Ha'), ('G', 'Ha'),
                                  ('C_v', 'Cal/(mol*K)')])

    df = pd.read_csv(fname, names=list(var_attributes.keys()), sep='\t')
    # make new df with all additional relevant info about scalar vals
    df2 = pd.DataFrame(dict(scalar_val=df.loc[1],
                            units=list(var_attributes.values()),
                            index=list(var_attributes.keys())))
    df2 = df2.drop(df2.index[0])  # delete tag column

    # df contains all original information in file, df2 is dict containing
    # all info that goes into PIF
    return df, df2.to_dict()


#------------------------------------------------------------------------------


def ParseCompoundName(orig_df):
    '''
    Parse through list of atoms from barebones df to get molecular name. Uses 
    pivot points to retain structural information about compound
    Usage: compound_name = ParseCompoundName(dataframe)
    '''
    num_atoms = int(orig_df.at[0, 'tag'])
    atom_col = list(orig_df['tag'])
    atom_list = atom_col[2:2+num_atoms]

    # make list of idx where atom in list & next atom in list differ
    pivot_idx = [0]  # initialize w/ first pivot point
    for i in range(len(atom_list) - 1):
        if atom_list[i] != atom_list[i+1]:
            pivot_idx.append(i+1)

    # if atom corresponds to pivot point, write atom & count of that atom
    compound_name_list = []
    for i in range(len(atom_list)):
        if i in pivot_idx:
            idx = pivot_idx.index(i)
            compound_name_list.append(atom_list[i])
            try:
                count_atom = pivot_idx[idx+1] - pivot_idx[idx]
            except IndexError:
                count_atom = len(atom_list) - pivot_idx[idx]
            # omit counts of 1 given convention for molecular formulas
            if count_atom != 1:
                compound_name_list.append(str(count_atom))

    compound_name = ''.join(compound_name_list)

    return compound_name


#------------------------------------------------------------------------------

def WritePIF(name_of_compound, info_dict):
    chem_sys = ChemicalSystem()

    properties = []
    for val in info_dict['scalar_val']:
        prop = Property()
        prop.name = val
        prop.scalars = info_dict['scalar_val'][val]
        prop.units = info_dict['units'][val]
        properties.append(prop)

    chem_sys.chemical_formula = name_of_compound
    chem_sys.properties = properties

    return pif.dumps(chem_sys, indent=4)

#------------------------------------------------------------------------------


def Ingester(fname):
    '''
    Reformats .xyz file from QM9 dataset to PIF
    Usage: Ingester('bar.xyz')
    '''
    df, df2 = FileToDF(fname)
    name = ParseCompoundName(df)
    pif = WritePIF(name, df2)
    print(pif)

    with open('test.json', 'w') as f:
        json.dump(pif, f, sort_keys=True)


#------------------------------------------------------------------------------
# if running from command line
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: ./ingester.py foo.xyz')
    elif len(sys.argv) > 2:
        print('Usage: ./ingester.py foo.xyz')
    else:
        Ingester(sys.argv[1])
