# -*- coding: utf-8 -*-
from odoo import models,fields,api
from datetime import datetime, timedelta,timezone
from odoo.exceptions import Warning
import json

def convert_for_dumps(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    
def _convert_to_seconds(time_string):
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = 0,0,0
    try:
        hours, minutes, seconds = map(int, time_string.split(':'))  # 0,0,0
    except:
        print('1')

    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


class aa_notification(models.Model):# models.TransientModel
    _name = 'aa.notification'
    _inherit = 'mail.thread'
    _rec_name='camera_id'
    _order = 'date_s desc'
    
    
    date_s = fields.Datetime("date start",required=True)
    date_e = fields.Datetime("date end")
    duration  = fields.Char("Durée (Seconds)",compute='_compute_duration',store=True)#
    descr  = fields.Char("Description")
    camera_id = fields.Many2one('aa.camera',"Camera",required=True)
    company_id = fields.Many2one('res.company',related='camera_id.company_id', string='Unité',store=True)
    
    
    img_file = fields.Binary("Image",attachment=True)
    img_file_name = fields.Char("res file name")  #,readonly=True
    
    type = fields.Selection([
        ('suicide', 'Suicide'),
        ('disconnected', 'déconnecté'),
        ('absence', 'Absence')
        ], 'Type',required=True)
    
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('done', 'Fait')
        ], 'Etat',required=True)
    
    color_state = fields.Integer("color state",compute='_compute_color_state')
    
    sequence = fields.Integer('Sequence')
    
    @api.multi
    @api.depends('date_e')
    def _compute_duration(self):
        # from datetime import timedelta
        for s in self:
            if s.date_e:
            # duration = timedelta(seconds=172202)
                s.duration = str(s.date_e.replace(microsecond=0) - s.date_s)


    
    
    @api.multi
    @api.depends('date_e','state')
    def _compute_color_state(self):
        for s in self:
            if s.date_s  and s.date_e:
                if not s.date_s > s.date_e:
                    # print("s.date_s=",s.date_s)
                    # print("s.date_e=",s.date_e)
                        # raise Warning("date start doit etre < Date end not_id=%s"%s.id)
                    # utc_timezone = timezone(timedelta(hours=1))
                    date_s = s.date_s - timedelta(hours=1)
                    date_e = date_s + timedelta(seconds=_convert_to_seconds(s.duration))
                    date_now = datetime.now()
                    diff =  date_now - date_e
                    # print("diff is ",diff.seconds)
                    if date_e>date_now or diff.seconds <10:
                        s.color_state = 2
                    elif s.state != 'done':
                        s.color_state = 1
                    else:
                        s.color_state = 0
                else:
                    s.color_state = -1
            
    def state_to_done(self):
        self.write({'state':'done'})
            
    def state_to_new(self):
        self.write({'state':'new'})
      
    def state_to_new_for_all_notifs(self):
        for s in self.search([]):
            s.write({'state':'new'})
            
      
    @api.model
    def create(self, vals):
        self._check_dates(vals)
        new_record = super(aa_notification, self).create(vals)
        old_notifs=self.search([("date_e","=",False),("camera_id","=",new_record.camera_id.id),('id','!=',new_record.id)])
        for old_notif in old_notifs:
            old_notif.write({"date_e":datetime.now().replace(microsecond=0),"descr":"closed new notif"})
        self.send_current_notifs()
        return new_record

    @api.multi
    def write(self, vals):
        res = False
        if 'date_e' in vals.keys():
            if not self.date_e:
                res = super().write(vals)
                if 'date_e' in vals.keys():
                    self.send_current_notifs()
            else:
                print("this case should not happen")
                # with open("notif_issues.txt", 'a') as file:
                # with open("/opt/odoo12/odoo/my_addons/gr_suicide/notif_issues.txt", 'a') as file:
                    # file.write(f"date end already exist prblm of ({self.camera_id.name}) utc now is {datetime.utcnow().__str__()} \n")
        else:
            res = super().write(vals)
            self.send_current_notifs()
        return res
    
    @api.multi
    def unlink(self):
        # uniteId=self.company_id.id
        res=super().unlink()
        # self.send_current_notifs()
        return res
    
    
    def get_notifsByUnite(self,uniteId,datet_start,datet_end):
        domain = [
            ('company_id', '=', uniteId),
            ('type', '=', 'absence'),   # Filter by id=12
            '|',  # Logical OR operator
            '&',  # Logical AND operator (optional, if needed)
            ('date_s', '>=', datet_start),
            ('date_s', '<=', datet_end),
            '&',  # Logical AND operator (optional, if needed)
            ('date_e', '>=', datet_start),
            ('date_e', '<=', datet_end)
        ]
        # abs_duration=timedelta()
        vals={'notifs':[],'intervals':[]}
        not_ids = self.search(domain)
        dmn1=[('date_e','=',False),('date_s', '<=', datet_end),('company_id', '=', uniteId)]
        not_ids=not_ids| self.search(dmn1)
        return not_ids
        

    def _check_dates(self,vals):
        if 'date_s' in vals.keys() and 'date_e' in vals.keys() and vals['date_e']:
            if not vals['date_s'] < vals['date_e']:
                raise Warning("date start doit etre < Date end")


    
    
    def send_current_notifs(self):
        
        # {'id': 725, 'date_s': datetime.datetime(2024, 4, 4, 11, 38, 37), 'duration': False, 'type': 'absence', 'state': 0, 'unite_id': (83, 'BT Ain Aouda')}
        # partner_ids = self.env['res.partner'].search([('id','=',14)])
        
        user_ids = self.env['res.users'].search([])
        for user_id in user_ids:
            allowed_unite_ids = self.company_id.search([('id','child_of',user_id.company_id.id)])
            if self.company_id.id in allowed_unite_ids.ids:
                data = self.sudo(user_id.id).get_current_notifs(user_id.company_id.id)
                data_json = json.dumps(data, default=convert_for_dumps)
                
                mail_channel = self.env['mail.channel']
                mail_channel_id = mail_channel.channel_get([user_id.partner_id.id])
                mail_channel_id = self.env['mail.channel'].browse(mail_channel_id['id'])
                res = mail_channel_id.message_post(message_type='comment',
                                                   partner_ids=[],
                                                   channel_ids=[],
                                                   body=data_json,
                                                   attachment_ids=[],
                                                   canned_response_ids=[]
                                                   ,subtype='mail.mt_comment')
            else:
                print(1)
            # print(res)
        

    # @api.multi
    # def write(self, vals):
    #     """Update the registry when existing rules are updated."""
    #     super(AuditlogRule, self).write(vals)
    #     if self._register_hook():
    #         modules.registry.Registry(self.env.cr.dbname).signal_changes()
    #     return True
            
        
    def get_current_notifs_old(self):
        result=[]
        notif_ids = self.sudo().search([('date_e','=',False)])
        for notif_id in notif_ids:
            res = notif_id.read(['date_s','type','company_id'])[0]
            res['state']=notif_id.color_state
            """rename company_id to unite_id"""
            res['unite_id'] = res.pop('company_id')
            result.append(res)
        return result
    
    
    def get_current_notifs(self,parent_uniteId=None):
        if parent_uniteId:
            allowed_unite_ids = self.env['res.company'].search([('id','child_of',parent_uniteId)])
        else:
        #     allowed_unite_ids = self.env['res.company'].search([('parent_id','=',False)])
            allowed_unite_ids = self.env['res.company'].search([('id','child_of',self.env.user.company_id.id)])
            
        result=[]
        notif_ids = self.search([('date_e','=',False),('company_id','in',allowed_unite_ids.ids)], order='date_s asc')
        for notif_id in notif_ids:
            res = notif_id.read(['date_s','type','company_id'])[0]
            res['state']=notif_id.color_state
            """rename company_id to unite_id"""
            res['unite_id'] = res.pop('company_id')
            result.append(res)
            
            
        for comp_id in allowed_unite_ids:
            if comp_id.id not in notif_ids.mapped("company_id").ids and not comp_id.child_ids:
                result.append({'id':comp_id.id,'unite_id':(comp_id.id,comp_id.name)})
            
        # for comp_id in allowed_unite_ids.filtered(lambda x:x.id not in notif_ids.mapped("company_id").ids):
            
        # """add another unites which dosn't have current notif this maybe will ignored after """
        # if notif_ids:
        #     print(1)
        # query = f"select id,name from res_company rc where id in (select company_id from aa_notification group by company_id) and id in {allowed_unite_ids.ids}"
        # # self._cr.execute(query)
        # # d=self._cr.fetchall()
        # # resIds = [x[0] for x in d if x[0] not in notif_ids.mapped("company_id").ids]
        # # comp_ids =self.env['res.company'].search([('id','in',resIds)])
        # # query = "select id,name from res_company"
        # # if notif_ids:
        # #     query+=f"""and id not in {tuple(notif_ids.mapped('company_id').ids).__str__().replace(",)", ")")}"""
        #
        # # res=[{'id':x[0],'unite_id':(x[0],x[1])}  for x in d if x[0] not in notif_ids.mapped("company_id").ids]#'id':x[0],
        # for comp_id in comp_ids:
        #     result.append({'id':comp_id.id,'unite_id':(comp_id.id,comp_id.name)})
        
        return result
        # compIds=[x for x in d]
        # comp_ids = self.company_id.browse(compIds)
        # for comp_id in comp_ids:
        #     result.append({'unite_id':comp_id.read('id')[0]})

        
    
        
        
        
        
            