# -*- coding: utf-8 -*-
from odoo import models,fields,api


class aa_nbr_personne(models.Model):# models.TransientModel
    _name = 'aa.nbr_personne'
    _rec_name='camera_id'
    _order = 'date_s desc'
    
    
    company_id = fields.Many2one('res.company',related='camera_id.company_id', string='Unité',store=True)
    camera_id = fields.Many2one('aa.camera',"Camera",required=True)
    # company_id = fields.Many2one('res.company', string='Company',store=True)
    date_s = fields.Datetime("date start",required=True)
    date_e = fields.Datetime("date end")
    duration  = fields.Char("Durée",compute='_compute_duration',store=True)
    nbr_personne = fields.Integer("nbr personne")
    
    def delete_all(self):
        query = "delete from aa_nbr_personne"
        self.env.cr.execute(query)
        self.env.cr.commit()
    # @api.multi
    # @api.depends('date_e')
    # def _compute_duration(self):
    #     # from datetime import timedelta
    #     for s in self:
    #         # duration = timedelta(seconds=172202)
    #         s.duration = str(s.date_e - s.date_s)
            
            