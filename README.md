# PAVOOC

*Prediction and visualization of on- and off-targets for CRISPR*

**CONTRIBUTIONS welcome**: The software should be easy to set up and work with on your local machine. If you have feature requests, file an issue (along with ideas on how to realize it).

The platform is based on hg19. hg38 is used only for the model generation to be in sync with the azimuth dataset.

# Run it

    python -m pavooc.pipeline

runs everything required to get you started. Additionally there is a docker-environment which should get you started with

    docker-compose up

Note: training requires installation of (cuda) pytorch (http://download.pytorch.org/whl/cpu/torch-0.3.1-cp36-cp36m-linux_x86_64.whl)
Note 2: By default a dump of the database is used to initialize all required data. To compute everything by scratch (probably takes several days), use the ONLY_INIT=0 environment variable (see pipeline.py and docker-compose.yml)

# Conventions

- this is all hg19/GRCh37!
- In the DB 'exons' right now are only the exons for the canonical transcript.. this also means, that in knockout and edit experiments we only consider the canonical transcripts
- canonical exons contain all exons of the canonical transcript MINUS UTR regions
- All sequences are saved in gene-relative direction ('-'-strands are reverse-complemented).
- Ensembl gene IDs are used
- Exon are saved with paddings such that a sgRNA search can find all guides that would cut inside the exon. Forward strand: (16padding)(exon)(6padding), Backward strand: (6padding)(exon)(16padding)

# Datasources

What follows is a list of used datasets

## Reference genome GRCh37

http://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/

## UCSC Pfam

Preprocessed Pfam data which maps protein domains to ucsc coordinates.

ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/ucscGenePfam.{sql,txt.gz}

## Gene annotations (exons included)

http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/refGene.txt.gz
  `bin` smallint(5) unsigned NOT NULL,  `name` varchar(255) NOT NULL,  `chrom` varchar(255) NOT NULL,  `strand` char(1) NOT NULL,  `txStart` int(10) unsigned NOT NULL,  `txEnd` int(10) unsigned NOT NULL,  `cdsStart` int(10) unsigned NOT NULL,  `cdsEnd` int(10) unsigned NOT NULL,  `exonCount` int(10) unsigned NOT NULL,  `exonStarts` longblob NOT NULL,  `exonEnds` longblob NOT NULL,  `score` int(11) default NULL,  `name2` varchar(255) NOT NULL,  `cdsStartStat` enum('none','unk','incmpl','cmpl') NOT NULL,  `cdsEndStat` enum('none','unk','incmpl','cmpl') NOT NULL,  `exonFrames` longblob NOT NULL,

## Protein data

http://www.uniprot.org/downloads

## Cancer cell line per-gene expression data

https://data.broadinstitute.org/ccle_legacy_data/dna_copy_number/CCLE_copynumber_byGene_2013-12-03.txt.gz

# Deployment

## Docker images

In docker-hub there are automated builds for pavooc and the configured nginx server.
Default tag is _latest_ and image names are moritzs/pavooc and moritzs/pavooc-nginx
This speeds up deployment

    docker-compose pull
    docker-compose build # for nginx
    docker-compose up -d

### Manual builds
It is possible to manually build and push the images using

    docker build -t pavooc .
    docker tag pavooc moritzs/pavooc:latest
    docker push moritzs/pavooc:latest
    cd nginx
    docker build -t pavooc-nginx .
    docker tag pavooc moritzs/pavooc-nginx:latest
    docker push moritzs/pavooc-nginx:latest

## AWS docker machine

To create a EC2 instance with docker run

docker-machine create --driver=amazonec2 --amazonec2-instance-type t2.large --amazonec2-region eu-central-1 --amazonec2-root-size=250 machine-name

To connect to it run
eval $(docker-machine env machine-name)

then simply run
docker-compose up

# Future work

## exon expressions

GUIDES (http://guides.sanjanalab.org/) offers a nice way of considering exon expressions. It would be nice and easy to add an expression level to guides in the table in the GeneViewer table.

## improve repository

Tests are not running a.t.m.. Also it would be nice to have automatic PEP8 and TypeScript sanity checks.

## Model features

Adding chromatin accessibility could be a very useful feature..

## Favicon

The website still has the stock react favicon. What a shame!
