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
    token = fields.Char(string='Token')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('close', 'Closed'),], string="Status",
                             default="draft")
    
    
    
    def action_check_connection(self):
        for line in self:
            header = {'Accept': 'application/json', "Content-Type": "application/json"}
            header.update({'Authorization': '02c8ee1fb79abbe83faglanz'})
            url = 'https://logistics.zacuta.com/api/get_booking_glanz/json'
            r = requests.get(url, stream=True, verify=False, timeout=10, headers=header)
            data = r.text
            list = json.loads(data)
            raise UserError(list)
