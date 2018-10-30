# ingester.py

Ingester will take in .xyz file from QM9 dataset and return data in PIF format in test.json.

[Dataset explanation & source](https://www.nature.com/articles/sdata201422)

[Dataset](https://figshare.com/articles/Data_for_6095_constitutional_isomers_of_C7H10O2/1057646)

Usage: 
1. Ingester('foo.xyz') -> test.json
2. From command line: ./ingester.py foo.xyz 

There are 3 steps to the ingester:
1. Load and format data: This is accomplished via. the FileToDF() function, which takes in a .xyz file from the dataset and returns two dataframes. The first dataframe (df) is just a barebones dataframe with all the information from the .xyz while the second (df2) is a reformatted dataframe with additional labels and information about the values from the data. df is used to later extract out the compound name whereas df2 is the dataframe that's eventually reformatted into the PIF file. 

2. Determining compound name: This is accomplished via. the ParseCompoundName()
function. This function takes in the barebones df from step 1 and utilizes the format of the data to extract a list of all atoms. Since molecular names have a defined stucture that contains information about the molecule, it was important to retain and express that structure rather than simply counting the number of each element i.e CxHyOz could be any number of constitutional isomers, but CH3COOH preserves information about the molecule that is not expressed in the former. In order to get this, I kept track of points in which the atoms in the list of atoms changed from one kind to another. I then used those pivot points to determine where atoms were clustered and how many were clustered together return the name of the compound.

3. Converting the information to a PIF via the WritePIF() function. This function uses the reformatted dataframe from step 1 (df2) to extract out the number of properties providede and writes them all to a PIF file with the help of pypif.

The Ingester() function uses the outputs of these three functions to establish a pipeline for taking in the data and returning test.json. 
