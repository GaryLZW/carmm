def get_sorted_distances(model, atoms_to_include=None):
    '''
    Returns a sorted list of atomic distances in the model, selecting only those atoms of interest
    Current usage is for molecules and periodic solids (through mic).

    Parameters:

    model: Atoms objects
        The model from which the RDF is to be plotted
    atoms_to_include: Integer or List of Integers
        Atoms that you want included in the RDF

    Returns:

    individual_lengths: List of floats
        An sorted list of all lengths of bonds between all atoms in the model


    '''

    # get all distances in the model
    distances = model.get_all_distances(mic=True, vector=False)

    # Define atoms_to_include
    if atoms_to_include is None:
        atoms_to_include = [i for i in range(len(distances))]
    elif isinstance(atoms_to_include, int):
        atoms_to_include = [atoms_to_include]

    individual_lengths = []
    # This should be condensed to one for loop.
    for i in range(len(distances)):
        for j in range(i+1, len(distances[i])):
            # Check if we are on a row/column for an atom we want.
            if i in atoms_to_include or j in atoms_to_include:
                individual_lengths.append(distances[i][j])

    return sorted(individual_lengths)

def analyse_all_bonds(model, verbose=True, abnormal=True):
    '''
    Analyse bonds and return all abnormal bond types and list of these
    TODO: Make this more bullet proof - what happens if abnormal bonds aren't requested.
    A table of bond distance analysis for the supplied model is also possible

    Parameters:

    model: Atoms object
        Structure for which the analysis is to be conducted
    verbose: Boolean
        Determines whether the output should be printed to screen
    abnormal: Boolean
        Collect information about rogue looking bond lengths.
        (Does enabling this by default add a large time overhead?)
    '''

    # set() to ensure unique chemical symbols list
    list_of_symbols = list(set(model.get_chemical_symbols()))
    # Combination as AB = BA for bonds, avoiding redundancy
    from itertools import combinations_with_replacement
    all_bonds = combinations_with_replacement(list_of_symbols, 2)

    # Define lists to collect abnormal observations
    abnormal_bonds = []
    list_of_abnormal_bonds = []

    # Table heading
    if verbose:
        print_bond_table_header()

    from ase.data import chemical_symbols, covalent_radii
    # Iterate over all arrangements of chemical symbols
    for bonds in all_bonds:
        print_AB, AB_Bonds, AB_BondsValues = analyse_bonds(model, bonds[0], bonds[1], verbose=verbose, multirow=True)

        if abnormal and AB_BondsValues is not None:
            sum_of_covalent_radii = covalent_radii[chemical_symbols.index(bonds[0])] + covalent_radii[chemical_symbols.index(bonds[1])]
            abnormal_cutoff = max(0.4, sum_of_covalent_radii*0.75)

            for values in AB_BondsValues:
                abnormal_values = [i for i in values if i < abnormal_cutoff ]
                if len(abnormal_values):
                    abnormal_bonds.append(len(abnormal_values))
                    list_of_abnormal_bonds.append(print_AB)

    # This now returns empty arrays if no abnormal bond checks are done,
    # or if genuinely there are no abnormal bonds.
    return abnormal_bonds, list_of_abnormal_bonds

def analyse_bonds(model, A, B, verbose=True, multirow=False):
    '''
    Check A-B distances present in the model.

    Parameters:
    model: Atoms object
        XXX
    A: string, chemical symbol, e.g. "H"
    B: string, chemical symbol, e.g. "H"
    verbose: Boolean
        Whether to print information to screen
    multirow: Boolean
        Whether we are working with analyse_all_bonds, so the output is multirow,
        or just one specific analysis of a bond, in which case the table header is needed.
    '''

    from ase.geometry.analysis import Analysis
    analysis = Analysis(model)

    print_AB = A + "-" + B
    # Retrieve bonds and values
    AB_Bonds = analysis.get_bonds(A, B)
    if AB_Bonds == [[]]:
        AB_BondsValues = None
    else:
        AB_BondsValues = analysis.get_values(AB_Bonds)

    if verbose and AB_BondsValues is not None:
        if not multirow:
            print_bond_table_header()
        # Table contents
        import numpy as np
        print('{:<8.8s}{:<6.0f}{:>4.6f}{:^12.6f}{:>4.6f}'.format(
            print_AB, len(AB_BondsValues[0]), np.average(AB_BondsValues),
            np.amin(AB_BondsValues), np.amax(AB_BondsValues)))

    return print_AB, AB_Bonds, AB_BondsValues

