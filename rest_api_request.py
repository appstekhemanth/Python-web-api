from numpy.testing._private.utils import IgnoreException, break_cycles
import requests
import pandas as pd
import time
import base64

# store starting time
begin = time.time()

BASE = "http://localhost/FlaskRedirect/"

print('Ids Pickle file Start')
ids = pd.read_pickle("ids.pkl")
ids = ids[:20]
print('Ids Pickle file End')

print('customers_data file Start')
customers_data = pd.read_pickle('data.pkl')
print('customers_data file End')

print('Response file Start')
data = pd.read_pickle('response.pkl')
print('Response file End')

data1 = pd.read_excel('customer_productid1.xlsx', index_col=0)

print('Existing pickle file Start')
data2 = pd.read_pickle('existing.pkl')
print('Existing pickle file End')

print('Clusters pickle file Start')
data3 = pd.read_pickle('clusters.pkl')
print('Clusters pickle file End')

print('Clusters ID file Start')
clusters_ids = pd.read_pickle('clusters_ids.pkl')
print('Clusters ID file End')

print('Clusters product file Start')
cluster_products = pd.read_pickle('cluster_products_temp.pkl')
print('Clusters product file End')

print('Quantity file Start')
quanity = pd.read_pickle('quantity.pkl')
print('Quantity file End')

def data_identifier(id):
    lis = clusters_ids[clusters_ids.isin(
        [clusters_ids.loc[id, 'clusters']])].dropna().index.tolist()
    return data1[data1['Customer'].isin(lis)]


def Product_quantity(customer, article, product):
    temp = quanity[quanity['Customer'] == customer][[
        'Article', 'Distributer_producttype', 'Count']]
    temp = temp[temp['Article'] == article][[
        'Distributer_producttype', 'Count']]
    temp = temp[temp['Distributer_producttype'] == product]['Count']
    if temp.empty:
        return 0
    else:
        return int(temp)


def Recommended_quantity(customer, article, product):
    cluster_customers = clusters_ids[clusters_ids['clusters'] == int(
        clusters_ids.loc[customer])].index.tolist()
    items = quanity[quanity['Customer'].isin(cluster_customers)][[
        'Article', 'Distributer_producttype', 'Count']]
    items = items[items['Article'] == article][[
        'Distributer_producttype', 'Count']]
    items = items[items['Distributer_producttype'] == product]['Count']
    if items.empty:
        return 0
    else:
        return int(sum(items))

#############################################Customer_id################################################################################


# for i in ids:
#     response_list = requests.put(BASE + "customerid_list", {'Customer_ID': i,
#                                                             'Customer_Name': customers_data[i]['Customer_type'],
#                                                             'Location': customers_data[i]['City'],
#                                                             'Country': customers_data[i]['Country_name']
#                                                             })

print('Customer_id Start')
for i in customers_data:
    response_list = requests.put(BASE + "customerid_list", {'Customer_ID': customers_data[i]['Customer'],
                                                            'Company_Name': customers_data[i]['Customer_type'],
                                                            'Location': customers_data[i]['City'],
                                                            'Country': customers_data[i]['Country_name']
                                                            })
print('Customer_id End')
############################################Recommendations#############################################################################

print('Recommendations Start')
def to_string(lis):
    sep = ', '
    return sep.join(lis)


def sorting(id, data, column):
    order = data[data['Customer'] == id][[column]]
    dic = {}
    for j in order[column].unique().tolist():
        dic[j] = len(order[order[column] == j])
    return sorted(dic, key=dic.get, reverse=True)


for i in range(len(ids)):
    id = data1[data1['Customer'] == ids[i]][[
        'Desc', 'Hierarchy_3']].drop_duplicates(ignore_index=True)
    # temp = data1[data1['Customer'] == ids[i]][['Hierarchy_3', 'Desc_2']].drop_duplicates(ignore_index=True)
    # break
    categories = []
    for k in sorting(ids[i], data1, 'Hierarchy_3'):
        Desc = data1[data1['Hierarchy_3'] == k]['Desc_2'].unique().tolist()
        # break
        categories.append({'Category_ID': str(k),
                           'Category_Name': str(id[id['Hierarchy_3'] == k]['Desc'].values[0]),
                           'Desc': to_string(list(set(Desc))[:10]),
                           'Category_img': ''})
    response_list = requests.put(BASE + "recommendations/"+str(ids[i]), json={'Total': int(len(id)),
                                                                              'Customer_ID': int(ids[i]),
                                                                              'Categories': categories
                                                                              })

