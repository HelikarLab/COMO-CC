#!/usr/bin/python3
import re
import sys
import getopt
import os
import json
import pandas as pd
import numpy as np
from project import configs
from GSEpipelineFast import *

from rpy2.robjects import pandas2ri
pandas2ri.activate()

# import R libraries
DESeq2 = importr("DESeq2")
edgeR = importr("edgeR")
openxlsx =importr("openxlsx")
# read and translate R functions
f = open("/home/jupyteruser/work/py/rscripts/DGE.R", "r")
string = f.read()
f.close()
DGEio = SignatureTranslatedAnonymousPackage(string, "DGEio")

# split multi-part entrez ids into muliple rows
def breakDownEntrezs(Disease_UP):
    Disease_UP['Gene ID'] = Disease_UP['Gene ID'].str.replace('///','//')
    singleGeneNames = Disease_UP[~Disease_UP['Gene ID'].str.contains('//')].reset_index(drop=True)
    multipleGeneNames = Disease_UP[Disease_UP['Gene ID'].str.contains('//')].reset_index(drop=True)
    breaksGeneNames = pd.DataFrame(columns=['Gene ID'])
    #print(singleGeneNames.shape)
    #print(multipleGeneNames.shape)
    for index, row in multipleGeneNames.iterrows():
        for genename in row['Gene ID'].split('//'):
            breaksGeneNames = breaksGeneNames.append({'Gene ID': genename}, ignore_index=True)
    GeneExpressions = singleGeneNames.append(breaksGeneNames, ignore_index=True)
    return GeneExpressions

# fetch entrez ids 
def get_entrez_id(regulated, outputFullPath, fullflag=False):
    Disease_UP = fetch_entrez_gene_id(list(regulated.index.values), input_db='Affy ID')
    Disease_UP.drop(columns=['Ensembl Gene ID'],inplace=True)
    Disease_UP.replace(to_replace='-', value=np.nan, inplace=True)
    if not fullflag:
        Disease_UP.dropna(how='any', subset=['Gene ID'], inplace=True)
        GeneExpressions = breakDownEntrezs(Disease_UP)
        # GeneExpressions.set_index('Gene ID', inplace=True)
    else: 
        GeneExpressions = Disease_UP
            
    GeneExpressions['Gene ID'].to_csv(outputFullPath, index=False)
    return GeneExpressions

# read config file
def pharse_configs(inqueryFullPath):
    xl = pd.ExcelFile(inqueryFullPath)
    sheet_name = xl.sheet_names
    inqueries = pd.read_excel(inqueryFullPath, sheet_name=sheet_name, header=0)
    inqueries['Sheet1'].fillna(method='ffill',inplace=True)
    df = inqueries['Sheet1'].loc[:,['GSE ID','Samples','GPL ID','Instrument']]
    df_target = inqueries['Sheet1'].loc[:,['Samples','Experiment']]
    df_target.rename(columns={'Samples':'FileName','Experiment':'Condition'},inplace=True)
    df_target['FileName'] = df_target['FileName'].astype(str) + '.txt.gz'
    df_target['SampleNumber']= 1 + df_target.index.values
    df_target = df_target[['SampleNumber','FileName','Condition']]
    df_target['Condition'] = df_target['Condition'].str.lower()
    return df, df_target

