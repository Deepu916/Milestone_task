# -*- coding: utf-8 -*-
"""Sale Order Line Model."""
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """ Model for sale order line """
    _inherit = "sale.order.line"

    milestone = fields.Integer(string="Milestone",default=1,required=True)