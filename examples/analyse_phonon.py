#IMPORTS

from ase.build import bulk
from carmm.phonon.post_process import get_band_conf, get_thermal_conf, generate_phonon_data, phonon_data_to_csv
# from post_process import get_band_conf, get_thermal_conf, generate_phonon_data, phonon_data_to_csv
from ase.io import read

atoms = read('geometry_eq.in')
get_band_conf(atoms)
get_thermal_conf()
generate_phonon_data()
phonon_data_to_csv(band_data=True)
