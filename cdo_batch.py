import os
from cdo import *
import subprocess

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
print (os.getcwd())

""" 
LOAD PROCESS METADATA
"""
from METEO_PARAMS import VARIABLES

class Metadata:
    pass

""" 
----------------------------------------------------------------------------------------------------------
SPATIAL PROCESSING
----------------------------------------------------------------------------------------------------------
Vytvorili sme si priecinok grid_files, kde sme ulozili aj budeme ukladat vsetky potrebne subory na 
premapovanie grib raw suborov
"""

# --------------------------------------------------------------------------------------------------------
# Project data from global model to eu-nest, for specific area
# Create wehights file if non-existent
# --------------------------------------------------------------------------------------------------------
def global_to_eugrid(in_grib, region, process):
    target_grid_description = f'grid_files/{region}/icon_eu_grid_{region}.txt'
    weights_file = f'grid_files/{region}/weights_{region}.nc'
    
    if not os.path.exists(weights_file):
        grid_file = 'grid_files/icon_grid_0026_R03B07_G.nc' 
        weights_file = f'grid_files/{region}/weights_{region}.nc'
        cdo.gennn(f'{target_grid_description} {grid_file}', output = weights_file)

    out_folder = os.path.join('data',args.product_type, region, process)
    os.makedirs(out_folder, exist_ok=True)
    out_grib_name = in_grib.split('/')[-1]
    out_grib = os.path.join(out_folder,out_grib_name)
    cdo.remapbil(target_grid_description, input = in_grib, output = out_grib)

# --------------------------------------------------------------------------------------------------------
# Project data from eu-nest to specific area
# --------------------------------------------------------------------------------------------------------
def eu_to_eugrid(in_grib, region, process):
    target_grid_description = f'grid_files/{region}/icon_eu_grid_{region}.txt'
    out_folder = os.path.join('data',args.product_type, region, process)
    os.makedirs(out_folder, exist_ok=True)
    out_grib_name = in_grib.split('/')[-1]
    out_grib = os.path.join(out_folder,out_grib_name)
    cdo.remapbil(target_grid_description, input = in_grib, output = out_grib)

""" 
----------------------------------------------------------------------------------------------------------
PREPROCESSING FUNCTIONS
----------------------------------------------------------------------------------------------------------
"""

# --------------------------------------------------------------------------------------------------------
# Function to parse icon grib string to find forecasted hour
# --------------------------------------------------------------------------------------------------------
def find_forecast_hour(string):
    if '/' in string:
        string = string.split('/')[-1]
    no = 0
    for n, symbol in enumerate(string):
        if symbol == '_':
            no = 0
        else:
            no += 1
        if no == 3 and string[n+1] == '_':
            return (string[n-2:n+1])

# --------------------------------------------------------------------------------------------------------
# Function to merge forecasted grib files to one n-dimensinal grib for each forecasted timestamp
# --------------------------------------------------------------------------------------------------------
def merge_gribs(*gribs):

    # 1. Define output folder and output filename
    out_folder = os.path.join(raw_fcst_data,year,month,day,metadata.run,args.product_type) 
    f_name = f'{args.process}_{year}{month}{day}{metadata.run}_{find_forecast_hour(gribs[0][0])}.grib2'

    # 2. Create output directory - solar/wind/cons
    os.makedirs(out_folder, exist_ok=True)

    # 3. Use "os" command "cat" to merge grib files passed as argument 
    out_file = os.path.join(out_folder, f_name)
    list_command = ' '.join(map(str, gribs[0]))
    #args_to_cli = str(gribs[0]).replace('[','').replace(']','').replace(',','')
    os.system('cat ' + list_command+' > ' + out_file)

# --------------------------------------------------------------------------------------------------------
# Main function
# --------------------------------------------------------------------------------------------------------
def main():
    # Merge gribs if args.process == 'fcst'
    if args.process == 'fcst':
        for file_no in range(len(glob.glob(
                os.path.join(raw_fcst_data,year,month,
                day,metadata.run,directories_names[0],'*')
                ))):
            gribs_to_merge = []
            for directory in directories_names:
                lst = glob.glob(os.path.join(raw_fcst_data,year,month,day,metadata.run,directory,'*'))
                lst.sort()
                gribs_to_merge.append(lst[file_no])
            #print (gribs_to_merge)
            merge_gribs(gribs_to_merge)
    """
    Nasledujuci proces si vezme parametre:

    model_type
    region
    product_type
    process

    a podla toho upravi bud fcst alebo history data do pozadovaneho formatu pre danu krajinu.
    """    
    # Process data from ICON-EU = local model
    if args.model_type == 'local' and args.process == 'fcst':
        in_folder = os.path.join(os.path.join(
            raw_fcst_data,
            year,
            month,
            day,
            metadata.run,
            args.product_type,
            '*'
            ))
        lst = glob.glob(os.path.join(in_folder))
        lst.sort()
        for in_grib in lst:
            eu_to_eugrid(in_grib, args.region, args.process)

    # Process data from ICON = global model
    elif args.model_type == 'global' and args.process == 'fcst':
        in_folder = os.path.join(os.path.join(
            raw_fcst_data,
            year,
            month,
            day,
            metadata.run,
            args.product_type,
            '*'
            ))
        lst = glob.glob(os.path.join(in_folder))
        lst.sort()
        for in_grib in lst:
            global_to_eugrid(in_grib, args.region, args.process)

    # Process history data
    elif args.process == 'hist':
        lst = []
        for fname in directories_names:
            lst.append(os.path.join('cds_raw_data',fname + '.grib'))
        lst.sort()
        for in_grib in lst:
            eu_to_eugrid(in_grib, args.region, args.process)
       
if __name__ == '__main__':

    # Nacitanie cdo
    cdo = Cdo()

    """
    --------------------------------------
    Sem budeme nacitavat parametre z Azure
    --------------------------------------
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-mt",'--model_type', action='store', dest ='model_type',
                        help="set model type ['local','global']", default='local')

    parser.add_argument("-rg",'--region', action='store', dest ='region',
                        help="set region ['sk','de']", default='sk')

    parser.add_argument("-pt",'--product_type', action='store', dest ='product_type',
                        help="set product type ['wind','solar','protiodchylka']",
                        default='wind')

    parser.add_argument("-pr",'--process', action='store', dest ='process',
                        help="set process type ['train','hist']", default='hist')

    parser.add_argument("-rn",'--run', action='store', dest ='run',
                        help="set run hour ['00','03','06',...,'21']", default='00')

    args = parser.parse_args()
    print (args)
    #exit()
    metadata = Metadata()

    """
   model_type     = 'local'       # local/global - Nacitane z pipeline 
                                            # (toto budeme robit az vo verzii 2.0, zatial vzdy local)
    region         = 'sk'          # de, sk - Nacitane z pipeline
    product_type   = 'protiodchylka'       # wind, solar - Nacitane z pipeline
    process        = 'hist'        # hist, fcst - Nacitane z pipeline
    """
    if args.process == 'fcst':
        run     = '00'     # 00, 03, 06, 09 ...
        year    = '2020'            # Nacitane z pipeline - podla datumu predikcie
        month   = '06'              # Nacitane z pipeline - podla datumu predikcie
        day     = '02'              # Nacitane z pipeline - podla datumu predikcie
    
    if args.model_type == 'local':
        raw_fcst_data = 'iconeudata'
    else:
        raw_fcst_data = 'iconglobaldata'

    directories_names = VARIABLES[args.product_type][args.process]

    main()