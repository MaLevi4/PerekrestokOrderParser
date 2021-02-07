# -*- coding: utf-8 -*-
import requests
import logging
import os
import re


def get_cookie():
    # Get cookie from environment
    cookie_value = os.environ.get('PEREKRESTOK_COOKIE_VALUE')
    cookie_name = os.environ.get('PEREKRESTOK_COOKIE_NAME')
    if cookie_value is None or cookie_name is None:
        logging.critical("Can not work without perekrestok cookie. Please specify cookie in "
                         "environmental variable 'PEREKRESTOK_COOKIE_VALUE' and 'PEREKRESTOK_COOKIE_NAME'.")
        return
    return (cookie_name, cookie_value)


def get_order_id_list(cookie_name, cookie_value):
    # Get orders list
    orders_list_response = requests.get("https://www.vprok.ru/profile/orders/history", cookies={cookie_name: cookie_value})
    if orders_list_response.status_code != 200:
        logging.error("Can not get orders list page. Maybe cookie is invalid.")
        return
    order_id_list = re.findall("https://www\.vprok\.ru/profile/orders/status/(?P<order_id>\d+)", orders_list_response.text)
    if len(order_id_list) == 0:
        logging.error("Can not parse orders list page.")
        return
    return order_id_list


def get_order_info_list(cookie_name, cookie_value):
    # Get orders list
    orders_list_response = requests.get("https://www.vprok.ru/profile/orders/history", cookies={cookie_name: cookie_value})
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
    product_re_pattern = 'data-owox-product-id=\"(?P<product_id>\d+)\"\s+data-owox-product-name=\"(?P<product_name>[^\"]+)\"[\S\s]+?data-cost=\"(?P<product_cost>[\d\.]+)\"'
    product_list = re.findall(product_re_pattern, order_info)
    if len(product_list) == 0:
        logging.error(f"Can not parse order {order_id} to product list")
        return
    print (product_list)
    return


if __name__ == "__main__":
    cookie_info = get_cookie()
    if cookie_info is None:
        exit()
    order_info_list = get_order_info_list(cookie_info[0], cookie_info[1])
    if order_info_list is None:
        exit()
    for order_object in order_info_list:
        process_oder(cookie_info[0], cookie_info[1], order_object['id'])

