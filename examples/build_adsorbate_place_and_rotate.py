#!/usr/bin/env python3

"""
Example script showing how to add a hydrogen to a zeolite cluster,
then add and rotate an ethanol molecule to the desired position.
"""

def test_adsorbate_placer():
    from ase.io import read
    from ase.build import molecule
    import numpy as np
    from carmm.build.adsorbate_placer import RotationBox
    from ase import Atoms

    idx = 0
    for cutoff_mult in [1, 1.2]:

        idx += 1
        mth = molecule('CH3CH2OH')
        site = read("data/H-Y_cluster/H-Y_cluster.xyz")

        h_atom = Atoms('H', positions=[(0, 0, 0)])

        h_placed = RotationBox(h_atom, site, 0, 0, 1.0, lps=2)
        h_placed.place_adsorbate()

        mth_placed = RotationBox(mth, h_placed.ads_and_site, 2, -1, 1.5, lps=1, cutoff_mult=cutoff_mult)
        mth_placed.place_adsorbate()

        mth_placed.rotate([-45, 0, -45])

        if idx==1:
            comp_pos1 = np.array([17.64422484,       3.85498689,      -0.54203256])
            comp_pos2 = np.array([19.50003770,       2.89160039,       0.56208881])
        if idx==2:
            comp_pos1 = np.array([19.74553637,       5.73078939,       1.80099570])
            comp_pos2 = np.array([19.77143688,       3.47775953,       1.08376180])

        error_pos1 = np.linalg.norm(comp_pos1 - mth_placed.atoms_ads.positions[0], axis=-1)
        error_pos2 = np.linalg.norm(comp_pos2 - mth_placed.atoms_ads.positions[2], axis=-1)

        assert np.isclose(error_pos1, 0, rtol=0, atol=1e-06), f"Error = {error_pos1}"
        assert np.isclose(error_pos2, 0, rtol=0, atol=1e-06), f"Error = {error_pos2}"

        from ase.visualize import view
        view(mth_placed.ads_and_site)

test_adsorbate_placer()
