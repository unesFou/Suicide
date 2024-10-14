
import logging

from odoo import _, http
from odoo.http import request
import base64

import json
from datetime import datetime

_logger = logging.getLogger(__name__)

def convert_for_dumps(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    
class BackendController(http.Controller):

    
    # @http.route('/your_route', type='http', auth='user', methods=['GET'], csrf=False)
    # def get_data(self, date_start=None, date_end=None, **kwargs):
        
    # @http.route('/api/presence_rate', type='json', methods=['OPTIONS', 'POST','GET'], auth="public",cors="*",csrf=False)
    # def presence_rate(self,**kw):
    #     print("########################### /api/presence_rate")
    #     print(kw)
    #     if 'date_start' in kw.keys() and 'date_end' in kw.keys():
    #
    #         response={'id':10,'img':"test"}
    #         response_json = json.dumps(response, default=convert_for_dumps)
    #         print("response_of api_notification")
    #         # print(response_json)
    #         return response_json
    #     else:
    #         return json.dumps({'error': 'date start and date end must be in the request params'})
        # if 'notif_id' in kw.keys() and kw['notif_id']:
        #     print("##### api_notification")
        #     response=[]
        #     not_id = request.env['aa.notification'].sudo().search([('id','=',kw['notif_id'])])
        #     if not_id :
        #         response=[{'id':not_id.id,'img':not_id.img_file}]
        
    @http.route('/api/presence_rate', type='json', methods=['OPTIONS', 'POST','GET'], auth="public",cors="*",csrf=False)
    def presence_rate(self,**kw):
        """{'date_start': '2024-02-07T12:22', 'date_end': '2024-02-07T13:22'}"""
        if 'date_start' in kw.keys() and 'date_end' in kw.keys():
            date_start_str = kw['date_start']
            date_end_str = kw['date_end']
            try:
                date_start = datetime.strptime(date_start_str, "%Y-%m-%dT%H:%M")
                date_end = datetime.strptime(date_end_str, "%Y-%m-%dT%H:%M")
            except ValueError as e:
                return json.dumps({'error': f'date format error ({e})'})
            # unite_ids = request.env['aa.unite'].sudo().search([('type','=','bt')])
            unite_ids = request.env['res.company'].sudo().search([])
            response=[]
            for unite_id in unite_ids:
                presence_rate=unite_id.get_presence_rate(date_start,date_end)
                vals = unite_id.read(['id','name','type','parent_id'])[0]
                vals['presence_rate']=presence_rate
                response.append(vals)
                
            response_json = json.dumps(response, default=convert_for_dumps)
            print("response_of presence_ratee")
            print(response_json)
            return response_json
        else:
            return json.dumps({'error': 'date start and date end must be in the request params'})
    
