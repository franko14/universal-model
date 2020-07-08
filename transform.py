# This script consists of multiple transformation functions that read grib data
# Lubomir Franko
# July 8th 2020
import os 

# --------------------------------------------------------------------------------------------------------
# Project data from global model to eu-nest, for specific area
# Create wehights file if non-existent
# --------------------------------------------------------------------------------------------------------
def global_to_eugrid(in_grib, region, process):
    target_grid_description = f'grid_files/{region}/icon_eu_grid_{region}.txt'
    os.path.join('grid_files',region,'icon_eu_grid_' + region + '.txt')
    weights_file = f'grid_files/{region}/weights_{region}.nc'
    
    if not os.path.exists(weights_file):
        grid_file = 'grid_files/icon_grid_0026_R03B07_G.nc' 
        weights_file = os.path.join('grid_files',region,'weights_' + region + '.nc')
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
    """
    
    """
    target_grid_description = f'grid_files/{region}/icon_eu_grid_{region}.txt'
    out_folder = os.path.join('data',args.product_type, region, process)
    os.makedirs(out_folder, exist_ok=True)
    out_grib_name = in_grib.split('/')[-1]
    out_grib = os.path.join(out_folder,out_grib_name)
    cdo.remapbil(target_grid_description, input = in_grib, output = out_grib)

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