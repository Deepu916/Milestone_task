# -*- coding: utf-8 -*-
"""Sale Order"""
from odoo import  fields,models,api


class SaleOrder(models.Model):
    """Sale Order Model"""
    _inherit = 'sale.order'


    project_id = fields.Many2one('project.project',string="Project")
    created = fields.Boolean(string="Create Date")
    parents = {}
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
        for line in self.order_line:
            milestone_key = line.milestone
            if milestone_key not in milestones:
                parent = self.env['project.task'].create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                    'sale_order_id':self.id,
                    'sale_line_id':line.id,

                })
                milestones[milestone_key] = parent
                self.parents[milestone_key] = parent
            self.env['project.task'].create({
                'name': "Milestone " + str(milestone_key)+ "-" + line.product_template_id.name,
                'project_id': self.project_id.id,
                'parent_id': milestones[milestone_key].id,
                'sale_order_id': self.id,
                'sale_line_id': line.id,
            })

    def action_update_so_project(self):
        """Update project from sale order"""
        print("Parents",self.parents)
        Task = self.env['project.task']
        existing_tasks = self.project_id.task_ids
        task_mapping ={}
        for task in existing_tasks:
            if task.sale_line_id:
                task_mapping[task.sale_line_id.id] = task
        for line in self.order_line:
            milestone_key = line.milestone
            if milestone_key not in self.parents:
                parent = Task.create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })

                self.parents[milestone_key] = parent
            if self.parents[milestone_key] not in self.env['project.task'].search([('project_id','=',self.project_id.id)]):
                parent = self.env['project.task'].create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })
                self.parents[milestone_key] = parent
            existing_parent_id = self.parents[milestone_key]
            existing_task = task_mapping.get(line.id)
            if not existing_task and line.product_uom_qty > 0:
                Task.create({
                    'name': "Milestone " + str(milestone_key) + "-" + line.product_template_id.name,
                    'project_id': self.project_id.id,
                    'parent_id': existing_parent_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })

        task_to_delete = existing_tasks.filtered(lambda task: task.sale_line_id.product_uom_qty == 0)
        task_to_delete.unlink()
        print(self.parents)