print('Recommendations End')
############################################New_Product#################################################################################

print('New_Product Start')
for i in range(len(ids)):
    main_data = data_identifier(ids[i])
    # customer_data = data[ids[i]]
    customer_data = main_data.copy()
    for cat in customer_data['Hierarchy_3'].unique().tolist():
        category = customer_data[customer_data['Hierarchy_3'] == cat][['Article', 'Distributer_producttype', 'Desc_2', 'Hierarchy_5',
                                                                       'Desc', 'Hierarchy_3', 'Price']].drop_duplicates()
        temp = []
        for j in category['Hierarchy_5'].unique().tolist():
            id = category[category['Hierarchy_5'] == j][['Article', 'Distributer_producttype', 'Desc_2', 'Hierarchy_5',
                                                         'Desc', 'Hierarchy_3', 'Price']].drop_duplicates()
            all_products = customer_data[customer_data['Hierarchy_5'] == j][['Article', 'Distributer_producttype',
                                                                             'Desc', 'Hierarchy_3', 'Price']].drop_duplicates()
            for k in id.index:
                index = all_products[all_products['Article']
                                     == id.loc[k, 'Article']].index
                all_products1 = all_products.drop(index)
                all_products1.drop_duplicates(ignore_index=True, inplace=True)
                dic = []
                for ind in all_products1.index:
                    dic.append({'Product_ID': str(all_products1.loc[ind, 'Article']),
                                'Product_Name': str(all_products1.loc[ind, 'Distributer_producttype']),
                                'Product_Desc': 'its under {}'.format(str(all_products1.loc[ind, 'Desc'])),
                                'Product_Image': '',
                                'Product_Price': int(all_products1.loc[ind, 'Price']),
                                'Quantity': Recommended_quantity(ids[i], str(all_products1.loc[ind, 'Article']), str(all_products1.loc[ind, 'Distributer_producttype']))
                                })
                products = {'Product_ID': str(id.loc[k, 'Article']),
                            'Product_Name': str(id.loc[k, 'Distributer_producttype']),
                            'Product_Desc': 'its under {}'.format(str(id.loc[k, 'Desc'])),
                            'Product_Image': '',
                            'Product_Price': int(id.loc[k, 'Price']),
                            'Quantity': int(Recommended_quantity(customer=int(ids[i]),
                                                                 article=str(id.loc[k, 'Article']), product=str(id.loc[k, 'Distributer_producttype']))),
                            'Similar_Products_Total': int(len(dic)),
                            'Similar_Products': dic
                            }
                temp.append(products)
        new_prod = requests.put(BASE + "new_product/{}/{}".format(str(ids[i]), str(cat)), json={'Total': int(len(temp)),
                                                                                                'Customer_ID': int(ids[i]),
                                                                                                'Category_ID': str(cat),
                                                                                                'Category_Name': str(category['Desc'].unique()[0]),
                                                                                                'Products': temp})
                                                                                               

print('New_Product End')
############################################Existing_product#########################################################################

print('Existing_product Start')
def sorting(data, column, id=None):
    if id:
        order = data[data['Customer'] == id][[column]]
    else:
        order = data
    dic = {}
    for j in order[column].unique().tolist():
        dic[j] = len(order[order[column] == j])
    return sorted(dic, key=dic.get, reverse=True)


