"""
This script tests the following functions from CommentaryToEpidoc.py
1. process_references
2. process_omission
3. process_addition
4. process_correxi
5. process_conieci
6. process_standard_variant
7. process_footnotes

The following functions are not tested
1. get_next_non_empty_line
2. test_footnotes
3. save_error
4. process_file
5. process_text_files
The necessary input and reference files should be in folder test_files, input 
data is in files ending in .in, reference output is in files ending in .ref
"""

###############################################################################
# FUNCTIONS TO DO THE TESTING
###############################################################################

def test_process_references():
    """
Runs the function process_references(...) on the text in 
test_process_references.in, and compares the output against the text in 
test_process_references.ref    
    """
    
    ok = False
    
    # Load text from input file
    with open('./test_files/test_process_references.in','r',encoding="utf-8") as f:
        text_in = f.read()
   
    # Load text from reference file
    with open('./test_files/test_process_references.ref','r',encoding="utf-8") as f:
        text_ref = f.read()
    
    # Run the function with the input
    text_out = CommentaryToEpidoc.process_references(text_in)

    # Test the return value matches the expected output
    if text_out == text_ref:
        ok = True
        print('test_process_references: PASSED')
    else:
        print('test_process_references: FAILED')
        print('return value:')
        print(text_out)
        
    return ok

    
def test_process_omission():
    """
Runs the function process_omission(...) on the text in 
test_process_omission.in, and compare the output against the text in 
test_process_omission.ref    
    """
    
    ok = False
    
    # Load text from input file
    with open('./test_files/test_process_omission.in','r',encoding="utf-8") as f:
        text_in = f.read()
         
    # Load text from reference file
    with open('./test_files/test_process_omission.ref','r',encoding="utf-8") as f:
        text_ref = f.read()
    
    # Run the function with the input
    list_out = []
    CommentaryToEpidoc.process_omission(text_in, list_out)
    
    # Convert the output list to a string with each element on a new line
    text_out = '\n'.join(list_out)

    # Test the return value matches the expected output
    if text_out == text_ref:
        ok = True
        print('test_process_omission: PASSED')
    else:
        print('test_process_omission: FAILED')
        print('return value:')
        print(text_out)
    
    return ok
    
    
def test_process_addition():
    """
Runs the function process_addition(...) on the text in 
test_process_addition.in, and compare the output against the text in 
test_process_addition.ref    
    """
    
    ok = False
    n_test = 3
    
    for test in range(1,n_test+1):
    
        # Load text from input file
        with open('./test_files/test_process_addition' + str(test) + '.in','r',encoding="utf-8") as f:
            text_in = f.read()
            
        # Load text from reference file
        with open('./test_files/test_process_addition' + str(test) + '.ref','r',encoding="utf-8") as f:
            text_ref = f.read()
    
        # Run the function with the input
        list_out = []
        CommentaryToEpidoc.process_addition(text_in, list_out)
    
        # Convert the output list to a string with each element on a new line
        text_out = '\n'.join(list_out)

        # Test the return value matches the expected output
        if text_out == text_ref:
            ok = True
            print('test_process_addition Test ' + str(test) + ': PASSED')
        else:
            ok = False
            print('test_process_addition Test ' + str(test) + ': FAILED')
            print('return value:')
            print(text_out)
    
    return ok
    
def test_process_correxi():
    """
Runs the function process_correxi(...) on the text in 
test_process_correxi.in, and compare the output against the text in 
test_process_correxi.ref    
    """
    
    ok = False
    n_test = 2
    
    for test in range(1,n_test+1):
    
        # Load text from input file
        with open('./test_files/test_process_correxi' + str(test) + '.in','r',encoding="utf-8") as f:
            text_in = f.read()
            
        # Load text from reference file
        with open('./test_files/test_process_correxi' + str(test) + '.ref','r',encoding="utf-8") as f:
            text_ref = f.read()
    
        # Run the function with the input
        list_out = []
        CommentaryToEpidoc.process_correxi(text_in, list_out)
    
        # Convert the output list to a string with each element on a new line
        text_out = '\n'.join(list_out)

        # Test the return value matches the expected output
        if text_out == text_ref:
            ok = True
            print('test_process_correxi Test ' + str(test) + ': PASSED')
        else:
            ok = False
            print('test_process_correxi Test ' + str(test) + ': FAILED')
            print('return value:')
            print(text_out)
    
    return ok
    

