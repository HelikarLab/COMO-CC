#!/usr/bin/python3
import os
import sys
import time
import pandas as pd
import numpy as np
import cobra
import copy
from cobra.flux_analysis import (single_gene_deletion, single_reaction_deletion,
                                 double_gene_deletion, double_reaction_deletion)
from project import configs
# from transcriptomic_gen import *
# from proteomics_gen import *

def knock_out_simulation(datadir, model_file, inhibitors):

    if model_file[-4:] == '.xml':
        model = cobra.io.read_sbml_model(os.path.join(datadir, model_file))
    elif model_file[-4:] == '.mat':
        model = cobra.io.load_matlab_model(os.path.join(datadir, model_file))
    else:
        print("Unsupported File Format of Model: {}".format(model_file))
        return None

    DT_genes = pd.read_csv(os.path.join(datadir,inhibitors), header=None)
    DT_genes.rename(columns={0:'Gene ID'},inplace=True)
    DT_genes['Gene ID'] = DT_genes['Gene ID'].astype(str)

    geneInd2genes = [x.id for x in model.genes]
    print(len(geneInd2genes))
    geneInd2genes = set(geneInd2genes)
    print(len(geneInd2genes))
    DT_model = set(DT_genes['Gene ID'].tolist()).intersection(geneInd2genes)
    print(len(DT_model))
    DT_model = list(DT_model)

    model_opt = model.optimize().to_frame()
    model_opt[abs(model_opt) < 1e-8] = 0.0

    fluxsolution = pd.DataFrame()
    for id in DT_model:
        # model_cp = copy.deepcopy(model)
        gene = model.genes.get_by_id(id)
        buff = gene._functional
        gene.knock_out()
        opt_model = model.optimize().to_frame()
        gene._functional = buff
        fluxsolution[id]=opt_model['fluxes']

    # fluxsolution
    fluxsolution[abs(fluxsolution) < 1e-8] = 0.0

    fluxSolutionRatios = fluxsolution.div(model_opt['fluxes'], axis=0)
    # fluxSolutionRatios
    fluxSolutionDiffs = fluxsolution.sub(model_opt['fluxes'], axis=0)
    # fluxSolutionDiffs

    HasEffects_Gene = []
    for id in DT_model:
        gene = model.genes.get_by_id(id)
        for rxn in gene.reactions:
            if abs(fluxSolutionDiffs.at[rxn.id, id]) > 1e-7:
                HasEffects_Gene.append(id)
                break
    # HasEffects_Gene
    return model, geneInd2genes, HasEffects_Gene, fluxSolutionRatios, fluxSolutionDiffs


def create_gene_pairs(datadir, model, geneInd2genes, fluxSolutionRatios, HasEffects_Gene, RA_Down):
    RA_down = pd.read_csv(os.path.join(datadir,RA_Down))
    DAG_dis_genes = pd.DataFrame()
    DAG_dis_genes['Gene ID'] = RA_down.iloc[:,0].astype(str)
    # DAG_dis_genes

    DAG_dis_met_genes = set(DAG_dis_genes['Gene ID'].tolist()).intersection(geneInd2genes)
    # DAG_dis_met_genes

    DAG_dis_met_rxnInd = []
    Gene_i = []
    for id in DAG_dis_met_genes:
        gene = model.genes.get_by_id(id)
        for rxn in gene.reactions:
            DAG_dis_met_rxnInd.append(rxn.id)
            Gene_i.append(id)

    # DAG_dis_met_rxnInd
    Gene_df = pd.DataFrame(Gene_i,columns=['Gene IDs'],index=DAG_dis_met_rxnInd)
    # Gene_df

    DAG_rxn_fluxRatio = fluxSolutionRatios.loc[DAG_dis_met_rxnInd]
    # DAG_rxn_fluxRatio

    gene_mat_out = []
    # Gene_i = DAG_dis_met_genes
    # Rind_i = DAG_dis_met_rxnInd
    for id in HasEffects_Gene:
        pegene = pd.DataFrame()
        pegene['Gene IDs'] = Gene_df['Gene IDs'].copy()
        pegene['rxn_fluxRatio'] = DAG_rxn_fluxRatio[id].copy()
        pegene['Gene'] = id
        pegene.dropna(axis=0,subset=['rxn_fluxRatio'],inplace=True)
        pegene.index.name='reaction'
        pegene.reset_index(drop=False, inplace=True)
        gene_mat_out.append(pegene)

    Gene_Pairs = pd.concat(gene_mat_out, ignore_index=True)
    return Gene_Pairs


