# -*- coding: utf-8 -*-
from odoo import models,fields


class aa_camera(models.Model):# models.TransientModel
    _name = 'aa.camera'
    _rec_name='name'
    _order = 'sequence'
    
    duration_red = fields.Integer("Nom",required=True)
    duration_red = fields.Integer("Nom",required=True)
    
    # ip = fields.Char("IP",required=True)
    # login = fields.Char("Login",required=True)
    # password = fields.Char("Password",required=True)
    # unite_id = fields.Many2one('aa.unite',"Unite",required=True)
    # company_id = fields.Many2one('res.company', string='Company', related='unite_id.company_id',store=True,required=True)
    # type = fields.Selection([
    #     ('geole', 'Geole'),
    #     ('permanencier', 'permanencier')
    #     ], 'Type', default='geole')
    sequence = fields.Integer('Sequence')