def test_process_conieci():
    """
Runs the function process_conieci(...) on the text in 
test_process_conieci.in, and compare the output against the text in 
test_process_conieci.ref    
    """
    
    ok = False
    n_test = 2
    
    for test in range(1,n_test+1):
    
        # Load text from input file
        with open('./test_files/test_process_conieci' + str(test) + '.in','r',encoding="utf-8") as f:
            text_in = f.read()
            
        # Load text from reference file
        with open('./test_files/test_process_conieci' + str(test) + '.ref','r',encoding="utf-8") as f:
            text_ref = f.read()
    
        # Run the function with the input
        list_out = []
        CommentaryToEpidoc.process_conieci(text_in, list_out)
    
        # Convert the output list to a string with each element on a new line
        text_out = '\n'.join(list_out)

        # Test the return value matches the expected output
        if text_out == text_ref:
            ok = True
            print('test_process_conieci Test ' + str(test) + ': PASSED')
        else:
            ok = False
            print('test_process_conieci Test ' + str(test) + ': FAILED')
            print('return value:')
            print(text_out)
    
    return ok
    
    
def test_process_standard_variant():
    """
Runs the function process_standard_variant(...) on the text in 
test_process_standard_variant.in, and compare the output against the text in 
test_process_standard_variant.ref    
    """
    
    ok = False
    
    # Load text from input file
    with open('./test_files/test_process_standard_variant.in','r',encoding="utf-8") as f:
        text_in = f.read()
         
    # Load text from reference file
    with open('./test_files/test_process_standard_variant.ref','r',encoding="utf-8") as f:
        text_ref = f.read()
    
    # Run the function with the input
    list_out = []
    CommentaryToEpidoc.process_standard_variant(text_in, list_out)
    
    # Convert the output list to a string with each element on a new line
    text_out = '\n'.join(list_out)

    # Test the return value matches the expected output
    if text_out == text_ref:
        ok = True
        print('test_process_standard_variant: PASSED')
    else:
        print('test_process_standard_variant: FAILED')
        print('return value:')
        print(text_out)
    
    return ok
    
    
def test_process_footnotes():
    """
Runs the function process_footnotes(...) on the text in 
test_process_footnotes_string.in (which contains a fabricated text string) and
test_process_footnotes_fn.in (which contains fabricated footnotes), and
compares the output against the text in test_process_footnotes.ref    
    """
    
    ok = False
    
    # Load text string from input file
    with open('./test_files/test_process_footnotes_str.in','r',encoding="utf-8") as f:
        text_in = f.read()
        
    # Load footnotes string from input file and convert to list
    with open('./test_files/test_process_footnotes_fn.in','r',encoding="utf-8") as f:
        footnotes_in = f.read()
    footnotes_in = footnotes_in.splitlines()
       
    # Load main XML from reference file
    with open('./test_files/test_process_footnotes_main.ref','r',encoding="utf-8") as f:
        main_ref = f.read()
        
    # Load app XML from reference file
    with open('./test_files/test_process_footnotes_app.ref','r',encoding="utf-8") as f:
        app_ref = f.read()
    
    # Run the function with the input
    main_out, app_out, junk = CommentaryToEpidoc.process_footnotes(text_in, 1, footnotes_in)
    
    # Convert the output lists to strings with each element on a new line
    main_out = '\n'.join(main_out)
    app_out = '\n'.join(app_out)

    # Test the return value matches the expected output
    if main_out == main_ref and app_out == app_ref:
        ok = True
        print('test_process_footnotes: PASSED')
    else:
        print('test_process_footnotes: FAILED')
        print('main XML return value:')
        print(main_out)
        print('app XML return value:')
        print(app_out)
    
    return ok
 
###############################################################################   
# RUN THE TESTS
###############################################################################
import CommentaryToEpidoc

test_process_references()
test_process_omission()
test_process_addition()
test_process_correxi()
test_process_conieci()
test_process_standard_variant()
test_process_footnotes()

