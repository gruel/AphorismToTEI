.. aphorismstotei:

#####################################
Python module usage and documentation
#####################################

Usage
=====

The expected way of using the module is via the process_text_files(…)
function which attempts to process all files with the .txt extension
within a specified directory. Input arguments for this function are:

1. text_folder - the folder containing the text file

2. template_file - the name of the XML template file

::

    AphorismToTEI file_to_analyse
    AphorismToTEI file_to_analyse --xml_template=xml_template.txt
    AphorismToTEI directory
    AphorismToTEI directory --xml_template=xml_template.txt

where:

- ``file_to_analyse`` contains the text to transform in XML (TEI compliant)
- ``directory`` is the name of a directory with file(s) to transform in XML
  (TEI compliant).
  All the files will be treated.
- ``--xml_template=`` is an option to precise the xml template used for
  the treatment (here ``xml_template.txt``)

To see the help ow to use this software::

    AphorismToTEI

will give::

    Usage:
            AphorismsToTEI <files> [--xml_template=<tmpl>]
            AphorismsToTEI -h | --help
            AphorismsToTEI --version

