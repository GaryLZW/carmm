#IMPORTS

def test_phonon_analysis():

    from ase.build import bulk
    from carmm.phonon.post_process import get_band_conf, get_thermal_conf, generate_phonon_data, phonon_data_to_csv
    from ase.io import read
    import os
    
    example_path = 'data/phonon_workflow'

    atoms = read(f'{example_path}/geometry_eq.in')
    get_band_conf(atoms, path=example_path)
    get_thermal_conf(path=example_path)

    assert (os.path.exists(f'{example_path}/band.conf'))
    assert (os.path.exists(f'{example_path}/thermal.conf'))
    # generate_phonon_data(path=example_path)
    # phonon_data_to_csv(band_data=True, path=example_path)

test_phonon_analysis()
