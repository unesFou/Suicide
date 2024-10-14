###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

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
    

# def datetime_serializer(obj):
#     if isinstance(obj, datetime):
#         return obj.isoformat()
    
class notificationController(http.Controller):

    # @http.route('/web/session/authenticate', type='json', auth="none")
    # @http.route('/api/get_data/<string:numero_appel>', auth='public', methods=['GET'], cors='*')
    
    
    
    # @http.route('/api/dashbord', type='json', methods=['OPTIONS', 'POST'], auth="user")
    # def api_dashbord(self, **kw):
    #     print("###################### api_dashbord")
    #     response_data = {'user':request.env.user.display_name}
    #     return response_data
    
    # @http.route('/apii/dashboardd', type='json', methods=['OPTIONS', 'POST'], auth="public")
    # def apii_dashboardd(self, **kw):
    #     print("###################### api_dashbordd")
    #     # request_json = JsonRequest(http.request.env, **kwargs)
    #     # response_json = request_json.dispatch()
    #     response_json=json.dumps({'test':1})
    #     # return http.Response(response_json, content_type='application/json')
    #     return response_json
    
    
    @http.route('/api/img_notif/<int:notif_id>', type='json', methods=['OPTIONS', 'POST','GET'], auth="user",cors="*")
    def api_img_notif(self,**kw):
        if 'notif_id' in kw.keys() and kw['notif_id']:
            print("##### api_notification")
            response=[]
            not_id = request.env['aa.notification'].sudo().search([('id','=',kw['notif_id'])])
            if not_id :
                response=[{'id':not_id.id,'img':not_id.img_file}]
                not_id.write({'state':'done'})
        response_json = json.dumps(response, default=convert_for_dumps)
        print("response_of api_img_notif")
        return response_json
    
    # @http.route('/api/dashboardd', type='json',         methods=['OPTIONS','POST','GET'], auth="user",cors="*",csrf=True)
    
    
    @http.route('/api/get_current_notifs', type='json', methods=['OPTIONS', 'POST'], auth="user",cors="*",csrf=True)
    def api_get_current_notification(self,**kw):
        if 'parent_unite_id' in kw.keys() :
            # response_json = json.dumps({'the connected user is ':request.env.user.display_name})
            response=request.env['aa.notification'].get_current_notifs(parent_uniteId = int(kw['parent_unite_id']))
            response_json = json.dumps(response, default=convert_for_dumps)
            return response_json
        else:
            return json.dumps({'error': 'parent_unite_id must be in the request params'})
    

    @http.route('/api/get_notifs', type='json', methods=['OPTIONS', 'POST','GET'], auth="user",cors="*")
    def api_get_notification(self, **kw):
        # print("client request /api/get_notifs")
        print(kw)
        """{'date_start': '2024-02-07T12:22', 'date_end': '2024-02-07T13:22'}"""
        if 'unite_id' in kw.keys() and 'date_start' in kw.keys() and 'date_end' in kw.keys():
            date_s=date_e=False
            date_start_str = kw['date_start']
            date_end_str = kw['date_end']
            try:
                date_s = datetime.strptime(date_start_str, "%Y-%m-%dT%H:%M")
                date_e = datetime.strptime(date_end_str, "%Y-%m-%dT%H:%M")
            except ValueError as e:
                return json.dumps({'error': f'date format error ({e})'})
            
            not_ids = request.env['aa.notification'].get_notifsByUnite(kw['unite_id'],date_s,date_e)
            response={"notifs":[]}
            for not_id in not_ids:#.filtered(lambda x:x.date_e!=False)
                res_notification = not_id.read(['date_s','date_e','duration','type'])[0]
                res_notification['state']=not_id.color_state
                response['notifs'].append(res_notification)
    
            response_json = json.dumps(response, default=convert_for_dumps)
            # print("response_of api_notification")
            return response_json
        else:
            return json.dumps({'error': 'unite_id and date start and date end must be in the request params'})
        
        
        
        
    
    