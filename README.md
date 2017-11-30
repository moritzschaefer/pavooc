# PAVOOC

Prediction and visualization of on- and off-targets for CRISPR

# Run it

    python -m pavooc.pipeline

runs everything required to get you started. Additionally there is a docker-environment which should get you started with

    docker-compose up

# Conventions

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

docker-machine create --driver=amazonec2 --amazonec2-instance-type t2.large --amazonec2-region eu-central-1 --amazonec2-root-size=50 machine-name

To connect to it run
eval $(docker-machine env machine-name)

then simply run
docker-compose up

## Swarm

Alternatively Docker Swarm can be used.
A swarm is created the easiest way via the docker cloud web interface

    https://cloud.docker.com/swarm/moritzs/swarm/wizard

Clicking on the created swarm reveals a command to connect to the swarm, e.g.:

    docker run --rm -ti -v /var/run/docker.sock:/var/run/docker.sock -e DOCKER_HOST dockercloud/client moritzs/swarm1

then just run swarm commands to deploy

    docker stack deploy -c docker-compose.yml
