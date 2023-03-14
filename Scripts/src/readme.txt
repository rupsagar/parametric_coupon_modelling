1. To launch GUI:
a. Run the script 'main_gui.py'
b. The user may have to add the path of the abaqus to the variable 'abqPath' depending on the local machine where the script is run
	(New paths can be appended to the existing list separated by comma; the script has been currently tested only in Windows OS)
c. Choose the coupon template
d. Select 'Built-in/Custom' model
e. Enter model parameters
f. Select a location to save the model
g. 'Create Model' to generate the model
h. Upon successful run, 6 files (_Data.json, _Geom.txt, _Job.inp, _Model.cae, _Model.jnl, _Status.txt) are generated in destination folder. 



2. In order to run the script in Abaqus CLI (needed for debug purpose):
a. Use the script 'main_debug.py'
b. Add the path of the 'src' folder to 'srcPath'
	(New paths can be appended to the existing list separated by comma; the current folder path is added; my guess is it should work correctly)
c. Uncomment the desired the template and coupon and comment out the remaining ones
d. Copy the script and paste in Abaqus CLI (command line interface) to generate the model. Or run the script from File -> Run Script option

