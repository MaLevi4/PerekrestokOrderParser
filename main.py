# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import re
import json
from bs4 import BeautifulSoup


def get_cookie():
    # Try to get cookie from environment
    cookie_value = os.environ.get('PEREKRESTOK_COOKIE_VALUE')
    cookie_name = os.environ.get('PEREKRESTOK_COOKIE_NAME')
    if cookie_value is not None and cookie_name is not None:
        return cookie_name, cookie_value
    logging.info("Perekrestok cookie is not found in environmental variables 'PEREKRESTOK_COOKIE_VALUE' and "
                 "'PEREKRESTOK_COOKIE_NAME'. Looking for command line arguments.")

    # Try to get cookie from command line
    if len(sys.argv) != 3:
        logging.critical("Can not work without perekrestok cookie. Please specify cookie in "
                         "environmental variable 'PEREKRESTOK_COOKIE_NAME' and 'PEREKRESTOK_COOKIE_VALUE'. "
                         "Or you can specify cookie name and cookie value as first and second command line arguments.")
        return

    cookie_name = str(sys.argv[1])
    cookie_value = str(sys.argv[2])
    return cookie_name, cookie_value


def get_order_info_list(cookie_name, cookie_value):
    # Get orders list
    orders_list_response = requests.get("https://www.vprok.ru/profile/orders/history",
                                        cookies={cookie_name: cookie_value})
    if orders_list_response.status_code != 200:
        logging.error("Can not get orders list page. Maybe cookie is invalid.")
        return
    order_info_re_pattern = '<div class=\"xf-lk-order__group _number\">\s+<span>Заказ №:</span>\s+<span>' \
                            '(?P<order_id>\d+)</span>\s+</div>\s+<div class=\"xf-lk-order__group _date js-tooltip\"' \
                            ' data-tooltip-text=\"Дата доставки\">\s+<span>Дата:</span>\s+<span>' \
                            '(?P<order_date>[\d\.]+)</span>\s+</div>'
    order_info_list = re.findall(order_info_re_pattern, orders_list_response.text)
    if len(order_info_list) == 0:
        logging.error("Can not parse orders list page.")
        return
    return [{'id': order_object[0], 'date': order_object[1]} for order_object in order_info_list]


def get_order_content(cookie_name, cookie_value, order_id):
    orders_info_response = requests.get(f"https://www.vprok.ru/profile/orders/details/{order_id}/?type=online",
                                        cookies={cookie_name: cookie_value}, timeout=60)
    if orders_info_response.status_code != 200:
        logging.error(f"Can not get info for order {order_id}")
        return
    return orders_info_response.text


def process_oder(cookie_name, cookie_value, order_id):
    logging.info(f"Starting process order {order_id}")
    order_info = get_order_content(cookie_name, cookie_value, order_id)
    if order_info is None:
        return
    product_list = []
    try:
        soup = BeautifulSoup(order_info, 'html.parser')
        soup_li_list = soup.find_all('li')
        for line in soup_li_list:
            if "xf-order-item-unavailable__item" in line["class"]:
                continue
            if "xf-order-item-replaced__item" in line["class"]:
                continue
            product_object = dict()
            product_object['id'] = line["data-owox-product-id"]
            product_object['title'] = line["data-owox-product-name"]
            product_object['link'] = "https://www.vprok.ru" + line.a["href"]
            product_object['img'] = line.a.img["src"]
            product_object['price'] = line.find("div", "xf-order-item__info")["data-cost"]
            product_object['amount'] = line.find("span", "xf-order-item__count-text").text.split(' ')[0]
            product_object['amount_unit'] = line.find("span", "xf-order-item__count-text").text.split(' ')[1]
            product_list.append(product_object)
    except:
        logging.error(f"Can not parse order {order_id} to product list", exc_info=True)
    return product_list


def enrich_products_category(product_list):
    logging.info(f"Starting enrichment of product list with {len(product_list)} entries")
    product_category_dict = {}
    if os.path.isfile('product_category_dict.json'):
        product_category_dict = load_from_file('product_category_dict.json')
        logging.info("Successfully loaded cached file with product to category relation")
    for i in range(len(product_list)):
        if i % 10 == 0:
            logging.info(f"Already processed {i} of {len(product_list)} entries")
        product = product_list[i]
        product_id = product['id']
        logging.debug(f"Starting enrichment for product {product_id}")
        if product_id in product_category_dict:
            product['category'] = product_category_dict[product_id]
            continue
        product_web_page_response = requests.get(product['link'], timeout=60)
        if product_web_page_response.status_code != 200:
            logging.error(f"Can not get web page for product {product_id}")
            logging.info(f"Try to change web-site to 'zoo.vprok.ru' for product {product_id}")
            modified_link = product['link'].replace('www.vprok.ru', 'zoo.vprok.ru')
            product_web_page_response = requests.get(modified_link, timeout=60,
                                                     headers={'User-Agent': 'My User Agent 1.0'})
            if product_web_page_response.status_code != 200:
                logging.error(f"Can not get web page for product {product_id} even after web-site replacement")
                continue
            logging.info(f"Changing web-site to 'zoo.vprok.ru' was successful: updating link for product {product_id}")
            product['link'] = modified_link
        category_tree = re.findall("<span itemprop=\"name\">(.+)</span>", product_web_page_response.text)
        if len(category_tree) == 0:
            logging.warning(f"could not get category for product {product_id}")
        product_category_dict[product_id] = category_tree[-2] + " -> " + category_tree[-1]
        product['category'] = product_category_dict[product_id]
    logging.info(f"Enrichment successfully finished")
    save_to_file(product_category_dict, 'product_category_dict.json')


def save_to_file(content, filename):
    fh = open(filename, 'w+')
    fh.write(json.dumps(content))
    fh.close()


def load_from_file(filename):
    fh = open(filename, 'r')
    content = json.loads(fh.read())
    fh.close()
    return content


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    cookie_info = get_cookie()
    if cookie_info is None:
        exit()
    order_info_list = get_order_info_list(cookie_info[0], cookie_info[1])
    if order_info_list is None:
        exit()
    all_product_list = []
    for order_object in order_info_list:
        product_list = process_oder(cookie_info[0], cookie_info[1], order_object['id'])
        product_list = [{**product_object, "order_id": order_object['id'], "date": order_object['date']}
                        for product_object in product_list]
        all_product_list += product_list
    enrich_products_category(all_product_list)
    save_to_file(all_product_list, 'exported_data.json')
