--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
The scripts in this folder perform parametric modelling of different coupons using python in the Abaqus environment.
There are two ways to generate the models:
1. Using GUI script
2. Using Abaqus CLI (command line interface)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1. Using GUI script:
==================================
a. Run the script 'main_gui.py'. It can be run from terminal or command prompt using the command 'python main_gui.py'. 
   Alternatively, the file can be opened in any code editor (like VS Code) and run from there.
b. The user may have to add path of the Abaqus to the variable 'abqPath' depending on the local machine or the OS where the script is run.
   New paths can be appended to the existing list by separating with commas. The script has been tested in Windows and Giseh environment.
c. Choose the coupon template.
d. Select 'Built-in/Custom' model.
e. Enter model parameters.
f. Select a location to save the model.
g. Click 'Create Model' to generate the model.
h. Upon successful run, 6 files (Data.json, Geom.txt, Job.inp, Model.cae, Model.jnl, Status.txt) and 1 folder (InpFolder) are generated in the destination folder.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2. Using Abaqus CLI:
==================================
a. Use the script 'main_debug.py'. This method of generating model (and hence the script) was originally intended for debugging purpose.
b. Add the path of the 'src' folder to variable 'srcPath' if the script is run from a location whose path is not included in the list.
   New paths can be appended to the existing list by separating with commas.
c. Uncomment the desired the template and coupon and comment out the remaining ones.
d. Copy the script and paste in Abaqus CLI to generate the model. Alternatively, run the script from Abaqus menu option: File -> Run Script.
e. Upon successful run, 6 files (Data.json, Geom.txt, Job.inp, Model.cae, Model.jnl, Status.txt) and 1 folder (InpFolder) are generated in the current working directory.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

