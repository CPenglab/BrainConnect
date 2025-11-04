"""
BrainConnect - a flexible pipeline to integrate brain connectivity and spatial transcriptomics for downstream analysis
"""

__version__ = "1.0.0"
__author__ = "sparkumr"
__email__ = "1984607077@qq.com"


__all__ = [
    '__version__',
    'Config'
]

class Config:
    """Package configuration class"""
    DEFAULT_RESOLUTION = 25
    DEFAULT_WINDOW_SIZE = 5
    SUPPORTED_FORMATS = ['swc', 'nrrd', 'csv', 'h5']
    
    @classmethod
    def show_info(cls):
        """Display package information"""
        info = f"""
Sp_Neuron Configuration Information:
  Version: {__version__}
  Default Resolution: {cls.DEFAULT_RESOLUTION}
  Default Window Size: {cls.DEFAULT_WINDOW_SIZE}
  Supported Formats: {', '.join(cls.SUPPORTED_FORMATS)}
  Author: {__author__}
        """
        print(info)