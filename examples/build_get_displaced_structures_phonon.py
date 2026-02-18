#/usr/bin/env python3

#IMPORTS


# sys.path.append("C:\Users\akash\OneDrive - Cardiff University\Desktop\phonon_workflow")
# from pre_process import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories

def test_generate_displaced_structures():
    from ase.build import bulk
    import sys
    from carmm.build.get_displaced_structures_phonon import make_displaced_supercells, get_charges_and_moments, creating_files_and_directories
    import os
    crys = bulk('Al', 'fcc', a=4.121, cubic=True)

    example_path = 'data/phonon_workflow'

    det, supercells = make_displaced_supercells(crys, [1,1,1], 0.01, path=example_path)

    assert (os.path.exists(f'{example_path}/geometry_eq.in'))
    assert (os.path.exists(f'{example_path}/phonopy_disp.yaml'))
    moments, charges = get_charges_and_moments(det,crys)
    creating_files_and_directories(supercells, charges, moments, path=example_path)
    assert (os.path.exists(f'{example_path}/disp-001/geometry.in'))

    # After creating the displaced geometries in seperate folders, you will have to run first-principles calculation
    # in FHI-aims in each of the separate directory to generate a aims.out file in each disp-00n folder
    # the post-process of phonon calculations using phonon_analysis.py script in analyse folder depends on the presence
    # of aims.out file in each of these folders
    #
    # import os
    # for disp in os.listdir(example_path):
    #     if os.path.isdir(f'{example_path}/{disp}'):
    #         atoms = read(f'{example_path}/{disp}/geometry.in')
    #         from carmm.run.aims_calculator import get_aims_calculator
    #         fhi_calc = get_aims_calculator(dimensions=2,...,)
    #         calc = fhi_calc
    #         atoms.set_calculator(calc)
    #         print(f'{defor}, {atoms.get_potential_energy()}')

test_generate_displaced_structures()