def score_gene_pairs(Gene_Pairs, filename):
    p_model_genes = Gene_Pairs.Gene.unique()
    d_score = pd.DataFrame([], columns=['score'])
    for p_gene in p_model_genes:
        data_p = Gene_Pairs.loc[Gene_Pairs['Gene'] == p_gene].copy()
        # print(data_p)
        total_aff = data_p['Gene IDs'].unique().size
        # print(total_aff)
        n_aff_down = data_p.loc[abs(data_p['rxn_fluxRatio']) < 0.99, 'Gene IDs'].unique().size
        # print(n_aff_down)
        n_aff_up = data_p.loc[abs(data_p['rxn_fluxRatio']) > 1.0, 'Gene IDs'].unique().size
        # print(n_aff_up)
        d_s = ((n_aff_down - n_aff_up) / total_aff)
        # print(d_s)
        d_score.at[p_gene, 'score'] = d_s

    d_score.index.name = 'Gene'
    d_score.to_csv(os.path.join(configs.datadir, filename))
    return d_score


def score_gene_pairs_diff(Gene_Pairs, filename):
    p_model_genes = Gene_Pairs.Gene.unique()
    d_score = pd.DataFrame([], columns=['score'])
    for p_gene in p_model_genes:
        data_p = Gene_Pairs.loc[Gene_Pairs['Gene'] == p_gene].copy()
        # print(data_p)
        total_aff = data_p['Gene IDs'].unique().size
        # print(total_aff)
        n_aff_down = data_p.loc[data_p['rxn_fluxRatio'] < -1e-8, 'Gene IDs'].unique().size
        # print(n_aff_down)
        n_aff_up = data_p.loc[data_p['rxn_fluxRatio'] > 1e-8, 'Gene IDs'].unique().size
        # print(n_aff_up)
        d_s = ((n_aff_down - n_aff_up) / total_aff)
        # print(d_s)
        d_score.at[p_gene, 'score'] = d_s

    d_score.index.name = 'Gene'
    d_score.to_csv(os.path.join(configs.datadir, filename))
    return d_score


def main(argv):
    print(configs.rootdir)
    datadir = os.path.join(configs.rootdir,'data')
    print(datadir)
    model, geneInd2genes, HasEffects_Gene, fluxSolutionRatios, fluxSolutionDiffs = knock_out_simulation(datadir=datadir,
                                      model_file='Th1_Cell_SpecificModel4manuscript.mat',
                                      inhibitors='Th1_inhibitors_Entrez.txt')
    Gene_Pairs_down = create_gene_pairs(datadir,
                                   model,
                                   geneInd2genes,
                                   fluxSolutionRatios,
                                   HasEffects_Gene,
                                   RA_Down='RA_DOWN.txt')
    Gene_Pairs_down.to_csv(os.path.join(datadir,'Gene_Pairs_Inhi_Fratio_DOWN.txt'),index=False)
    Gene_Pairs_up = create_gene_pairs(datadir,
                                   model,
                                   geneInd2genes,
                                   fluxSolutionRatios,
                                   HasEffects_Gene,
                                   RA_Down='RA_UP.txt')
    Gene_Pairs_up.to_csv(os.path.join(datadir,'Gene_Pairs_Inhi_Fratio_UP.txt'),index=False)
    print(geneInd2genes)
    print(fluxSolutionRatios)
    print(HasEffects_Gene)
    d_score_down = score_gene_pairs(Gene_Pairs_down, 'd_score_DOWN.csv')
    # d_score_down = score_gene_pairs_diff(Gene_Pairs_down, 'd_score_DOWN.csv')
    d_score_up = score_gene_pairs(Gene_Pairs_up, 'd_score_UP.csv')
    # d_score_up = score_gene_pairs_diff(Gene_Pairs_up, 'd_score_UP.csv')
    print(d_score_down)
    print(d_score_up)


if __name__ == "__main__":
   main(sys.argv[1:])
