from __future__ import absolute_import

import os

from .mapping_metrics import DragenMappingMetics
from .fragment_length import DragenFragmentLength
from .ploidy_estimation_metrics import DragenPloidyEstimationMetrics
from .vc_metrics import DragenVCMetrics
from .coverage_per_contig import DragenCoveragePerContig
from .coverage_metrics import DragenCoverageMetrics
from .coverage_hist import DragenCoverageHist
from .fastqc_metrics import DragenFastQcMetrics

import logging
log = logging.getLogger(__name__)


class MultiqcModule(DragenMappingMetics, DragenFragmentLength, DragenPloidyEstimationMetrics,
                    DragenVCMetrics, DragenCoveragePerContig, DragenCoverageMetrics, 
                    DragenCoverageHist, DragenFastQcMetrics):
    """ DRAGEN provides a number of differrent pipelines and outputs, including base calling, DNA and RNA alignment,
    post-alignment processing and variant calling, covering virtually all stages of typical NGS data processing.
    However, it can be treated as a fast aligner with additional features on top, as users will unlikely use any
    features without enabling DRAGEN mapping. So we will treat this module as an alignment tool module and
    place it accordingly in the module_order list, in docs, etc.

    The QC metrics DRAGEN generates resemble those of samtools-stats, qualimap, mosdepth, bcftools-stats and alike.
    Whenver possible, the visual output is made similar to those modules.

    Note that this MultiQC module supports some of DRAGEN output but not all. Contributions are welcome!

    The code is structured in a way so every mix-in parses one type of QC file that DRAGEN generates
    (e.g. *.mapping_metrics.csv, *.wgs_fine_hist_normal.csv, etc). If a corresponding file is found, a mix-in adds
    a section into the report.
    """

    def __init__(self):
        super(MultiqcModule, self).__init__(
            name='DRAGEN', anchor='DRAGEN', target='DRAGEN',
            href='https://www.illumina.com/products/by-type/informatics-products/dragen-bio-it-platform.html',
            info=(" is a Bio-IT Platform that provides ultra-rapid secondary analysis of sequencing data"
                  " using field-programmable gate array technology (FPGA)."))

        self.css = { 'assets/css/multiqc_fastqc.css' : os.path.join(os.path.dirname(__file__), '..', 'fastqc', 'assets', 'css', 'multiqc_fastqc.css') }
        self.js = { 'assets/js/multiqc_fastqc.js' : os.path.join(os.path.dirname(__file__), 'assets', 'js', 'multiqc_fastqc.js') }
        self.intro += '<script type="application/json" class="fastqc_passfails">["DRAGEN", {"per_base_sequence_content": {"TEST": "pass"}}]</script>'

        samples_found = set()
        samples_found |= self.add_vc_metrics()
        # <output prefix>.vc_metrics.csv                   - a dedicated table and the total number of Variants into the general stats table

        samples_found |= self.add_ploidy_estimation_metrics()
        # <output prefix>.ploidy_estimation_metrics.csv    - add just Ploidy estimation into gen stats

        #samples_found |= self.add_coverage_hist()
        # <output prefix>.wgs_fine_hist_normal.csv         - coverage distribution and cumulative coverage plots
        # <output prefix>.wgs_fine_hist_tumor.csv          - same

        #samples_found |= self.add_coverage_metrics()
        # <output prefix>.wgs_coverage_metrics_normal.csv  - general stats table and a dedicated table
        # <output prefix>.wgs_coverage_metrics_tumor.csv   - same

        #samples_found |= self.add_coverage_per_contig()
        # <output prefix>.wgs_contig_mean_cov_normal.csv   - a histogram like in mosdepth, with each chrom as a category on X axis, plus a category for autosomal chromosomes average
        # <output prefix>.wgs_contig_mean_cov_tumor.csv    - same

        samples_found |= self.add_mapping_metrics()
        # <output prefix>.mapping_metrics.csv              - general stats table, a dedicated table, and a few barplots

        samples_found |= self.add_fragment_length_hist()
        # <output prefix>.fragment_length_hist.csv         - a histogram plot

        samples_found |= self.add_fastqc_metrics()
        # <output prefix>.fastqc_metrics.csv               - various plots to replicate output from Babraham's FastQC

        if len(samples_found) == 0:
            raise UserWarning
        log.info("Found {} reports".format(len(samples_found)))