def search_abnormal_bonds(model, verbose=True):
    '''
    Check all bond lengths in the model for abnormally
    short ones.

    Parameters:
    model: Atoms object or string. If string it will read a file
        in the same folder, e.g. "name.traj"
    '''

    # Abnormality check
    abnormal_bonds, list_of_abnormal_bonds = analyse_all_bonds(model, verbose=verbose, abnormal=True)

    from ase.data import chemical_symbols, covalent_radii
    import numpy as np
    if list_of_abnormal_bonds:
        sums_of_covalent_radii = []
        for i in list_of_abnormal_bonds:
            bond_chem_symbols = i.split("-")
            sums_of_covalent_radii += [covalent_radii[chemical_symbols.index(bond_chem_symbols[0])]
                + covalent_radii[chemical_symbols.index(bond_chem_symbols[1])]]


    # Check against possible covalent radii values averaged * 0.75
    if len(abnormal_bonds) > 0:
        if verbose:
            print("-"*40)
            print("A total of", len(abnormal_bonds),
            "abnormal bond lengths observed (<" + str(max(0.4, np.average(sums_of_covalent_radii)*0.75)) + " A")
            print("Identities:", list_of_abnormal_bonds)
            print("-"*40)
        return False
    else:
        return True

def compare_structures(atoms1, atoms2, label=None):
    '''

    Comparison of two input structures to identify equivalent atoms but incorrect index ordering

    Parameters:

    atoms1: Atoms object or trajectory of individual atoms
        An atoms object
    atoms2: Atoms object or trajectory of individual atoms
        Another atoms object
    label: String of elemental character
        Only necessary to limit search to specific atomic species
    '''
    from math import sqrt

    if len(atoms1) != len(atoms2):
        print("The inputs don't contain the same number of atoms.")
        exit()

    # Configure arrays
    differences = []
    atoms2_indices = []

    # Iterate over indices of all atoms in structure 1 and compare to structure 2.
    for i in range(len(atoms1.positions)):
        xyz = atoms1.positions[i]
        distance_sq = 999999.9
        temp_index = 0
        for j in range(len(atoms2.positions)):
            if atoms1.symbols[i] == atoms2.symbols[j] and (atoms1.symbols[i] == label or label == None):
                temp_distance_sq = ((atoms2.positions[j][0] - xyz[0]) * (atoms2.positions[j][0] - xyz[0])
                                    + (atoms2.positions[j][1] - xyz[1]) * (atoms2.positions[j][1] - xyz[1])
                                    + (atoms2.positions[j][2] - xyz[2]) * (atoms2.positions[j][2] - xyz[2]))

                if distance_sq > temp_distance_sq:
                    distance_sq = temp_distance_sq
                    temp_index = j

        atoms2_indices.append(temp_index)
        differences.append(sqrt(distance_sq))

    return atoms2_indices, differences

def comparing_bonds_lengths(atoms1, atoms2):                                   
    '''                                                                               
description: this function allows to compare difference in bonds lengths between two structures,    
parameters:                                                                           
     atoms1: Atoms object or trajectory of individual atoms                           
     atoms2: a second atom object                                                     
    '''                                                                               
                                                                                      
    import numpy as np                                                                
                                                                                      
    from ase.build import molecule                                                    
    from ase import Atoms                                                             
                                                                                      
                                                                                      
    distances_1 = atoms1.get_all_distances(mic=True, vector=False)                    
    distances_2 = atoms2.get_all_distances(mic=True, vector=False)                    
                                                                                      
    d1=[]                                                                             
    d2=[]                                                                             
                                                                                      
    for i in range(len(distances_1)):                                                 
        for j in range(i+1, len(distances_1[i])):                                     
            d1.append(distances_1[i][j])                                              
            d2.append(distances_2[i][j])                                              
                                                                                      
    diff = np.abs(np.sort(d1) - np.sort(d2))                                          
    return(diff)                                                                      
                                                                                      

