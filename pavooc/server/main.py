'''
The server application
'''
# TODO rename gene_ids to ensembl_ids

from flask import Flask, request
from flask_restplus import Resource, Api, fields
from werkzeug.exceptions import BadRequest

import os
import time
import tempfile
import sys
from os import path
# bugfix server debugging
sys.path.append(path.join(path.dirname(path.abspath(__file__)), '../..'))

from pavooc.preprocessing.generate_guide_bed import guides_to_bed
from pavooc.config import DEBUG, BASEDIR  # noqa
from pavooc.db import guide_collection  # noqa
from pavooc.data import celllines, read_gencode
from pavooc.preprocessing.exon_guide_search import generate_edit_guides


app = Flask(__name__)
api = Api(app)
ns = api.namespace('api', description='API')

guide_field = fields.Nested({
    'exon_id': fields.String,
    'target': fields.String,
    'start': fields.Integer,
    'cut_position': fields.Integer,
    'aa_cut_position': fields.Integer,
    'otCount': fields.Integer,
    'orientation': fields.String,
    'mutations': fields.List(fields.String),
    'scores': fields.Nested({
        'azimuth': fields.Float,
        # 'Doench2014OnTarget': fields.Float,
        'Doench2016CFDScore': fields.Float,
        # 'dangerous_GC': fields.String,
        # 'dangerous_polyT': fields.String,
        # 'dangerous_in_genome': fields.String,
        'Hsu2013': fields.Float
    }),
})

pdb_field = fields.Nested({
    'pdb': fields.String,
    'start': fields.Integer,
    'end': fields.Integer,
    'chain': fields.String,
    'swissprot_id': fields.String,
    'mappings': fields.Raw,
})

edit_input = api.model('EditInput', {
    'gene_id': fields.String,
    'edit_position': fields.Integer,
    'padding': fields.Integer,
})

edit_output = api.model('EditGuides', {
    'bed_url': fields.String,
    'guides_before': fields.List(guide_field),
    'guides_after': fields.List(guide_field),
    'sequence': fields.String,
    'edit_position': fields.Integer,
    # 'pdbs': fields.List(pdb_field, default=[]),
    'canonical_exons': fields.List(fields.Nested({
        'start': fields.Integer,
        'end': fields.Integer,
        'exon_id': fields.String
    })
    )
})

knockout_input = api.model('KnockoutInput', {
    'gene_ids': fields.List(fields.String),
})

knockout_output = api.model('KnockoutGuides', {
    'gene_id': fields.String,
    'gene_symbol': fields.String,
    'chromosome': fields.String,
    'cns': fields.List(fields.String),
    'exons': fields.List(
        fields.Nested({
            'start': fields.Integer,
            'end': fields.Integer,
            'exon_id': fields.String,
        })),
    'domains': fields.List(
        fields.Nested({
            'name': fields.String,
            'start': fields.Integer,
            'end': fields.Integer
        }), default=[]),
    'pdbs': fields.List(pdb_field, default=[]),
    'guides': fields.List(guide_field)
})

initial_output = api.model('InitialData', {
    'genes': fields.List(fields.Nested({
        'pdbs': fields.List(pdb_field, default=[]),  # TODO is this too much?
        'gene_id': fields.String,
        'gene_symbol': fields.String,
        'chromosome': fields.String,
        'strand': fields.String,
        'start': fields.Integer,
        'end': fields.Integer,
    })),
    'celllines': fields.List(fields.String)
})


@ns.route('/initial')  # TODO rename
class InitialData(Resource):
    '''
    Initial data like available genes and cancer cell lines
    '''

    @api.marshal_with(initial_output)
    def get(self):
        fields = ['gene_id', 'gene_symbol',
                  'chromosome', 'start', 'end', 'strand', 'pdbs']
        genes = guide_collection.aggregate([
            {"$unwind": "$exons"},
            {"$group": {
                "_id": "$_id",
                "gene_id": {"$first": "$gene_id"},
                "pdbs": {"$first": "$pdbs"},
                "gene_symbol": {"$first": "$gene_symbol"},
                "strand": {"$first": "$strand"},
                "start": {"$min": "$exons.start"},
                "chromosome": {"$first": "$chromosome"},
                "end": {"$max": "$exons.end"}}}])
        genes = [{field: v[field] for field in fields} for v in genes]

        return {'genes': genes, 'celllines': celllines()}


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
        if not gene_ids:  # TODO improve
            raise BadRequest('gene_ids not set')

        # TODO here goes all the computation for checking wether SNP and CNSD
        # influence the guides. For now return the 6 best guides
        aggregation_pipeline = [
            # filter our genes
            {'$match': {'gene_id': {'$in': gene_ids}}},
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
        result = guide_collection.aggregate(aggregation_pipeline)
        return list(result)


# TODO make sure only JSON gets accepted
@ns.route('/edit')
class EditGuides(Resource):
    '''
    Access to the recommendations of all guides
    '''
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
            gene_id, gene_data['chromosome'], edit_position)

        output['pdbs'] = gene_data['pdbs']
        output['canonical_exons'] = gene_data['canonical_exons']

        bed_url = f'{time.time()}.guides.bed'
        guides_to_bed(output['guides_before'] + output['guides_after'],
                      gene_data,
                      os.path.join(BASEDIR, 'webapp/public/', bed_url))
        output['bed_url'] = f'/{bed_url}'

        return output


def main():
    app.run(debug=DEBUG, host='0.0.0.0')


if __name__ == '__main__':
    main()
