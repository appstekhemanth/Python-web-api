import requests
BASE = "http://127.0.0.1:5000/"

response = requests.get(BASE + "customerid_list")
print(response.json())


response = requests.get(BASE + "/recommendations/40000128")
print(response.json())


response = requests.get(BASE + "/new_product/40000128/R01000006")
print(response.json())


response = requests.get(BASE + "/existing_product/40000128/R01000006")
print(response.json())


# response = requests.get(
#     BASE + "/similar_products/40000128/R01000005/RF6831")
# print(response.json())


response = requests.get(
    BASE + "/basket_analysis/40000128/R01000006/RF1189-TP")
print(response.json())

# def find_data(data,column,id):
#     res = []
#     for sub in data:
#         if sub[column] == id:
#             res.append(sub)
#     print(res)
