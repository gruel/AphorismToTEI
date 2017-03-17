# Hyppocratic Aphorisms

## AphorismToTEI

A Python module contained in CommentaryToEpidoc.py to convert text files
to EpiDoc compatible XML.

See the documentation in CommentaryToEpidoc.py and read the ``doos`` folder
for more information.

* Example input files can be found in the Example/TextFiles folder
* the convenience script: driver.py was used to run the module on these files
  to produce the corresponding output in the XML folder,
  xml_template.txt is also required.

* test_CommentaryToEpidoc.py contains some testing function.
  The input and reference output for tests are in folder test_files



## Installation

### Required

* Python ( v3.5 or higher) 

### Installation from Source

Clone the code from the github repository:

```commandline
git clone https://github.com/UoMResearchIT/CommentaryToEpidoc.git
```

go into the project directory:

```commandline
cd CommentaryToEpidoc
```

Install the required packages using their list available in 
the file *requirement.txt*:

```commandline
pip install -U -r requirements.txt --user 
```

The ```--user``` is optional but will install the package without the need 
to be administrator. It will install the package in a user accessible directory
(plateforme dependant).

Install the package:

```commandline
python setup.py install --user
```

## Usage

When the package is installed, it should be available in your ```PATH``` 
under the name ```CommentaryToEpidoc```. 

To use it start a terminal and execute the command:

```commandline
CommentaryToEpidoc <path> 
```

where:

```path``` is the name of the directory which contains the files to treat.
 
## Log 

At the end of the execution a log file called ```hyppocratic.log``` will be 
create in the directory where the process was run.
It will contains informations on the run and errors if any.