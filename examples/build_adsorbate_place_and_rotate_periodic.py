#!/usr/bin/env python3

"""
Example script showing how to add a hydrogen to a periodic
zeolite then add and rotate an ethanol molecule to the desired position.
"""

def test_adsorbate_placer_periodic():
    from ase.io import read
    from ase.build import molecule
    import numpy as np
    from carmm.build.adsorbate_placer import RotationBox
    from ase import Atoms

    for cutoff_mult in [1.2]:

        mth = molecule('CH3CH2OH')
        site = read("data/CHA_unitcell/CHA.cif")

        h_atom = Atoms('H', positions=[(0, 0, 0)])

        site[104].symbol = "Al"
        site[104].number = 13

        h_placed = RotationBox(h_atom, site, 0, 47, 1.0, lps=2, lp_idx=1)
        h_placed.place_adsorbate()

        mth_placed = RotationBox(mth, h_placed.ads_and_site, 2, -1, 1.5, lps=1, cutoff_mult=cutoff_mult)
        mth_placed.place_adsorbate()

        mth_placed.rotate([0, 0, 0])

        comp_pos1 = np.array([-0.56302228,       1.60628513,       4.60411466])
        comp_pos2 = np.array([-0.00420942,       3.08117121,       6.36584055])
        error_pos1 = np.linalg.norm(comp_pos1 - mth_placed.atoms_ads.positions[0], axis=-1)
        error_pos2 = np.linalg.norm(comp_pos2 - mth_placed.atoms_ads.positions[2], axis=-1)

        assert np.isclose(error_pos1, 0, rtol=0, atol=1e-06), f"Error = {error_pos1}"
        assert np.isclose(error_pos2, 0, rtol=0, atol=1e-06), f"Error = {error_pos2}"

        from ase.visualize import view
        view(mth_placed.ads_and_site)

test_adsorbate_placer_periodic()
