# -*- coding: utf-8 -*-
import requests
import logging
import os
import re
from bs4 import BeautifulSoup


def get_cookie():
    # Get cookie from environment
    cookie_value = os.environ.get('PEREKRESTOK_COOKIE_VALUE')
    cookie_name = os.environ.get('PEREKRESTOK_COOKIE_NAME')
    if cookie_value is None or cookie_name is None:
        logging.critical("Can not work without perekrestok cookie. Please specify cookie in "
                         "environmental variable 'PEREKRESTOK_COOKIE_VALUE' and 'PEREKRESTOK_COOKIE_NAME'.")
        return
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
                                        cookies={cookie_name: cookie_value})
    if orders_info_response.status_code != 200:
        logging.error(f"Can not get info for order {order_id}")
        return
    return orders_info_response.text


def process_oder(cookie_name, cookie_value, order_id):
    order_info = get_order_content(cookie_name, cookie_value, order_id)
    if order_info is None:
        return
    product_list = []
    try:
        soup = BeautifulSoup(order_info, 'html.parser')
        soup_li_list = soup.find_all('li')
        for line in soup_li_list:
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


if __name__ == "__main__":
    cookie_info = get_cookie()
    if cookie_info is None:
        exit()
    order_info_list = get_order_info_list(cookie_info[0], cookie_info[1])
    if order_info_list is None:
        exit()
    for order_object in order_info_list:
        process_oder(cookie_info[0], cookie_info[1], order_object['id'])

