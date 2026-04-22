# -*- coding: utf-8 -*-
"""Sale Order"""
from odoo import  fields,models


class SaleOrder(models.Model):
    """Sale Order Model"""
    _inherit = 'sale.order'


    project_id = fields.Many2one('project.project',string="Project")
    created = fields.Boolean(string="Create Date")
    def action_create_so_project(self):
        """Create project from sale order"""
        milestones = {}
        # Creating the project
        self.project_id = self.env['project.project'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'company_id':self.company_id.id,
            'user_id': self.env.user.id,
        })
        self.created = True
        names = ['New','In Progress','Done','Cancelled']
        demo = self.env['project.task.type'].search([('name','in',names),('user_id','!=',self.env.user.id)])
        demo.write({'project_ids':[fields.Command.link(self.project_id.id)]})
        self.project_count = len(self.project_id)
        for line in self.order_line:
            milestone_key = line.milestone
            if milestone_key not in milestones:
                parent = self.env['project.task'].create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                })
                milestones[milestone_key] = parent
            self.env['project.task'].create({
                'name': "Milestone " + str(milestone_key)+ "-" + line.product_template_id.name,
                'project_id': self.project_id.id,
                'parent_id': milestones[milestone_key].id,
            })
        