Demand Sensing
------------

In this project, we are analyzing the combination of product demand data with commercial data for various products.

[ignore these instructions and follow instructions below to build a container] To run the setup.py file to install alll dependencies navigate to root folder and run `python3 setup.py install` (This errors out because you need to set up virtual eenvironment and install OpenMP runtime (vcomp140.dll or libgomp-1.dll for Windows, libomp.dylib for Mac OSX, libgomp.so for Linux and other UNIX-like OSes)

In the command line, navigate to demandsensing/ and run `$docker build -t USERNAME/PROJECT:VERSION . ` (i.e. `$docker build -t sagrawal01/demandsensing:v1 . `) to build the docker image from the file. 

Run `$docker images` to check that your image was built. Once you see it, run `$docker run -it -v (current working directory):/app USERNAME/PROJECT:VERSION /bin/bash` in command line. This will run the container. Then navigate to src/compare_data and do the following: 


In order to load the data and train models for a specific product, please run via terminal: python3 output.py [country] [Product] [NDC #] [Input File] [Start Date] [Months to run training] [Output name]

For example: `python3 output.py US 001 001 input_file.xlsx 2019-12-31 4 product_output`

Project Structure
------------

    demandsensing/          
    ├── LICENSE              
    ├── pyproject.toml 
    ├── README.md 
    ├── Dockerfile
    ├── requirements.txt  
    ├── setup.py            <- Required packages and setup to run code
    ├── src/                <- Source code for this package
    │   ├──compare_data/ <- module to combine demand data with commercial data and analyze
    │   │   ├──processdata.py
    │   │   ├──getdata.py
    │   │   ├──ml_training.py
    │   │   ├──output.py
    │   ├──config/
    │   │   ├──encrypted
    │   │   ├──key.txt
--------
