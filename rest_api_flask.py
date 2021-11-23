from pickle import APPEND, PUT
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, request
import pandas as pd
# import requests as request
import json

app = Flask(__name__)
api = Api(app)


##############################################################################################################

customer_id_put_args = reqparse.RequestParser()
customer_id_put_args.add_argument('Customer_ID', type=str)
customer_id_put_args.add_argument('Company_Name', type=str)
customer_id_put_args.add_argument('Location', type=str)
customer_id_put_args.add_argument('Country', type=str)
customer_ids = []


class Customers_List(Resource):
    def get(self):
        try:
            # if customer_ids:
            return customer_ids
        except KeyError:
            return 'No Data Found', 404

    def put(self):
        args = customer_id_put_args.parse_args()
        customer_ids.append(args)
        return customer_ids


##############################################################################################################


Category_ids = {}


class Category_List(Resource):
    def get(self, customer_id):
        try:
            # if Category_ids[customer_id]:
            return Category_ids[customer_id]
        except KeyError:
            return 'No Data Found', 404

    def put(self, customer_id):
        args = request.get_json()
        Category_ids[customer_id] = args
        return Category_ids[customer_id]


###############################################################################################################


new_products = {}


class New_Product(Resource):
    def get(self, customer_id, category_id):
        try:
            # if new_products[customer_id][category_id]:
            return new_products[customer_id][category_id]
        except KeyError:
            return 'No Data Found', 404

    def put(self, customer_id, category_id):
        # abort_if_customer_id_exist(customer_id)
        args = request.get_json()
        if customer_id not in new_products:
            new_products[customer_id] = {}
        new_products[customer_id][category_id] = args
        return new_products[customer_id][category_id]

    def delete(self, customer_id, category_id):
        # abort_if_customer_id_doesnot_exist(customer_id)
        del new_products[customer_id][category_id]
        return '', 204


###############################################################################################################


existing_products = {}


class Existing_Product(Resource):
    def get(self, customer_id, category_id):
        try:
            # if existing_products[customer_id][category_id]:
            return existing_products[customer_id][category_id]
        except KeyError:
            return 'No Data Found', 404

    def put(self, customer_id, category_id):
        # abort_if_customer_id_exist(customer_id)
        args = request.get_json()
        if customer_id not in existing_products:
            existing_products[customer_id] = {}
        existing_products[customer_id][category_id] = args
        return existing_products[customer_id][category_id]

    def delete(self, customer_id, category_id):
        # abort_if_customer_id_doesnot_exist(customer_id)
        del existing_products[customer_id][category_id]
        return '', 204


##############################################################################################################


similar_items = {}


class Customer_Similarity_Items(Resource):
    def get(self, category_id, product_id):
        try:
            # if similar_items[customer_id][category_id][product_id]:
            return similar_items[category_id][product_id]
        except KeyError:
            return 'No Data Found', 404

    def put(self, category_id, product_id):
        # abort_if_customer_id_exist(customer_id)
        args = request.get_json()
        if category_id not in similar_items:
            similar_items[category_id] = {}
        similar_items[category_id][product_id] = args
        return similar_items[category_id][product_id]

    def delete(self, category_id, product_id):
        # abort_if_customer_id_doesnot_exist(customer_id)
        del similar_items[category_id][product_id]
        return '', 204


##############################################################################################################


recommend_similar = {}


class Recommend_Similarity_Items(Resource):
    def get(self, customer_id, category_id, product_id):
        try:
            # if recommend_similar[customer_id][category_id][product_id]:
            return recommend_similar[customer_id][category_id][product_id]
        except KeyError:
            return 'No Data Found', 404

    def put(self, customer_id, category_id, product_id):
        # abort_if_customer_id_exist(customer_id)
        args = request.get_json()
        if customer_id not in recommend_similar:
            recommend_similar[customer_id] = {}
        if category_id not in recommend_similar[customer_id]:
            recommend_similar[customer_id][category_id] = {}
        # if product_id not in recommend_similar[customer_id][category_id]:
        #     recommend_similar[customer_id][category_id][product_id] = []
        recommend_similar[customer_id][category_id][product_id] = args
        return recommend_similar[customer_id][category_id][product_id]

    def delete(self, customer_id, category_id, product_id):
        # abort_if_customer_id_doesnot_exist(customer_id)
        del recommend_similar[customer_id][category_id][product_id]
        return '', 204


##############################################################################################################
# api.add_resource(Users, "/users/<int:user_id>")
api.add_resource(Customers_List, "/customerid_list")

api.add_resource(Category_List, "/recommendations/<string:customer_id>")

api.add_resource(New_Product, "/new_product/<string:customer_id>/<string:category_id>")

api.add_resource(Existing_Product,"/existing_product/<string:customer_id>/<string:category_id>")

api.add_resource(Customer_Similarity_Items,"/similar_products/<string:category_id>/<string:product_id>")

api.add_resource(Recommend_Similarity_Items,"/basket_analysis/<string:customer_id>/<string:category_id>/<string:product_id>")

if __name__ == "__main__":
    app.run()
