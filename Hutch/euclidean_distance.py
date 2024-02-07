"""
Program: euclidean_distance.py

Purpose: Takes a file of amino acid coordinates and creates a two-dimensional
         matrix of the Euclidean distance between them.

Input parameters: Amino acid coordinates file
                  Input file delimiter
                  Output file

Outputs: csv file

Execution: python euclidean_distance.py <input file> <input file delimiter>
               <output file>

Notes: This is a refactoring of the Euclidean distance program previously
       written for the Biometrics Core.

       This program requires a virtual environment in order to run.

"""

import click
import numpy
import sys
sys.path.append('/bioinfo/toolbox/lib/python')
from cjm_module_library import read_2x2_add_ambig

@click.command()
@click.argument("infile", type=str)
@click.argument("in_dlm", type=str)
@click.argument("outfile_fp", type=click.File("w"))
def main(infile, in_dlm, outfile_fp):
    """
    \b
    Purpose: Takes a file of amino acid coordinates and creates a two-dimensional
             matrix of the Euclidean distance between them.

    \b
    Input parameters: Amino acid coordinates file
                      Input file delimiter
                      Output file

    \b
    Execution: python euclidean_distance.py <input file> <input file delimiter>
                   <output file>
    NOTE: Do not include the angle brackets with the parameters.

    """

    # Read the input file into a 2x2 table and add rows for the ambiguity codes.
    input_rows = read_2x2_add_ambig(infile, in_dlm)

    # Grab the amino acid and then delete the first row, as we do not need it.
    aa_desig = input_rows[0][0]
    del input_rows[0]

    # Create a list of column headers by popping the first value off of each
    # row.
    column_headers = []
    for row in input_rows:
        column_headers.append(row.pop(0))

    header_line = column_headers.copy()
    header_line.insert(0, aa_desig)

    # Initialize a dictionary to hold the z values for each amino acid.
    amino_acids = {}

    # Populate the amino acid dictionary. The values are read from the file as
    # strings, so convert them to floats.
    for x in range(len(input_rows)):
        float_row = [float(zv) for zv in input_rows[x]]
        amino_acids[column_headers[x]] = float_row
 
    # Initialize the output matrix and insert the column headers.
    ed_matrix = []
    ed_matrix.append(header_line)

    # Create an outer loop of the column headers to set up the first vector.
    for ol in column_headers:
        new_row = []
        new_row.append(ol)

        # Convert the dictionary list into an array in order to use numpy
        # functions.
        z1 = numpy.asarray(amino_acids[ol])

        # Create an inner loop to do the Euclidean distance calculation.
        for il in column_headers:
            # Convert the inner loop dictionary list into an array.
            z2 = numpy.asarray(amino_acids[il])

            # Calculate the distance.
            dist = numpy.linalg.norm(z1-z2)
            new_row.append("%.2f" % dist)

        # Append the new row to the output matrix.
        ed_matrix.append(new_row)

    # Write out the matrix.
    for row in ed_matrix:
        for column in range(len(row)):
            outfile_fp.write(row[column])
            if column == len(row) - 1:
                outfile_fp.write("\n")
            else:
                outfile_fp.write(",")

if __name__ == "__main__":
    main()
