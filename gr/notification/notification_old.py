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
    duration  = fields.Char("Durée (Seconds)",compute='_compute_duration',store=True)
    camera_id = fields.Many2one('aa.camera',"Camera",required=True)
    company_id = fields.Many2one('res.company',related='camera_id.company_id', string='Unité',store=True)
    
    img_file = fields.Binary("Image",attachment=True)
    img_file_name = fields.Char("res file name")  #,readonly=True
    
    type = fields.Selection([
        ('suicide', 'Suicide'),
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
                s.duration = str(s.date_e - s.date_s)
            
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
        vals={'intervals':[],'notifs':[]}
        not_ids = self.search(domain)
        for not_id in not_ids.filtered(lambda x:x.date_e!=False):
            """"adapt_date_for calculate absence duration"""
            dt_s=not_id.date_s
            if dt_s<datet_start:
                dt_s=datet_start
                
            dt_e=not_id.date_e
            if dt_e>datet_end:
                dt_e=datet_end
            vals['intervals'].append({'date_start':dt_s,'date_end':dt_e})
            
            res_notification = not_id.read(['date_s','date_e','duration','type'])[0]
            res_notification['state']=not_id.color_state
            vals['notifs'].append(res_notification)
                        
            # 'notifs':[]
        return vals

    def send_mail_message(self):
        # import threading
        import time
        import logging
        _logger = logging.getLogger(__name__)
        
        
        def thread_function():
            mail_channel_id = self.env['mail.channel'].browse([2])
            kwargs = {'partner_ids': [], 'channel_ids': [], 'body': '2', 'attachment_ids': [], 'canned_response_ids': [], 'subtype': 'mail.mt_comment'}
            # kwargs = {"partner_ids":[],"channel_ids":[],"body":"2","attachment_ids":[],"canned_response_ids":[],"message_type":"comment","subtype":"mail.mt_comment"}
            # message_post
            counter=0
            
            while True:
                kwargs['body']="message_%s"%counter
                mail_channel_id.message_post(message_type="comment",**kwargs)
                # print("counter is ",counter);counter+=1
                # _logger.info("#################test")
                time.sleep(2)
                counter+=1
        # thread = threading.Thread(target=thread_function)
        # thread.start()
        thread_function()
        print("send_mail_message")
# mail.channel(2,)
#message_type='notification'
#{'partner_ids': [], 'channel_ids': [], 'body': 'fdgfg', 'attachment_ids': [], 'canned_response_ids': [], 'subtype': 'mail.mt_comment'}
#
    
    def _check_dates(self,vals):
        if 'date_s' in vals.keys() and 'date_e' in vals.keys() and vals['date_e']:
            if not vals['date_s'] < vals['date_e']:
                raise Warning("date start doit etre < Date end")

    @api.model
    def create(self, vals):
        self._check_dates(vals)
        new_record = super(aa_notification, self).create(vals)
        self.send_current_notifs()
        return new_record

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self.send_current_notifs()
        return res
    
    def send_current_notifs(self):
        # {'id': 725, 'date_s': datetime.datetime(2024, 4, 4, 11, 38, 37), 'duration': False, 'type': 'absence', 'state': 0, 'unite_id': (83, 'BT Ain Aouda')}
        data = self.get_current_notifs()
        data_json = json.dumps(data, default=convert_for_dumps)
        
        mail_channel = self.env['mail.channel']
        partner_ids = self.env['res.users'].search([]).mapped("partner_id")
        # partner_ids = self.env['res.partner'].search([('id','=',14)])
        for partner_id in partner_ids:
                print(partner_id.display_name)
                print("partner_id.display_name = " , partner_id.display_name)
                mail_channel_id = mail_channel.channel_get([partner_id.id])
                mail_channel_id = self.env['mail.channel'].browse(mail_channel_id['id'])
                res = mail_channel_id.message_post(message_type='comment',
                                                   partner_ids=[],
                                                   channel_ids=[],
                                                   body=data_json,
                                                   attachment_ids=[],
                                                   canned_response_ids=[]
                                                   ,subtype='mail.mt_comment')
                print(res)
        

    # @api.multi
    # def write(self, vals):
    #     """Update the registry when existing rules are updated."""
    #     super(AuditlogRule, self).write(vals)
    #     if self._register_hook():
    #         modules.registry.Registry(self.env.cr.dbname).signal_changes()
    #     return True
    def send_chat_msg2(self):
        
        data = self.get_current_notifs()
        mail_channel = self.env['mail.channel']
        partner_ids = self.env['res.users'].search([]).mapped("partner_id")
        # partner_ids = self.env['res.partner'].search([('id','=',14)])
        for partner_id in partner_ids:
                print(partner_id.display_name)
                print("partner_id.display_name = " , partner_id.display_name)
                mail_channel_id = mail_channel.channel_get([partner_id.id])
                mail_channel_id = self.env['mail.channel'].browse(mail_channel_id['id'])
                res = mail_channel_id.message_post(message_type='comment',
                                                   partner_ids=[],
                                                   channel_ids=[],
                                                   body=data.__str__(),
                                                   attachment_ids=[],
                                                   canned_response_ids=[]
                                                   ,subtype='mail.mt_comment')
                print(res)
            
    def send_chat_msg(self):
        """partner_ids     15=cie_sale@gr.ma    96=2@gr.ma    14=reg_rabat@gr.ma """
        import time
        counter=0
        while True:
            counter+=1
            mail_channel = self.env['mail.channel']
            partners_to=[14]
            mail_channel_id = mail_channel.channel_get(partners_to)
            self._cr.commit()
            import requests
            import json
            url = "http://localhost:8072/web/dataset/call_kw/mail.channel/message_post"
            
            payload = json.dumps({
              "jsonrpc": "2.0",
              "method": "call",
              "params": {
                "args": [mail_channel_id['id']],
                "model": "mail.channel",
                "method": "message_post",
                "kwargs": {
                  "partner_ids": [],
                  "channel_ids": [],
                  "body": "test %s"%counter,
                  "attachment_ids": [],
                  "canned_response_ids": [],
                  "message_type": "comment",
                  "subtype": "mail.mt_comment"
                }
              },
              # "id": 490657879
            })
            headers = {
              # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
              # 'Accept': 'application/json, text/javascript, */*; q=0.01',
              # 'Accept-Language': 'en-US,en;q=0.5',
              # 'Accept-Encoding': 'gzip, deflate, br',
              'Content-Type': 'application/json',
              # 'X-Requested-With': 'XMLHttpRequest',
              # 'Origin': 'http://localhost:8082',
              # 'DNT': '1',
              # 'Sec-GPC': '1',
              # 'Connection': 'keep-alive',
              # 'Referer': 'http://localhost:8082/web',
            'Cookie': 'session_id=739471fb1a3d6401d1a7a24b1a32204037287505',
              # 'Sec-Fetch-Dest': 'empty',
              # 'Sec-Fetch-Mode': 'cors',
              # 'Sec-Fetch-Site': 'same-origin',
              # 'Pragma': 'no-cache',
              # 'Cache-Control': 'no-cache'
            }
            
            response = requests.request("POST", url, headers=headers, data=payload)
            
            print(response.text)
            time.sleep(5)
        
        
    def websocket(self):
        import asyncio
        import websockets
        import json
        from datetime import datetime
        
        async def handler(websocket, path):
            # Simulate sending data every 2 seconds
            while True:
                data = {"message": f"Server time: {datetime.now()}"}
                await websocket.send(json.dumps(data))
                await asyncio.sleep(5)
        
        async def start_websocket_server():
            start_server = await websockets.serve(handler, "localhost", 5000)
            await start_server.wait_closed()
        
        # Run the WebSocket server in a separate coroutine
        async def run_server():
            await start_websocket_server()
        
        # This function will run the server in the event loop
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_server())
            print("end")
        # Run the WebSocket server
        # if __name__ == "__main__":
        run()
    
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
    
    def get_current_notifs(self):
        result=[]
        notif_ids = self.sudo().search([('date_e','=',False)], order='date_s asc')
        for notif_id in notif_ids:
            res = notif_id.read(['date_s','type','company_id'])[0]
            res['state']=notif_id.color_state
            """rename company_id to unite_id"""
            res['unite_id'] = res.pop('company_id')
            result.append(res)
            
        """add another unites which dosn't have current notif this maybe will ignored after """
        
        # query = "select id,name from res_company rc where id in (select company_id from aa_notification group by company_id)"
        query = "select id,name from res_company"
        # if notif_ids:
        #     query+=f"""and id not in {tuple(notif_ids.mapped('company_id').ids).__str__().replace(",)", ")")}"""
        self._cr.execute(query)
        d=self._cr.fetchall()
        res=[{'id':x[0],'unite_id':(x[0],x[1])} for x in d]#'id':x[0],
        for line in res:
            result.append(line)
        
        return result
        # compIds=[x for x in d]
        # comp_ids = self.company_id.browse(compIds)
        # for comp_id in comp_ids:
        #     result.append({'unite_id':comp_id.read('id')[0]})

        
    
        
        
        
        
            