def main(argv):
    targetfile = 'targets.txt'
    count_matrix = None
    try:
        opts, args = getopt.getopt(argv, "hd:c:m:", ["data_source=", "config_file=", "count_matrix="])
    except getopt.GetoptError:
        print('python3 disease_analysis.py -d <data_source> -i <config_file> -c <config_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python3 disease_analysis.py -d <data_source> -c <config_file> -m <count_matrix>')
            sys.exit()
        elif opt in ("-d", "--data_source"):
            data_source = arg
        elif opt in ("-c", "--config_file"):
            config_file = arg
        elif opt in ("-m", "--count_matrix"):
            count_matrix = arg
    print('Config file is "', config_file)
 
    # print('Target file is "', targetfile)
    # print(configs.rootdir)
    # filename = 'Disease_Gene_Analyzed.xlsx'
    try:
        inqueryFullPath = os.path.join(configs.rootdir, 'data', config_file)
    except:
        print('Config file not properly defined')
    
    targetdir = os.path.join(configs.datadir, targetfile)
    if data_source == 'microarray':
        querytable, df_target = pharse_configs(inqueryFullPath)
        df_target.to_csv(targetdir, index=False, sep='\t')
        sr = querytable['GSE ID']
        gse_ids = sr[sr.str.match('GSE')].unique()
        GSE_ID = gse_ids[0]
        gseXXX = GSEproject(GSE_ID, querytable, configs.rootdir)
        for key,val in gseXXX.platforms.items():
            rawdir = os.path.join(gseXXX.genedir,key)
            print('{}:{}, {}'.format(key, val, rawdir))
            data2 = affyio.fitaffydir(rawdir, targetdir)
            data2 = ro.conversion.rpy2py(data2)
    elif data_source == 'bulk':
        print('Count Matrix File is "', count_matrix)
        count_matrix_path = os.path.join(configs.rootdir, 'data', count_matrix)
        data2 = DGEio.DGE_main(count_matrix_path, inqueryFullPath)
        data2 = ro.conversion.rpy2py(data2)
        GSE_ID = "bulk"

    else:
        print("data_source should be either 'microarray' or 'bulk'")
        print("Refer to example config file for either type for formatting")
        
    data2['abs_logFC'] = data2['logFC'].abs()
    data2.sort_values(by='abs_logFC', ascending=False, inplace=True)
    regulated = data2[data2['abs_logFC']>=1.0]
    down_regulated = regulated[regulated['logFC']<0]
    up_regulated = regulated[regulated['logFC']>0]
   

    up_file = os.path.join(configs.datadir,'Disease_UP_{}.txt'.format(GSE_ID))
    down_file = os.path.join(configs.datadir,'Disease_DOWN_{}.txt'.format(GSE_ID))
    if data_source == 'microarray':
        Disease_UP = get_entrez_id(up_regulated, up_file)
        Disease_DOWN = get_entrez_id(down_regulated, down_file)
    else:
        up_regulated['Gene ID'].to_csv(up_file, index=False)
        Disease_UP = up_regulated
        down_regulated['Gene ID'].to_csv(down_file, index=False)
        Disease_DOWN = down_regulated
  
        
    Disease_UP.dropna(how='any', subset=['Gene ID'], inplace=True)
    Disease_DOWN.dropna(how='any', subset=['Gene ID'], inplace=True)
    # Disease_UP = pd.read_csv(up_file, index_col=False, header=None)
    # Disease_UP.rename(columns={0:'Gene ID'}, inplace=True)
    # Disease_UP['Gene ID'] = Disease_UP['Gene ID'].astype(str)
    # Disease_UP = breakDownEntrezs(Disease_UP)
    # Disease_DOWN = pd.read_csv(down_file, index_col=False, header=None)
    # Disease_DOWN.rename(columns={0:'Gene ID'}, inplace=True)
    # Disease_DOWN['Gene ID'] = Disease_DOWN['Gene ID'].astype(str)
    # Disease_DOWN = breakDownEntrezs(Disease_DOWN)

    all_file = os.path.join(configs.datadir, 'Disease_FULL_{}.txt'.format(GSE_ID))
    Disease_FULL = get_entrez_id(data2, all_file, True)
    data2.index.name = 'Affy ID'
    data2['ENTREZ_GENE_ID'] = Disease_FULL['Gene ID']
    #data2.dropna(how='any', subset=['ENTREZ_GENE_ID'], inplace=True)
    raw_file = os.path.join(configs.datadir, 'Raw_Fit_{}.csv'.format(GSE_ID))
    print('Raw Data saved to\n{}'.format(raw_file))
    data2.to_csv(raw_file, index=False)

    files_dict = {'GSE': GSE_ID, 'UP_Reg': up_file, 'DN_Reg': down_file, 'RAW_Data': raw_file}
    files_json = os.path.join(configs.datadir, 'step2_results_files.json')
    with open(files_json, 'w') as fp:
        json.dump(files_dict, fp)
    if data_source == 'microarray':
        os.remove(targetdir)

if __name__ == "__main__":
   main(sys.argv[1:])
