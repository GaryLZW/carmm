#/usr/bin/env python3

#IMPORTS

from ase.build import bulk
import sys
from carmm.phonon.pre_process import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories
# sys.path.append("C:\Users\akash\OneDrive - Cardiff University\Desktop\phonon_workflow")
# from pre_process import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories


crys = bulk('Al', 'fcc', a=4.121, cubic=True)

det, supercells = make_displaced_supercells(crys, [1,1,1], 0.01)
moments, charges = get_charges_and_moments(det,crys)
creating_files_and_directories(supercells, charges, moments)
