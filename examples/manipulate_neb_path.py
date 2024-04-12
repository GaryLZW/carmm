from ase.io import read
from carmm.build.neb.interpolation import add_images_to_path, remove_one_image_from_path

path2traj = 'data/CO2_Cu_disso'
last_path = read(path2traj + '/' + '100-ML-NEB.traj@:')
# Add one image between image 2 and image 3
one_added = add_images_to_path(last_path, 2, n_images_add=1, write_to_file=False)
# Add another image between image 4 and image 5
# Default values: n_images_add=1, write_to_file=True
two_added = add_images_to_path(one_added, 4, write_to_file=False)

dist_C_O = [image.get_distance(63, 64) for image in two_added]
assert dist_C_O[3] == 2.2494491758440005
assert dist_C_O[5] == 2.4733595132791972


# Remove the 6th image
one_removed = remove_one_image_from_path(last_path, 6, write_to_file=False)

dist_C_O = [image.get_distance(63, 64) for image in one_removed]
assert dist_C_O[6] == 3.3176373697539745

