#!/usr/bin/env python3

"""
Program: template_tools.py

Purpose: Functions used by the template generation programs

"""

import os
import pandas as pd

def template_excel(workbook_name, template_df, dictionary_df, values_df):
    """
    Function: template_excel

    Purpose: Write an Excel workbook containing the following worksheets:
             - "Template": worksheet with column names to be used for
                           entering data
             - "Dictionary": worksheet with the definitions of the columns in
                             the "Template" worksheet
             - "Values": worksheet with any controlled vocabulary lists used
                         for columns in the "Template" worksheet

    Arguments:
        workbook_name: Name of the workbook to output
        template_df - An empty pandas dataframe with the column names being
                      the desired template columns
        dictionary_df - A pandas dataframe containing the definition
                        information for each column in the template
        values_df - A pandas dataframe of the values lists used by columns
                    in the template
    """
    workbook_writer = pd.ExcelWriter(workbook_name, engine="xlsxwriter")

    # Create a template worksheet.
    template_df.to_excel(workbook_writer, index=False, sheet_name="Template")

    # Create a dictionary worksheet
    dictionary_df.to_excel(workbook_writer, index=False, sheet_name="Dictionary")

    # Create a values worksheet
    values_df.to_excel(workbook_writer, index=False, sheet_name="Values")

    workbook_writer.save()


def template_csv(template_file_name, template_df, dictionary_df, values_df):
    """
    Function: template_csv

    Purpose: Write csv files as follows:
             - <file name>_template.csv: template file with column names to be
                   used for entering data
             - <file name>_dictionary.csv: file with the definitions of the
                   columns in the "_template" file
             - <file name>_Values: file with any controlled vocabulary lists
                   used for columns in the "_template" file

    Arguments:
        template_file_name: Name of the template file to output. The dictionary
                            and values files will append "_dictionary" and
                            "_values", respectively, after the file name and
                            before the ".csv" extension.
        template_df - An empty pandas dataframe with the column names being
                      the desired template columns
        dictionary_df - A pandas dataframe containing the definition
                        information for each column in the template
        values_df - A pandas dataframe of the values lists used by columns
                    in the template
    """
    base_file_name, base_file_ext = os.path.splitext(template_file_name)
    dictionary_file_name = (base_file_name + "_dictionary" +
                            base_file_ext)
    values_file_name = (base_file_name + "_values" + base_file_ext)

    # Create a template file.
    with open(template_file_name, "w") as template_file:
        template_df.to_csv(template_file, index=False)

    # Create a dictionary file
    with open(dictionary_file_name, "w") as dictionary_file:
        dictionary_df.to_csv(dictionary_file, index=False)

    # Create a values file
    with open(values_file_name, "w") as values_file:
        values_df.to_csv(values_file, index=False)