for i in range(len(ids)):
    customer_data = data1[data1['Customer'] == ids[i]][['Article', 'Distributer_producttype',
                                                        'Desc_2', 'Hierarchy_5', 'Desc', 'Hierarchy_3', 'Desc_1', 'Price']].drop_duplicates()
    for cat in sorting(data1, 'Hierarchy_3', ids[i]):
        category = customer_data[customer_data['Hierarchy_3'] == cat][['Article', 'Distributer_producttype', 'Desc_2', 'Hierarchy_5',
                                                                       'Desc', 'Hierarchy_3', 'Desc_1', 'Price']].drop_duplicates()
        temp = []
        for j in sorting(category, 'Hierarchy_5'):
            id = category[category['Hierarchy_5'] == j][['Article', 'Distributer_producttype', 'Desc_2', 'Hierarchy_5',
                                                         'Desc', 'Hierarchy_3', 'Desc_1', 'Price']].drop_duplicates()
            all_products = data1[data1['Hierarchy_5'] == j][['Article', 'Distributer_producttype',
                                                             'Desc', 'Hierarchy_3', 'Price']]

            for k in id.index:
                index = all_products[all_products['Article']
                                     == id.loc[k, 'Article']].index
                all_products1 = all_products.drop(index)
                all_products1.drop_duplicates(ignore_index=True, inplace=True)
                dic = []
                for ind in all_products1.index:
                    dic.append({'Product_ID': str(all_products1.loc[ind, 'Article']),
                                'Product_Name': str(all_products1.loc[ind, 'Distributer_producttype']),
                                'Product_Desc': 'its under {}'.format(str(all_products1.loc[ind, 'Desc'])),
                                'Product_Image': '',
                                'Product_Price': int(all_products1.loc[ind, 'Price']),
                                'Quantity': Product_quantity(ids[i], str(all_products1.loc[ind, 'Article']), str(all_products1.loc[ind, 'Distributer_producttype']))
                                })
                products = {'Product_ID': str(id.loc[k, 'Article']),
                            'Product_Name': str(id.loc[k, 'Distributer_producttype']),
                            'Product_Desc': 'its under {}'.format(str(id.loc[k, 'Desc'])),
                            'Product_Image': '',
                            'Product_Price': int(id.loc[k, 'Price']),
                            'Quantity': int(Product_quantity(customer=int(ids[i]),
                                                             article=str(id.loc[k, 'Article']), product=str(id.loc[k, 'Distributer_producttype']))),
                            'Similar_Products_Total': int(len(dic)),
                            'Similar_Products': dic
                            }
                temp.append(products)
        exi_prod = requests.put(BASE + "existing_product/{}/{}".format(str(ids[i]), str(cat)), json={'Total': int(len(temp)),
                                                                                                     'Customer_ID': int(ids[i]),
                                                                                                     'Category_ID': str(cat),
                                                                                                     'Category_Name': str(category['Desc'].unique()[0]),
                                                                                                     'Products': temp
                                                                                                     })
print('Existing_product End')
############################################Similarities################################################################################
print('Similarities Start')
for subcat_id in data1['Hierarchy_5'].unique().tolist():
    id = data1[data1['Hierarchy_5'] == subcat_id][['Article', 'Distributer_producttype',
                                                   'Desc', 'Hierarchy_3', 'Desc_1', 'Desc_2', 'Price']].drop_duplicates(ignore_index=True)

    for j in id.index:
        dic = []
        all_products = id.drop([j])
        for ind in all_products.index:
            item = all_products.loc[ind, 'Distributer_producttype'].replace(
                '"', 'inch').replace('/', '-').replace('*', 'x').replace(':', ' ')
            dic.append({'Product_ID': str(all_products.loc[ind, 'Article']),
                        'Product_Name': str(all_products.loc[ind, 'Distributer_producttype']),
                        'Product_Desc': 'its under {},{},{}'.format(str(all_products.loc[ind, 'Desc']),
                                                                    str(
                                                                        all_products.loc[ind, 'Desc_1']),
                                                                    str(all_products.loc[ind, 'Desc_2'])),
                        'Product_Image': '',
                        'Product_Price': int(all_products.loc[ind, 'Price']),
                        })
        similar = requests.put(BASE + "similar_products/{}/{}".format(str(id['Hierarchy_3'].unique()[0]),
                                                                      str(id.loc[j, 'Article'])),
                               json={'Product_ID': str(id.loc[j, 'Article']),                  'Product_Name': str(id.loc[j, 'Distributer_producttype']),
                                     'Product_Desc': 'its under {},{},{}'.format(str(id.loc[j, 'Desc']),
                                                                                 str(
                                         id.loc[j,
                                                'Desc_1']),
                                   str(
                                         id.loc[j, 'Desc_2'])),
                                     'Category_ID': str(id.loc[j, 'Hierarchy_3']),
                                     'Category_Name': str(id.loc[j, 'Desc']),
                                     'Similiar_Products': dic
                                     })

