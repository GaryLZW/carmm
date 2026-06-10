
def read_bader_critic2(file, verbose=True):
    """
    Read Bader charge from critic2 output.
    
    Return: list
            [(index, symbol, charge), ...]

    """
    with open(file, "r") as fp:
        flag = False
        lines = []
        for line in fp:
            if line == "* Integrated atomic properties\n":
                flag = True
            if line.startswith("---------------"):
                break
            if flag:
                lines.append(line)
    if verbose:
        print(len(lines), " lines of output")

    first_output_line = lines.index("* Integrated atomic properties\n") + 4
    #Store data in tuples (index, symbol, charge)
    if verbose:
        print("Store data in tuples (index, symbol, charge)")
        title = first_output_line - 1
        print("title line:", lines[title])
        print("first output:", lines[first_output_line])

    charge_list = []
    this_index = first_output_line
    while(this_index < len(lines) ):
        this_atom_info = (lines[this_index].split()[0], lines[this_index].split()[3], lines[this_index].split()[7])
        charge_list.append(this_atom_info)
        #print(this_index, this_atom_info)
        this_index += 1
    if verbose:
          print("last output:", charge_list[-1])

    return charge_list

