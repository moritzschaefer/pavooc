from pavooc.data_integration.downloader import main as main_downloader
from pavooc.preprocessing.preprocessing import main as main_preprocessing
from pavooc.preprocessing.prepare_flashfry import main as main_ff
# from pavooc.preprocessing.sgrna_finder import main as main_sgrna
from pavooc.preprocessing.exon_guide_search import main as main_guide_search
from pavooc.preprocessing.guides_to_db import main as main_guides_to_db


if __name__ == "__main__":
    main_downloader()
    main_preprocessing()
    main_ff()
    # main_sgrna()  # manual search
    main_guide_search()  # ff search
    main_guides_to_db
