# -*- coding: utf-8 -*-
"""Sale Order"""
from odoo import  models


class SaleOrder(models.Model):
    """Sale Order Model"""
    _inherit = 'sale.order'

    def action_create_so_project(self):
        """Create project from sale order"""
        milestones = {}
        # Creating the project
        project = self.env['project.project'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'company_id':self.company_id.id,
            'user_id': self.env.user.id,
        })
        parent_task = []
        for line in self.order_line:
            if line.milestone not in milestones:
                milestones[line.milestone] = [line.product_template_id.name]
                parent = (self.env['project.task'].create({
                    'name': "Milestone " + str(line.milestone),
                    'project_id': project.id,
                }))
                self.env['project.task'].create({
                    'name': "Milestone " + str(line.milestone) + ' - '+ line.product_template_id.name,
                    'project_id': project.id,
                    'parent_id':parent.id
                })
                parent_task.append(parent)
            else:
                milestones[line.milestone].append(line.product_template_id.name)
                for p in parent_task:
                    if p.name == "Milestone " + str(line.milestone):
                        self.env['project.task'].create({
                            "name": "Milestone " + str(line.milestone) + ' - '+ line.product_template_id.name,
                            "project_id": project.id,
                            "parent_id": p.id,
                        })
