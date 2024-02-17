# Parametric Coupon Modelling

## Python modules for parametric modelling of different coupons in Abaqus

The scripts in this folder perform parametric modelling of different coupons using python in the Abaqus environment. There are two ways to generate the models:
   1. Using GUI script
   2. Using Abaqus CLI (command line interface)

### Using GUI script:
   - Run the script `main_gui.py`. It can be run from terminal or command prompt using the command `python main_gui.py`. Alternatively, the file can be opened in any code editor (like VS Code) and run from there.
   - The user may have to add path of the Abaqus to the variable `abqPath` depending on the local machine or the OS where the script is run. New paths can be appended to the existing list by separating with commas. The script has been tested in `Windows` and `Linux` environment.
   - Choose the coupon template.
   - Select `Built-in/Custom` model.
   - Enter model parameters.
   - Select a location to save the model.
   - Click `Create Model` to generate the model.
   - Upon successful run, 6 files (`Data.json`, `Geom.txt`, `Job.inp`, `Model.cae`, `Model.jnl`, `Status.txt`) and 1 folder (`InpFolder`) are generated in the destination folder.

### Using Abaqus CLI:
   - Use the script `main_debug.py`. This method of generating model (and hence the script) was originally intended for debugging purpose.
   - Add the path of the `src` folder to variable `srcPath` if the script is run from a location whose path is not included in the list. New paths can be appended to the existing list by separating with commas.
   - Update `srcPathID` to the list index of the correct `srcPath` entry.
   - Uncomment the desired the template and coupon and comment out the remaining ones.
   - Copy the script and paste in Abaqus CLI to generate the model. Alternatively, run the script from Abaqus menu option: `File -> Run Script`.
   - Upon successful run, 6 files (`Data.json`, `Geom.txt`, `Job.inp`, `Model.cae`, `Model.jnl`, `Status.txt`) and 1 folder (`InpFolder`) are generated in the current working directory.

## Authors

- Rupsagar Chatterjee
