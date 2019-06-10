'''
The server application
'''
# TODO rename gene_ids to ensembl_ids

import os
import sys
import tempfile
import time
from os import path

from flask import Flask, request
from flask_restplus import Api, Resource, fields
from pyfaidx import Fasta
from werkzeug.exceptions import BadRequest

from pavooc.config import BASEDIR, DEBUG, GENOME, GENOME_FILE  # noqa
from pavooc.data import celllines, gencode_exons
from pavooc.db import guide_collection  # noqa
from pavooc.preprocessing.exon_guide_search import generate_edit_guides
from pavooc.preprocessing.generate_guide_bed import guides_to_bed

# bugfix server debugging
sys.path.append(path.join(path.dirname(path.abspath(__file__)), '../..'))


app = Flask(__name__)
api = Api(app, doc='/api/')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

ns = api.namespace('api', description='API')

guide_field = fields.Nested(api.model('Guide', {
    'exon_id': fields.String,
    'target': fields.String,
    'start': fields.Integer,
    'cut_position': fields.Integer,
    'aa_cut_position': fields.Integer,
    'otCount': fields.Integer,
    'orientation': fields.String,
    'mutations': fields.List(fields.String),
    'scores': fields.Nested(api.model('Score', {
        'azimuth': fields.Float,
        'pavooc': fields.Float,
        # 'Doench2014OnTarget': fields.Float,
        'Doench2016CFDScore': fields.Float,
        # 'dangerous_GC': fields.String,
        # 'dangerous_polyT': fields.String,
        # 'dangerous_in_genome': fields.String,
        'Hsu2013': fields.Float
    })),
}))

pdb_field = fields.Nested(api.model('PDB', {
    'pdb': fields.String,
    'start': fields.Integer,
    'end': fields.Integer,
    'chain': fields.String,
    'swissprot_id': fields.String,
    'mappings': fields.Raw,
}))

exon_field = fields.Nested(api.model('Exon', {
    'start': fields.Integer,
    'end': fields.Integer,
    'exon_id': fields.String,
}))

edit_input = api.model('EditInput', {
    'gene_id': fields.String,
    'edit_position': fields.Integer,
    'padding': fields.Integer,
})

edit_output = api.model('EditGuides', {
    'bed_url': fields.String,
    'guides_before': fields.List(guide_field),
    'guides_after': fields.List(guide_field),
    'mutations': fields.List(fields.String, default=[]),
    'sequence': fields.String,
    'edit_position': fields.Integer,
})

knockout_input = api.model('KnockoutInput', {
    'gene_ids': fields.List(fields.String),
    'edit': fields.Boolean(default=False),
    'genome': fields.String()
})

knockout_output = api.model('KnockoutGuides', {
    'gene_id': fields.String,
    'gene_symbol': fields.String,
    'chromosome': fields.String,
    'strand': fields.String,
    'cns': fields.List(fields.String),
    'exons': fields.List(exon_field),
    'sequence': fields.String(default=''),
    'domains': fields.List(
        fields.Nested(api.model('Domain', {
            'name': fields.String,
            'start': fields.Integer,
            'end': fields.Integer
        })), default=[]),
    'pdbs': fields.List(pdb_field, default=[]),
    'guides': fields.List(guide_field)
})


gene_details_input = api.model('GeneDetailsInput', {
    'gene_id': fields.String,
    'genome': fields.String
})


gene_details = api.model('GeneDetails', {
    'gene_id': fields.String,
    'gene_symbol': fields.String,
    'pdbs': fields.List(pdb_field, default=[]),
    'exons': fields.List(exon_field),
    'cns': fields.List(fields.String, default=[]),
    'chromosome': fields.String,
    'strand': fields.String,
    'start': fields.Integer,
    'end': fields.Integer,
})


initial_output = api.model('InitialData', {
    'genes': fields.List(fields.Nested(api.model('Gene', {
        'gene_id': fields.String(),
        'gene_symbol': fields.String(),
    }))),
    'celllines': fields.List(fields.String)
})


@ns.route('/initial')  # TODO rename
class InitialData(Resource):
    '''
    Initial data like available genes and cancer cell lines
    '''

    @api.marshal_with(initial_output)
    def get(self):
        # fields = ['gene_id', 'gene_symbol',
                 #  'chromosome', 'start', 'end', 'strand', 'pdbs', 'exons']
        # genes = guide_collection.aggregate([
        #     {"$unwind": "$exons"},
        #     {"$group": {
        #         "_id": "$_id",
        #         "gene_id": {"$first": "$gene_id"},
        #         "pdbs": {"$first": "$pdbs"},
        #         "gene_symbol": {"$first": "$gene_symbol"},
        #         "exons": {"$push": "$exons"},
        #         "strand": {"$first": "$strand"},
        #         "start": {"$min": "$exons.start"},
        #         "chromosome": {"$first": "$chromosome"},
        #         "end": {"$max": "$exons.end"}}}], allowDiskUse=True)
        # genes = [{field: v[field] for field in fields} for v in genes]

        genes = guide_collection.find(
            {}, projection=['gene_id', 'gene_symbol', 'genome'])

        return {'genes': list(genes), 'celllines': celllines()}


