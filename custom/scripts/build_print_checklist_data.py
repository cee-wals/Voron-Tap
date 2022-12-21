#!/usr/bin/env python3
"""
    Tools for building Voron tap 3D Printed part checklist.
"""
import csv
import os
import re

FNAME_FILTER = [".DS_Store"]
COLORS = ["Black", "Red", "Opaque", "Clear"]

def part_cat_name_bldr(fpath):
    fpath = fpath.replace('[a]_','').replace('[o]_','').replace('[c]_','').replace("_", "-")
    fpath = re.sub('[_|\-]x(\d)', '', fpath)

    fparts = fpath.split(os.sep)
    category = fparts[0]
    group = '/'.join(fparts[1:-1])
    part = os.path.splitext(fparts[-1])[0]

    return category, group, part

def resolve_color(part_fname):
    if part_fname.startswith('[a]'):
        color = COLORS[1]
    elif part_fname.startswith('[o]'):
        color = COLORS[2]
    elif part_fname.startswith('[c]'):
        color = COLORS[3]
    else:
        color = COLORS[0]

    return color

def record_builder(fpath):
    """
    Part name format
        Derived from STL file name

    Record format:
        category
        part group
        part name
        quantity
        color
        status
        quality
        required
        build Mod
        STL File
        filament
    """
    fparts = fpath.split(os.sep)
    part_fname = fparts[-1]

    category, group, name = part_cat_name_bldr(fpath)

    color = resolve_color(part_fname)

    quantity = re.findall('[_|\-]x(\d)', part_fname)
    if quantity:
        quantity = int(quantity[0])
    else:
        quantity = 1

    status = "Not Printed"
    quality = ""
    filament = "Prusament ASA"
    required = "YES"
    build_mod = "NO"

    """
    # Mark non-require or parts to exclude
    for filter in ['CW1_SB_Parts']:     # Filtered during file tree walk
        if filter in fpath:
            quality = 'N/A'
            status = 'DO NOT PRINT'
            required = "NO"
            quantity = 0
    if 'Printheads' in group:       # We are using the "phaetus_rapido" printhead
        printhead = fpath.split('/')[-2]
        if printhead in ["phaetus_bmo","phaetus_bms","phaetus_dragon","revo_micro","revo_six_and_v6","revo_voron"]:
            quality = 'N/A'
            status = 'DO NOT PRINT'
            required = "NO"
            quantity = 0
    """
    #return f"{category},{group},{name},{color},{status},{quality},{required},{build_mod},{fpath},{filament}"
    return [category,group,name,quantity,color,status,quality,required,build_mod,fpath,filament]

def do_include_stl(root, fname):
    """
        Returns True if the STL @ "{root}/{fname}" is to be includes. Return False if the STL should be excluded.
        Printhead config:
            - phaetus_rapido
            - clockwork 2 version parts
    """
    # Only include the phaetus-rapido STLs
    if 'Printheads' in root:
        printhead = root.split('/')[-1]
        if printhead in ["phaetus_bmo","phaetus_bms","phaetus_dragon","revo_micro","revo_six_and_v6","revo_voron"]:
            return False

    # Only include STL files and the clockwork2 parts
    return fname.endswith('.stl') and 'cw1' not in fname and 'CW1_SB_Parts' not in root

def build_part_list(fpath: str = "/Users/cwilder/Documents/3D Printing/cee-wals/voron-tap/STLs"):
    """
    Usage:
        data = build_part_list()
    """
    os.chdir(fpath)
    data = list()
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk("."):
        for fname in files:
            if do_include_stl(root, fname):
                fpath = os.path.join(root[2:], fname)
                data.append(record_builder(fpath))
    return data

def create_csv_file(data, fname:str = '/Users/cwilder/Documents/3D Printing/cee-wals/voron-tap/custom/scripts/voron_tap_part_checklist_data.csv'):
    """
    usage:
        data = build_part_list("/Users/cwilder/Documents/3D Printing/cee-wals/voron-tap/STLs")
        create_csv_file(data, '/Users/cwilder/Documents/3D Printing/cee-wals/voron-tap/custom/scripts/voron_tap_part_checklist_data.csv')
    """
    with open(fname, 'w') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data)

def get_categories():
    """
    Usage:
        cats, sub_cats = get_categories()
    """
    cats = set()
    sub_cats = set()
    for root, dirs, files in os.walk('.'):
        fpath = root[2:]
        fparts = fpath.split(os.sep)
        if fparts[0]:
            if len(fparts) == 1:
                cats.add(fparts[0])
            else:
                sub_cats.add('/'.join(fparts))
    return list(cats), list(sub_cats)