print('Similarities End')
############################################Clusters####################################################################################
print('Clusters Start')
for i in range(len(ids)):
    cluster_no = clusters_ids.loc[ids[i], 'clusters']
    customer_data = data1[data1['Customer'] == ids[i]][['Article', 'Distributer_producttype', 'Hierarchy_5', 'Desc_1',
                                                        'Desc', 'Desc_2', 'Hierarchy_3', 'Price']].drop_duplicates(ignore_index=True)
    result = [k for k in cluster_products[cluster_no]
              if k in customer_data['Distributer_producttype'].unique().tolist()]
    if result:
        for k in result:
            cus = customer_data[customer_data['Distributer_producttype']
                                == k].drop_duplicates()
            products = []
            id = pd.DataFrame()
            for j in range(len(cluster_products[cluster_no][k])):
                if id.empty:
                    id = cluster_products[cluster_no][k][j][0]
                else:
                    id = id.append(cluster_products[cluster_no][k][j][0])
            id.reset_index(drop=True, inplace=True)
            for ind in id.index:
                # sim = data1[data1['Hierarchy_5'] == id.loc[ind, 'Hierarchy_5']][['Article', 'Distributer_producttype', 'Hierarchy_5', 'Desc_2',
                #                                                                  'Desc', 'Hierarchy_3', 'Price']].drop_duplicates()
                # sim_index = sim[sim['Article'] == id.loc[ind, 'Article']].index
                # all_products = sim.drop(sim_index)
                # dic = []
                # for sim_index in all_products.index:
                #     dic.append({'Product_ID': str(all_products.loc[sim_index, 'Article']),
                #                 'Product_Name': str(all_products.loc[sim_index, 'Distributer_producttype']),
                #                 'Product_Desc': 'its under {}'.format(str(all_products.loc[sim_index, 'Desc'])),
                #                 'Product_Image': '',
                #                 'Product_Price': int(all_products.loc[sim_index, 'Price'])
                #                 })

                products.append({'Product_ID': str(id.loc[ind, 'Article']),
                                 'Product_Name': str(id.loc[ind, 'Distributer_producttype']),
                                 'Product_Desc': 'its under {}'.format(str(id.loc[ind, 'Desc'])),
                                 'Confidence': '{:.2%}'.format(cluster_products[cluster_no][k][j][1]),
                                 'Product_Image': '',
                                 'Product_Price': int(id.loc[ind, 'Price']),
                                 'Quantity': Recommended_quantity(ids[i], str(id.loc[ind, 'Article']), str(id.loc[ind, 'Distributer_producttype']))
                                 #  'Similar_Products_Total': int(len(dic)),
                                 #  'Similar_Products': dic
                                 })
            dic1 = []
            for mar_index in cus.index:
                sim = data1[data1['Hierarchy_5'] == cus.loc[mar_index, 'Hierarchy_5']][['Article', 'Distributer_producttype', 'Hierarchy_5', 'Desc_2',
                                                                                        'Desc', 'Hierarchy_3', 'Price']].drop_duplicates()
                sim_index = sim[sim['Article'] == id.loc[ind, 'Article']].index
                all_products = sim.drop(sim_index)
                for sim_mar_index in all_products.index:
                    dic1.append({'Product_ID': str(all_products.loc[sim_mar_index, 'Article']),
                                 'Product_Name': str(all_products.loc[sim_mar_index, 'Distributer_producttype']),
                                 'Product_Desc': 'its under {}'.format(str(all_products.loc[sim_mar_index, 'Desc'])),
                                 'Product_Image': '',
                                 'Product_Price': int(all_products.loc[sim_mar_index, 'Price']),
                                 'Quantity': Recommended_quantity(ids[i], str(all_products.loc[sim_mar_index, 'Article']), str(all_products.loc[sim_mar_index, 'Distributer_producttype']))
                                 })
            customer_sim = requests.put(BASE + "basket_analysis/{}/{}/{}".format(str(ids[i]), str(cus['Hierarchy_3'].unique()[0]), str(cus['Article'].unique()[0])),
                                        json={'Total': int(len(id)),
                                              'Customer_ID': int(ids[i]),
                                              'Category_ID': str(cus['Hierarchy_3'].unique()[0]),
                                              'Category_Name': str(cus['Desc'].unique()[0]),
                                              'Product_ID': str(cus['Article'].unique()[0]),
                                              'Product_Name': str(cus['Distributer_producttype'].unique()[0]),
                                              'Description': '{},{},{}'.format(str(cus['Desc'].unique()[0]), str(cus['Desc_1'].unique()[0]), str(cus['Desc_2'].unique()[0])),
                                              'Similar_Products_Total': int(len(dic1)),
                                              'Similar_Products': dic1,
                                              'Basket_Analysis_Products': products})

print('Clusters End')
# store end time
end = time.time()

# total time taken
print(f"Total runtime of the program is {end - begin}")
