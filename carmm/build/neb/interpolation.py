def check_interpolation(initial, final, n_max, interpolation="linear", verbose=True, save=True):
    '''
    Interpolates the provided geometries with n_max total images
    and checks whether any bond lengths are below sane defaults.
    Saves the interpolation in interpolation.traj

    Parameters:

    initial: Atoms object or string
        Starting geometry for interpolation.
    final: Atoms object or string
        End point geometry for interpolation
    n_max: integer
        Desired total number of images for the interpolation
        including start and end point.
    interpolation: string
        "linear" or "idpp". First better for error identification, latter for
        use in NEB calculation
    verbose: boolean
        If verbose output of information is required
    save: boolean
        Whether to save the trajectory for transfer on to an NEB calculation
    '''

    from ase.neb import NEB
    from carmm.analyse.bonds import search_abnormal_bonds
    from ase.io.trajectory import Trajectory
    from ase.io import read

    # Pre-requirements
    if not isinstance(n_max, int):
        raise ValueError
        print("Max number of images must be an integer.")

    # Make a band consisting of 10 images:
    images = [initial]
    images += [initial.copy() for i in range(n_max - 2)]
    images += [final]
    neb = NEB(images)
    # Interpolate linearly the potisions of the middle images:
    neb.interpolate(interpolation, apply_constraint=True)

    # TODO: Tidy up this horrible mix of if statements.
    if save:
        t = Trajectory('interpolation.traj', 'w')

    flag = True
    for i in range(0, n_max):
        if verbose:
            print("Assessing image", str(i + 1) + '.')
        updated_flag = search_abnormal_bonds(images[i], verbose)
        if save:
            t.write(images[i])
        if (not updated_flag):
            flag = updated_flag

    if save:
        t.close()

    return flag


"""
Functions to add images to a given interpolation, or remove images from an interpolation
"""


def add_images_to_path(path, insertion_start, n_images_add=1, write_to_file=True):
    """
    Add images between two neighbouring images in a given path. The new images are added based on linear interpolation.
    This may be useful when restart a neb calculation with more images from a path that is optimized to some extent.

    :param path: a list of atoms objects, a path, e.g. a neb path
    :param insertion_start: int, index of the starting image for insertion (start from 0)
    :param n_images_add: int, number of additional images you want to add
    :param write_to_file: boolean, whether to save the new path to a traj file "new_path.traj"
    :return: a list of atoms objects, the new path with added images
    """
    from ase.neb import interpolate
    from ase.io.trajectory import Trajectory
    from ase import Atoms

    if type(path[0]) is Atoms:
        if sum(path[0].pbc) > 0:
            mic = True
        else:
            mic = False
    else:
        raise TypeError("Your path[0] seems not to be an Atoms object.")

    insertion_end = insertion_start + 1

    added_images = [path[insertion_start]]
    added_images += [path[insertion_start].copy()] * n_images_add
    added_images += [path[insertion_end]]

    interpolate(added_images, mic)

    new_path = [path[i].copy() for i in range(insertion_start)]
    new_path += [image.copy() for image in added_images] + [path[i].copy() for i in range(insertion_end + 1, len(path))]

    if write_to_file:
        new_path_traj = Trajectory('new_path.traj', 'w')
        for image in new_path:
            new_path_traj.write(image)
        new_path_traj.close()

    return new_path


def remove_one_image_from_path(path, index, write_to_file=True):
    """
    Remove an image from a given path.
    :param path: a list of atoms objects, a path, e.g. a neb path
    :param index: the index of image to be removed
    :param write_to_file: verbose: boolean, whether to save the new path to a traj file "new_path.traj"
    :return: a list of atoms objects, the new path without the discarded image
    """
    from ase.io.trajectory import Trajectory
    del path[index]

    if write_to_file:
        new_path_traj = Trajectory('new_path.traj', 'w')
        for image in path:
            new_path_traj.write(image)
        new_path_traj.close()

    return path
