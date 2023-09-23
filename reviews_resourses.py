from flask_restful import abort, Resource
from data import db_session
from data.reviews import Review
from flask.json import jsonify
import datetime


def abort_if_review_not_found(id):
    session = db_session.create_session()
    review = session.query(Review).get(id)
    if not review:
        abort(404, message=f"Review {id} not found")


class ReviewsResource(Resource):
    def get(self, id):
        abort_if_review_not_found(id)
        session = db_session.create_session()
        review = session.query(Review).get(id)
        return jsonify({'review': review.to_dict(
                only=('id', 'user_id', 'user_name', 'user_surname', 'rating',
                      'content', 'date'))})

    def delete(self, id):
        abort_if_review_not_found(id)
        session = db_session.create_session()
        review = session.query(Review).get(id)
        session.delete(review)
        session.commit()
        return jsonify({'success': 'OK'})


class ReviewsListResource(Resource):
    def get(self, rating):
        session = db_session.create_session()
        if not rating:
            reviews = session.query(Review).all()
            return jsonify({'reviews': [item.to_dict(
                    only=('id', 'user_id', 'user_name', 'user_surname', 'rating',
                          'content', 'date')) for item in reviews]})
        elif rating in range(1, 6):
            reviews = session.query(Review).filter(Review.rating == rating)
            return jsonify({'reviews': [item.to_dict(
                    only=('id', 'user_id', 'user_name', 'user_surname', 'rating',
                          'content', 'date')) for item in reviews]})
        else:
            return abort(400, message=f"Bad rating request")
