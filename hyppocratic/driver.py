# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 14:14:17 2015

@author: mcbicjb2
"""

from importlib import reload

try:
    from hyppocratic import CommentaryToEpidoc
except ImportError:
    import CommentaryToEpidoc

# We need to reload if the package code has been modified
reload(CommentaryToEpidoc)


def main():
    # Call ArabicToXML.process_text_files with the following arguements
    # 1st - the folder containing the text file
    # 2nd - the name of the XML template file
    # 3rd - the number of offsets to use when adding XML to the <body> element
    # 4th - the number of space characters to use for each XML offset

    location_of_files = "./TextFiles"
    template_file = "xml_template.txt"
    n_offsets = 3
    n_space = 4

    CommentaryToEpidoc.process_text_files(location_of_files,
                                          template_file,
                                          n_offsets,
                                          n_space)

    print("Finished")

if __name__ == '__main__':
    main()
