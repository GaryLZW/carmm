#/usr/bin/env python3

#IMPORTS


# sys.path.append("C:\Users\akash\OneDrive - Cardiff University\Desktop\phonon_workflow")
# from pre_process import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories

def test_generate_displaced_structures():
    from ase.build import bulk
    import sys
    from carmm.phonon.pre_process import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories
    import os
    crys = bulk('Al', 'fcc', a=4.121, cubic=True)

    example_path = 'data/phonon_workflow'

    det, supercells = make_displaced_supercells(crys, [1,1,1], 0.01, path=example_path)

    assert (os.path.exists(f'{example_path}/geometry_eq.in'))
    assert (os.path.exists(f'{example_path}/phonopy_disp.yaml'))
    # moments, charges = get_charges_and_moments(det,crys)
    # creating_files_and_directories(supercells, charges, moments)

test_generate_displaced_structures()
