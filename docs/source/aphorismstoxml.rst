.. aphorismstoxml:

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

    AphorismToXML file_to_analyse
    AphorismToXML file_to_analyse --xml-main-template=xml_main_template.xml
    AphorismToXML directory
    AphorismToXML directory --xml-main-template=xml_main_template.xml

where:

- ``file_to_analyse`` contains the text to transform in XML (TEI compliant)
- ``directory`` is the name of a directory with file(s) to transform in XML
  (TEI compliant).
  All the files will be treated.
- ``--xml-main-template=`` is an option to precise the xml template used for
  the treatment (here ``xml_main_template.xml``)

To see the help ow to use this software::

    AphorismToXML

will give::

    Usage:
            AphorismsToXML <files> [--xml-main-template=<tmpl>]
            AphorismsToXML -h | --help
            AphorismsToXML --version


Example
=======

The user have a file called ``aphorisms.txt`` in the internal format and he want
to convert it in the XML TEI format. The file is locate in a sub-directory
called ``texts``.

::
    .
    └── texts
        └── aphorisms.txt

to achieve the transformation in a terminal::

    > AphorismsToXML texts/aphorisms.txt

or just use the name of the directory (All the files inside it will be treated)::

    > AphorismsToXML texts


If everything is running well the user will not get any message but will come
back to the normal terminal prompt ``>``::

    > AphorismsToXML texts/
    >

if there are a problem an error message will appeared in the terminal::

    >AphorismsToXML texts/
    2017-04-25 11:57:05,389 - hyppocratic - ERROR - N aphorism expected 4, got: 3
    2017-04-25 11:57:05,389 - hyppocratic - ERROR - Missing or problematic aphorism: [2]
    2017-04-25 11:57:05,389 - hyppocratic - ERROR - Error: unable to process "aphorisms.txt", see log file.
    >

In this example, the error message said that the problem is at the aphorism 2.
It can be missing or having other problem to find it. The user interaction is
needed at this stage and he should verify the ``aphorisms.txt`` file.

For both results a logging file will be created in the working directory::

    .
    ├── hyppocratic.log
    ├── texts
       └── aphorisms.txt

If the process is running until the end without any problems, a new directory
will be created in the working directory with the name ``XML``::

    .
    ├── hyppocratic.log
    ├── texts
    │   └── aphorisms.txt
    └── XML
        ├── aphorisms_app.xml
        └── aphorisms_main.xml

Two files are presents inside an app file, which contains the footnotes
informations and the main file which contains the texts and the references
to the footnotes.
