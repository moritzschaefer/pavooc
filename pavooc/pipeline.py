import ipdb
ipdb.set_trace()
from pavooc.data_integration.downloader import main as main_downloader
from pavooc.preprocessing.preprocessing import main as main_preprocessing
from pavooc.preprocessing.prepare_flashfry import main as main_ff

if __name__ == "__main__":
    main_downloader()
    main_preprocessing()
    main_ff()
