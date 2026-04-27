# -*- coding: utf-8 -*-
"""Sale Order"""
from odoo import  fields,models


class SaleOrder(models.Model):
    """Sale Order Model"""
    _inherit = 'sale.order'


    project_id = fields.Many2one('project.project',string="Project")
    created = fields.Boolean(string="Create Date")
    parents = {}
    line_milestone ={}
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
        demo = self.env['project.task.type'].search([
            ('name','in',names),
            ('user_id','!=',self.env.user.id)
        ])
        demo.write({'project_ids':[fields.Command.link(self.project_id.id)]})
        for line in self.order_line:
            self.line_milestone[line.id] = line.milestone
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
        task = self.env['project.task']
        existing_tasks = self.project_id.task_ids
        task_mapping ={}
        for task in existing_tasks:
            if task.sale_line_id:
                task_mapping[task.sale_line_id.id] = task
        for line in self.order_line:
            # self.line_milestone[line.id] = line.milestone
            milestone_key = line.milestone
            if milestone_key not in self.parents:
                parent = task.create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })

                self.parents[milestone_key] = parent
            # Parent task creation if parent task is deleted and creating task for the same milestone of deleted parent task
            if (self.parents[milestone_key] not in
                    self.project_id.task_ids
                    and line.milestone >0) :
                parent = self.env['project.task'].create({
                    'name': "Milestone " + str(milestone_key),
                    'project_id': self.project_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })
                self.parents[milestone_key] = parent
            existing_parent_id = self.parents[milestone_key]
            existing_task = task_mapping.get(line.id)
            if not existing_task and line.milestone > 0:
                task.create({
                    'name': "Milestone " + str(milestone_key) + "-" + line.product_template_id.name,
                    'project_id': self.project_id.id,
                    'parent_id': existing_parent_id.id,
                    'sale_order_id': self.id,
                    'sale_line_id': line.id,
                })
                self.line_milestone[line.id] = line.milestone

            if (self.line_milestone[line.id] != line.milestone) and line.milestone > 0:
                print(existing_task.child_ids)
                existing_task.write({
                    'name': "Milestone " + str(milestone_key) + "-" + line.product_template_id.name,
                    'parent_id': existing_parent_id.id,
                    'sale_order_id': self.id,
                    # 'sale_line_id': line.id,
                })
                self.line_milestone[line.id] = line.milestone
        print(self.line_milestone)
        task_to_delete = existing_tasks.filtered(lambda task: task.sale_line_id.milestone == 0)
        task_to_delete.unlink()