# TODO make sure only JSON gets accepted
@ns.route('/knockout')
class KnockoutGuides(Resource):
    '''
    Access to the recommendations of all guides
    '''
    @api.expect(knockout_input)
    @api.marshal_with(knockout_output)
    def post(self):
        gene_ids = request.get_json(force=True)['gene_ids']
        edit = request.get_json(force=True)['edit']
        genome = request.get_json(force=True)['genome']
        if not gene_ids:  # TODO improve
            raise BadRequest('gene_ids not set')

        if genome not in ['hg19', 'mm10']:  #
            raise BadRequest(f'{genome} not supported')

        if edit and len(gene_ids) != 1:
            raise BadRequest('gene_ids needs to have length 1 if editing..')


        # TODO here goes all the computation for checking wether SNP and CNSD
        # influence the guides. For now return the 6 best guides
        aggregation_pipeline = [
            # filter our genes
            {'$match': {'$and': [{'gene_id': {'$in': gene_ids}}, {'genome': genome} ]}},
            # unwind guides so we can access their score
            # {'$unwind': '$guides'},
            # # sort by score
            # {'$sort': {'guides.score': -1}},
            # # group guides together again (contrary of unwind)
            # {'$group': {
            #     '_id': '$_id',
            #     'gene_id': {'$first': '$gene_id'},
            #     'chromosome': {'$first': '$chromosome'},
            #     'pdbs': {'$first': '$pdbs'},
            #     'exons': {'$first': '$exons'},
            #     'guides': {'$push': '$guides'}
            # }},
        ]
        result = list(guide_collection.aggregate(aggregation_pipeline))
        if edit:
            df = gencode_exons(genome)
            exons = df[(df.gene_id == gene_ids[0])]
            chromosome = exons.seqname.iloc[0]
            # TODO here i have to change things..
            fasta = Fasta(GENOME_FILE.format(GENOME), as_raw=True)

            seq = fasta[chromosome][min(exons.start):max(exons.end)]
            # if self.strand == '-':  # i think this is done on the client...
            #     seq = seq.reverse.complement
            result[0]['sequence'] = seq
        return result


@ns.route('/details')
class Details(Resource):
    @api.expect(gene_details_input)
    @api.marshal_with(gene_details)
    def post(self):
        data = request.get_json(force=True)
        gene_id = data['gene_id']
        genome = data['genome']

        if not gene_id:  # TODO improve
            raise BadRequest('gene_id not set')

        gene_data = guide_collection.aggregate([
            {"$match": {"$and": [{"gene_id": gene_id}, {"genome": genome}]}},
            {"$unwind": "$exons"},
            {"$group": {
                "_id": "$_id",
                "gene_id": {"$first": "$gene_id"},
                "gene_symbol": {"$first": "$gene_symbol"},
                "pdbs": {"$first": "$pdbs"},
                "cns": {"$first": "$cns"},
                "exons": {"$push": "$exons"},
                "strand": {"$first": "$strand"},
                "start": {"$min": "$exons.start"},
                "chromosome": {"$first": "$chromosome"},
                "end": {"$max": "$exons.end"}}}])

        # gene_data = [{field: v[field] for field in fields} for v in genes]

        return next(gene_data)


# TODO edit is not necessary anymore.. also I didnot apply multi genome changes..
@ns.route('/edit')
class EditGuides(Resource):
    @api.expect(edit_input)
    @api.marshal_with(edit_output)
    def post(self):
        data = request.get_json(force=True)
        gene_id = data['gene_id']
        edit_position = data['edit_position']

        if not gene_id:  # TODO improve
            raise BadRequest('gene_id not set')
        gene_data = guide_collection.find_one({'gene_id': gene_id})

        output = {}
        output['edit_position'] = edit_position
        # TODO sequence to upper case in generate_edit_guides?
        output['sequence'], output['guides_before'], output['guides_after'] = \
            generate_edit_guides(
            gene_id,
            gene_data['chromosome'],
            edit_position,
            offset=data['padding'])

        bed_url = f'{time.time()}.guides.bed'
        guides_to_bed(output['guides_before'] + output['guides_after'],
                      gene_data,
                      os.path.join(BASEDIR, 'webapp/public/', bed_url))
        output['bed_url'] = f'/{bed_url}'

        return output


def main():
    # call them so that their results get buffered and are fastly accessible
    for g in ['mm10', 'hg19']:
        gencode_exons()
    app.run(debug=DEBUG, host='0.0.0.0')


if __name__ == '__main__':
    main()
