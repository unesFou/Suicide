# -*- coding: utf-8 -*-
from odoo import models,fields,api


class aa_camera(models.Model):# models.TransientModel
    _name = 'aa.camera'
    _rec_name='name'
    _order = 'sequence'
    
    name = fields.Char("Nom",required=True)
    # ip = fields.Char("IP NVR old",required=True)
    ip_nvr = fields.Char("IP NVR",required=True)
    # zabbix_hostid = fields.Char("zabbix host id")
    # ip_cam = fields.Char("IP Caméra",required=True)
    login = fields.Char("Login",required=True)
    password = fields.Char("Password",required=True)
    rtsp_str  = fields.Char("rtsp_str",required=True)
    desc  = fields.Char("Description")
    max_elapsed_time  = fields.Integer("max elapsed time (seconds)",required=True,default=2)
    company_id = fields.Many2one('res.company',"Unite")
    host_id = fields.Many2one('aa.zabbix_host',"zabbix host")
    type = fields.Selection([
        ('geole', 'Geole'),
        ('permanencier', 'permanencier')
        ], 'Type', default='geole')
    sequence = fields.Integer('Sequence')

    color_state = fields.Integer("color state",compute='_compute_color_state')


    _sql_constraints = [
        ('ip_nvr_uniq', 'unique(ip_nvr)',
         ("this IP already exist \n"))
    ]


    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default={'ip_nvr': f"{self.ip_nvr}(copie)",
                 "name":f"{self.name}(copie)",
                 "login":f"____",
                 "password":f"____",
                 "rtsp_str":f"{self.rtsp_str}(copie)",
                 "unite":False
                 
                 }
        rec = super(aa_camera, self).copy(default)
        return rec
    
    def show_notifs(self):
        action = self.env.ref('gr_suicide.aa_notification_action').read()[0]
        action['domain']=[('camera_id','=',self.id)]
        return action 
        
        
    @api.multi
    def _compute_color_state(self):
        for s in self:
            # not_ids = self.env['aa.notification']
            # now = datetime.now()
            # date_e = now + timedelta(seconds=_convert_to_seconds(s.duration))
            # diff = date_e - now
            # if diff.seconds <5:
                s.color_state = 0
            # elif s.state != 'done':
            #     s.color_state = 1
            # else:
            #     s.color_state = 0
                
                