# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
import base64
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class ZacutaConnector(models.Model):
    _name = 'zacuta.instance'
    _description = 'Zacuta Instance'

    name = fields.Char(string='Name')
    url = fields.Char(string='URL')
    response_json = fields.Char(string='Data')
    token = fields.Char(string='Token')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Closed'),], string="Status",
                             default="draft")
    
    
    
    def action_fetch_data(self):
        header = {'Accept': 'application/json', "Content-Type": "application/json"}
        header.update({'ApiToken': str(self.token)})
        url = str(self.url)
        req = requests.request('POST', url, headers=header)
        data_list = req.content
        final_list = json.loads(data_list)
        inner_count = 0
        for data in final_list['bookings']:
            inner_count+=1
            if inner_count == 10:
                break
            vals = {
               'zid': data['id'],
               'user_id': data['user_id'],
               'sheet_id': data['sheet_id'],
               'booking_date': data['booking_date'],
                'promo': data['promo'],
               'status': data['status'],
               'remarks': data['remarks'],
                'cn_number': data['cn_number'],
               'shipper_id': data['shipper_id'],
               'consignment_name': data['consignment_name'],
                'consignee_email': data['consignee_email'],
               'consignment_addres': data['consignment_addres'],
               'consignment_phone_number': data['consignment_phone_number'],
               'designation': data['designation'],
                'order_id': data['order_id'],
               'tracking_number': data['tracking_number'],
               'cod_amount': data['cod_amount'],
                'tax': data['tax'],
               'comment': data['comment'],
               'assigned_to': data['assigned_to'],
                'rts': data['rts'],
               'weight': data['weight'],
               'delivery_price': data['delivery_price'],
               'discount': data['discount'],
                'advance': data['advance'],
               'added_by': data['added_by'],
               'last_edit_by': data['last_edit_by'],
                'created_at': data['created_at'],
               'updated_at': data['updated_at'],
               'deposit_type': data['deposit_type'],
                'deposit_status': data['deposit_status'],
               'deposit_accept_date': data['deposit_accept_date'],
               'bank_trans_details': data['bank_trans_details'],
               'reminder_comments': data['reminder_comments'],
                'reminder_date': data['reminder_date'],
               'reminder': data['reminder'],
               'reminder_flag': data['reminder_flag'],
                'source': data['source'],
               'shopify_order_id': data['shopify_order_id'],
               'shipper_tracking_id': data['shipper_tracking_id'],
                'return_remarks': data['return_remarks'],
               'attempt': data['attempt'],
               'shipper_last_status': data['shipper_last_status'],
               'shipper_shipping_stats': data['shipper_shipping_stats'],
                'booking_complete_status': data['booking_complete_status'],
               'fetched': data['fetched'],
               'shipper_slip_link': data['shipper_slip_link'],
                'province': data['province'],
               'commission': data['commission'],
            }
            order = self.env['zacuta.order'].create(vals)
            for product in data['products']:
                product_vals = {
                    'name': product['name'],
                    'quantity': product['quantity'],
                    'price': product['price'],
                    'order_id': order.id,
                }
                order_line = self.env['zacuta.order.line'].create(product_vals)
            for pay in data['shipper_shipping_stats']:
                pay_vals = {
                    'cn_number': pay['cn_number'],
                    'billing_method': pay['billing_method']
                    'invoice_cheque_no': pay['invoice_cheque_no'],
                    'invoice_cheque_date': pay['invoice_cheque_date'],
                    'weight_charged': pay['weight_charged'],
                    'shipment_charges': pay['shipment_charges'],
                    'cash_handling_charges': pay['cash_handling_charges'],
                    'return_charges': pay['return_charges'],
                    'insurance_charges': pay['insurance_charges'],
                    'fuel_surcharge_percentage': pay['fuel_surcharge_percentage'],
                    'fuel_surcharge_amount': pay['fuel_surcharge_amount'],
                    'gst': pay['gst'],
                    'gst_amount': pay['gst_amount'],
                    'net_charges': pay['net_charges'],
                    'gross_charges': pay['gross_charges'],
                    'order_id': order.id,
                }
                pay_line = self.env['zacuta.pay.line'].create(pay_vals)  
            for shipper in data['shipper']:
                shipper_vals = {
                    'id': shipper['id'],
                    'name': shipper['name'],
                    'email': shipper['email'],
                    'phone_number': shipper['phone_number'],
                    'address': shipper['address'],
                     'origin_city': shipper['origin_city'],
                    'created_at': shipper['created_at'],
                    'updated_at': shipper['updated_at'],
                    'api_status': shipper['api_status'],
                    'order_id': order.id,
                }
                shipper_line = self.env['zacuta.shipper.line'].create(shipper_vals)  
            for rider in data['rider']:
                rider_vals = {
                    'id': rider['id'],
                     'name': rider['name'],
                    'username': rider['username'],
                    'password': rider['password'],
                    'token': rider['token'],
                     'phone': rider['phone'],
                    'address': rider['address'],
                    'delete_status': rider['delete_status'],
                    'status': rider['status'],
                    'created_at': rider['created_at'],
                    'updated_at': rider['updated_at'],
                    'order_id': order.id,
                }
                rider_line = self.env['zacuta.rider.line'].create(rider_vals)      

    
    def action_check_connection(self):
        for line in self:
            header = {'Accept': 'application/json', "Content-Type": "application/json"}
            header.update({'ApiToken': str(line.token)})
            url = str(line.url)
            req = requests.request('POST', url, headers=header)
            raise UserError(str(req))
#             if req.status_code=='200':
#                 raise UserError('Successfully connected to Zacuta Instance!')
            
            
