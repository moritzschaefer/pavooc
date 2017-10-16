'''
The server application
'''
# TODO rename gene_ids to ensembl_ids

from flask import Flask, request
from flask_restplus import Resource, Api, fields
from werkzeug.exceptions import BadRequest

import sys
from os import path
# bugfix server debugging
sys.path.append(path.join(path.dirname(path.abspath(__file__)), '../..'))

from pavooc.config import DEBUG  # noqa
from pavooc.db import guide_collection  # noqa


app = Flask(__name__)
api = Api(app)
ns = api.namespace('api', description='API')

knockout_input = api.model('KnockoutInput', {
    'gene_ids': fields.List(fields.String),
    })
knockout_output = api.model('KnockoutGuides', {
    'gene_id': fields.String,
    'guides': fields.List(
        fields.Nested({
            'exon_id': fields.String,
            'start': fields.Integer,
            'otCount': fields.Integer,
            'orientation': fields.String,
            'score': fields.Float
        }))
})


@ns.route('/initial')  # TODO rename
class InitialData(Resource):
    '''
    Initial data like available genes and cancer cell lines
    '''

    def get(self):
        # TODO cancer celllines missing
        gene_ids = guide_collection.find({}, {'gene_id': 1})
        return {'gene_ids': list(gene_ids)}


# TODO make sure only JSON gets accepted
@ns.route('/knockout')
class KnockoutGuides(Resource):
    '''
    Access to the recommendations of all guides
    '''
    @api.expect(knockout_input)
    @api.marshal_with(knockout_output)
    def get(self):
        gene_ids = request.get_json(force=True)['gene_ids']
        if not gene_ids:  # TODO improve
            raise BadRequest('gene_ids not set')

        # TODO here goes all the computation for checking wether SNP and CNSD
        # influence the guides. For now return the 6 best guides
        aggregation_pipeline = [
            # filter our genes
            {'$match': {'gene_id': {'$in': gene_ids}}},
            # unwind guides so we can access their score
            {'$unwind': '$guides'},
            # sort by score
            {'$sort': {'guides.score': -1}},
            # group guides together again (contrary of unwind)
            {'$group': {
                '_id': '$_id',
                'gene_id': {'$first': '$gene_id'},
                'guides': {'$push': '$guides'}
                }},
            # only show first 6 guides
            {'$project': {
                'gene_id': 1,
                'guides': {'$slice': ['$guides', 6]}}}
            ]
        result = guide_collection.aggregate(aggregation_pipeline)
        return list(result)


def main():
    app.run(debug=DEBUG)


if __name__ == '__main__':
    main()
