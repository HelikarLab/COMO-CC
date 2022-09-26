import os
import sys
import pandas as pd

# Allow us to import anything we need from the /main/py directory
# From: https://stackoverflow.com/a/30536516/13885200
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_bioservices.input_database import InputDatabase
from async_bioservices.output_database import OutputDatabase
from async_bioservices.taxon_ids import TaxonIDs
from async_bioservices.database_convert import fetch_gene_info


class TestDatabases:
    """
    We've chosen a few random input databases to test.
    These values should never change.
    """
    def test_input_database(self):
        assert InputDatabase.GENE_ID.value == "Gene ID"
        assert InputDatabase.GENE_SYMBOL.value == "Gene Symbol"
        assert InputDatabase.TAXON_ID.value == "Taxon ID"
        assert InputDatabase.UNIGENE_ID.value == "UniGene ID"
        assert InputDatabase.MIM_ID.value == "MIM ID"
        assert InputDatabase.HGNC_ID.value == "HGNC ID"
        assert InputDatabase.HOMOLOGENE_ID.value == "HomoloGene ID"

    def test_output_database(self):
        assert OutputDatabase.CPDB_PROTEIN_INTERACTOR.value == "CPDB Protein Interactor"
        assert OutputDatabase.EC_NUMBER.value == "EC Number"
        assert OutputDatabase.GAD_DISEASE_INFO.value == "GAD Disease Info"
        assert OutputDatabase.GO_ID.value == "GO ID"
        assert OutputDatabase.HOMOLOG_HUMAN_ENS_GENE_ID.value == "Homolog - Human Ens Gene ID"
        assert OutputDatabase.KEGG_PATHWAY_ID.value == "KEGG Pathway ID"
        assert OutputDatabase.UNIPROT_ACCESSION.value == "UniProt Accession"

    def test_taxon_ids(self):
        assert TaxonIDs.HUMAN.value == 9606


def test_conversion():
    """
    This test determines if the data collected/converted from async_bioservices.database_convert.fetch_gene_info is correct.
    It does so by comparing the results of fetch_gene_info to a pre-collected dataframe, defined as `static_dataframe`
    """
    static_dataframe: pd.DataFrame = pd.DataFrame(
        data={
            "Ensembl Gene ID": [
                "ENSG00000141510",
                "ENSG00000232810",
                "ENSG00000146648",
                "ENSG00000112715",
                "ENSG00000130203",
                "ENSG00000136244",
                "ENSG00000105329",
                "ENSG00000177000",
                "ENSG00000091831",
                "ENSG00000142208"
            ]
        },
        index=[
            "TP53", "TNF", "EGFR",
            "VEGFA", "APOE", "IL6",
            "TGFB1", "MTHFR", "ESR1", "AKT1"
        ]
    )

    input_values: list[str] = static_dataframe.index.to_list()
    input_db: InputDatabase = InputDatabase.GENE_SYMBOL
    output_db: list[OutputDatabase] = [OutputDatabase.ENSEMBL_GENE_ID]

    # This is the function we're testing
    test_dataframe: pd.DataFrame = fetch_gene_info(
        input_values=input_values,
        input_db=input_db,
        output_db=output_db,
        taxon_id=9606
    )

    assert static_dataframe.equals(test_dataframe)