def get_indices_of_elements(list_of_symbols, symbol):
    '''

    Check an atoms object for occurences of symbols given and return indices

    Parameters:

    list_of_symbols: List of strings
        Symbols from an atoms object in structural order
    symbol:
        Symbol to search for
    '''

    return [i for i, x in enumerate(list_of_symbols) if x == symbol.capitalize()]

def print_bond_table_header():
    print("-" * 40)
    print('{:<6.5s}{:<6.5s}{:>4.10s}{:^13.10s}{:>4.10s}'.format(
        "Bond", "Count", "Average", "Minimum", "Maximum"))
    print("-" * 40)

def analyse_chelation(atoms, metal, ligand_atom, mult=1):
    '''
    Returns information on the ligands surrounding a metal atom and their chelation type. Currently only works with one metal atom.
    TODO: rework so script can account for multiple separate atoms.

    Parameters:
    atoms: Atoms object
        Input structure from which to calculate molecular information
    Mult: float value
        Multiplier for the bond cutoffs. Set to 1 as default but can be adjusted depending on application
    metal: String
        Metal atom to characterise the coordination environment around
    ligand_atom: String
        Element symbol of the atom coordinating with the metal atom
        TODO: expand this functionality as a list of element symbols.
    '''

    ## Import modules
    from carmm.analyse.bonds import analyse_bonds, analyse_all_bonds
    from ase.neighborlist import NeighborList, get_connectivity_matrix, natural_cutoffs
    from scipy import sparse
    import collections
    from collections import OrderedDict

    ## identifies atoms coordinated to the metal cation
    ligand_coord = analyse_bonds(atoms, metal, ligand_atom, verbose=False)

    ## Defines cutoffs, connectivity matrix for first image.
    cutOff = natural_cutoffs(atoms, mult=mult)
    neighborList = NeighborList(cutOff, skin=0, self_interaction=True, bothways=True)
    neighborList.update(atoms)
    # defines matrix and removes entries from the metal, so the complex is not considered as one molecule.
    matrix = neighborList.get_connectivity_matrix(sparse=False)
    metal_idx = [i for i in range(len(atoms)) if atoms.get_chemical_symbols()[i] == metal] # gets index corresponding to metal atom
    for i in range(len(matrix[0])):
        matrix[metal_idx[0]][i] = 0
        matrix[i][metal_idx[0]] = 0
    n_components, component_list = sparse.csgraph.connected_components(matrix)

    ## gets atoms indexes coordinating to the metal (coord_inx) and the lengths of these bonds (coord_len) as lists
    coord_idx = [ligand_coord[1][0][i][1] for i in range(len(ligand_coord[1][0]))]
    coord_len = ligand_coord[2][0]

    ## gets the molecule numbers corresponding to the atom indices
    molidx = {}
    molIdxs = {}
    for idx in coord_idx:
        molidx[str(idx)] = component_list[idx]

    ## counters the molecules coordinating to the metal atom so we get a dictionary containing the molecules and their chelation type
    counter = collections.Counter([*molidx.values()])
    # converts dictionary into separate lists containing the molecules and ligand chelation types
    molecules = [*counter.keys()]
    chelation_type = [*counter.values()]

    ## for the molecules coordinating to the metal atom, determines their chemical formula.
    molecule_formulas = []
    for idx in molecules:
        index = molecules.index(idx)
        # for said molecule number, obtains all atom indices in said molecule as a list.
        molIdxs[str(idx)] = [i for i in range(len(component_list)) if component_list[i] == molecules[index]]
        # converts the atom indices list to their respective chemical symbols.
        idx_symbols = [atoms.get_chemical_symbols()[i] for i in [*molIdxs.values()][index]]
        # counts the chemical symbols present and returns the molecular formula in Hill notation.
        symbolcount = collections.Counter(idx_symbols)
        ordered = OrderedDict(sorted(symbolcount.items())) # orders keys in c dictionary so they are in alphabetical order

        chemical_formula = ''
        for k, v in ordered.items():
            entry = str(k) + str(v)
            chemical_formula += entry
        molecule_formulas.append(chemical_formula)

    # old_counter = [[*molidx.values()].count(i) for i in [*molidx.values()]]
    bond_info = {'molecules': molecules, 'formula': molecule_formulas, 'chelation': chelation_type}
    return bond_info