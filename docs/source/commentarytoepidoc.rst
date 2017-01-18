.. _commentarytoepidoc:

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

3. n_offset - the number of offsets to use when inserting XML in
   the <body> element (default is 0)

4. offset_size -the number of space characters for each XML offset
   (default value is 4)

Code description
================

Additional functions:

1. process_file – called by process_text_files to process a single text file
	
2. save_error – called by process_file to output error messages to file

3. test_footnotes – called by process_file to test the footnotes for errors

4. get_next_non_empty_line – called by process_file to get the
   next line containing text

5. process_references – called by process_file to process generate
   XML for references from a single line of commentary text
       
6. process_footnotes – called by process_file to process footnote
   symbols and generate XML from a single line of commentary text
       
7. process_omission – called by process_footnotes to generate XML
   for an omission
   
8. process_addition – called by process_footnotes to generate XML
   for an addition
   
9. process_correxi – called by process_footnotes to generate XML
   for a correxi

10. process_conieci – called by process_footnotes to generate XML
    for a conieci

11. process_standard_variant – called by process_footnotes to
    generate XML for a standard variation

The file driver.py demonstrates how to use the module

