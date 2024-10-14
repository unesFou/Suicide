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
from odoo import http
from odoo.http import request
from datetime import datetime

_logger = logging.getLogger(__name__)

class BackendController(http.Controller):

    @http.route('/api/dashboard', type='json', methods=['OPTIONS', 'POST', 'GET'], auth="user", cors="*")
    def api_dashboard(self, **kw):
        date_s = date_e = False
        if 'date_start' in kw and 'date_end' in kw:
            try:
                date_s = datetime.strptime(kw['date_start'], "%Y-%m-%dT%H:%M")
                date_e = datetime.strptime(kw['date_end'], "%Y-%m-%dT%H:%M")
            except ValueError as e:
                return {'error': f'date format error ({e})'}

        unite_ids = request.env['res.company'].sudo().search([('parent_id', '=', request.env.user.company_id.id)])

        def get_res_data(unite_id):
            res = unite_id.read(['id', 'name', 'type_id'])[0]
            res['presence_rate'] = unite_id.get_presence_rate(date_s, date_e)
            
            if unite_id.children_ids:
                res['childs'] = [get_res_data(child_id) for child_id in unite_id.children_ids]
            elif unite_id.camera_ids:
                res["camera_ids"] = []
                for camera_id in unite_id.camera_ids:
                    res_camera = camera_id.read(['id', 'name', 'type', 'sequence'])[0]
                    res_camera['notifications'] = []
                    notification_ids = request.env['aa.notification'].get_notifsByUnite(unite_id.id, date_s, date_e)
                    res_camera['notifications'] = [notif.read(['date_s', 'date_e', 'duration', 'type'])[0] for notif in notification_ids]
                    res_camera['notifications'] = [{'date_s': n['date_s'], 'date_e': n['date_e'], 'duration': n['duration'], 'type': n['type'], 'state': notif.color_state} for n, notif in zip(res_camera['notifications'], notification_ids)]
                    res["camera_ids"].append(res_camera)
            return res

        response_data = [get_res_data(unite_id) for unite_id in unite_ids]
        return response_data


    
    #
    # @http.route('/api/dashboard_old', type='json', methods=['OPTIONS', 'POST','GET'], auth="user",cors="*")
    # def api_dashboard_old(self, **kw):
    #     date_s=date_e=False
    #     """{'date_start': '2024-02-07T12:22', 'date_end': '2024-02-07T13:22'}"""
    #     if 'date_start' in kw.keys() and 'date_end' in kw.keys():
    #         date_start_str = kw['date_start']
    #         date_end_str = kw['date_end']
    #         try:
    #             date_s = datetime.strptime(date_start_str, "%Y-%m-%dT%H:%M")
    #             date_e = datetime.strptime(date_end_str, "%Y-%m-%dT%H:%M")
    #         except ValueError as e:
    #             return json.dumps({'error': f'date format error ({e})'})
    #     # else:
    #     #     return json.dumps({'error': 'date start and date end must be in the request params'})
    #
    #     print("###################### api_dashbord")
    #     response=[]
    #     cie_ids = request.env['res.company'].sudo().search([('parent_id','=',request.env.user.company_id.id)])
    #     for cie_id in cie_ids:
    #         # state=random.randint(0, 2)
    #         res_cie=cie_id.read(['id','name','type_id'])[0]
    #         res_cie['state']=1
    #         if date_s and date_e:
    #             res_cie['presence_rate']=cie_id.get_presence_rate(date_s,date_e)
    #         res_cie["bt_ids"]=[]
    #         for bt_id in cie_id.children_ids:
    #             res_bt = bt_id.read(['id','name','type_id','parent_id'])[0]
    #             res_bt['state']=1
    #             if date_s and date_e:
    #                 res_bt['presence_rate']=bt_id.get_presence_rate(date_s,date_e)
    #             res_bt["camera_ids"]=[]
    #             for camera_id in bt_id.camera_ids:
    #                 res_camera=camera_id.read(['id','name','type','sequence'])[0]
    #                 res_camera['state']=1
    #                 res_camera['notifications']=[]
    #                 notification_ids = request.env['aa.notification'].sudo().search([('camera_id','=',camera_id.id)])
    #                 # color_state = -1
    #                 for notification_id in notification_ids:
    #                     res_notification = notification_id.read(['date_s','date_e','duration','type'])[0]
    #                     res_notification['state']=notification_id.color_state
    #
    #                     # res_notification['state']=state
    #                     res_camera['notifications'].append(res_notification)
    #
    #                 res_bt["camera_ids"].append(res_camera)
    #             res_cie["bt_ids"].append(res_bt) 
    #         response.append(res_cie)
    #     response_json = json.dumps(response, default=datetime_serializer)
    #     print("response_is")
    #     # print(response_json)
    #     return response_json
   
  
    # @http.route('/api/dashboardd', type='json', methods=['OPTIONS','POST','GET'], auth="user",cors="*",csrf=True)
    # def api_dashboardd(self, **kw):
    #     response_json = json.dumps({'the connected user is ':request.env.user.display_name})
    #     # print("response of api_dashboarddd is ")
    #     # print(response_json)
    #     return response_json
    
    
    
    # @http.route('/gr_api', type='json', methods=['OPTIONS','POST','GET'], auth="publidc")
    # def gr_api(self, **kw):
    #     response_json = json.dumps({'test':1})
    #     print("response of api_dashboarddd is ")
    #     session_id=kw['session_id']
    #     print(response_json)
    #     return response_json
    #     # return request.make_response(resp,{
    #     #     'Cache-Control': 'no-cache',
    #     #     'Content-Type': 'text/html; charset=utf-8',
    #     #     'Access-Control-Allow-Origin':  '*',
    #     #     'Access-Control-Allow-Methods': 'GET',
    #     #     })
    
# class IrHttp(models.AbstractModel):
#     _inherit = 'ir.http'
#
#     @classmethod
#     def _dispatch(cls):
#         # if request.httprequest.method == 'OPTIONS':
#         #     headers = {
#         #         'Access-Control-Max-Age': 60 * 60 * 24,
#         #         'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode',
#         #         'Access-Control-Allow-Origin':'*'
#         #     }
#         #     return request.make_response({}, headers)
#
#         # context = dict(request.context)
#         # if 'editable' in request.httprequest.args and 'editable' not in context:
#         #     context['editable'] = True
#         # if 'edit_translations' in request.httprequest.args and 'edit_translations' not in context:
#         #     context['edit_translations'] = True
#         # if context.get('edit_translations') and 'translatable' not in context:
#         #     context['translatable'] = True
#         # request.context = context
#         print("request.httprequest.base_url=",request.httprequest.base_url)
#
#         # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
#         # request.httprequest.headers.set('Access-Control-Allow-Headers', 'http://127.0.0.1:3000')
#         # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
#         # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
#         if request.httprequest.method == 'OPTIONS' and "dashboardd" in request.httprequest.base_url:
#             # return request._json_response(result={'1':1})
#             headers={
#             'Access-Control-Allow-Origin':  'http://192.168.100.140:3000',
#             'Access-Control-Allow-Headers':'Content-Type, Authorization',
#             'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
#             'Access-Control-Allow-Credentials':'true',
#             # 'Access-Control-Allow-Methods': 'GET',
#             }
#             response = request.make_response(data={"preflight":"HHHHHHHHHHHHH"},headers=headers)
#             # if hasattr(response, 'set_cookie'):
#             #     delattr(response, 'set_cookie')
#             # else:
#             #     print(1)
#             return response
#
#         if request.httprequest.remote_addr in ('127.0.0.1','192.168.100.140'):
#             response=super(IrHttp, cls)._dispatch()
#             response.headers['Access-Control-Allow-Origin']='http://192.168.100.140:3000'
#             response.headers['Access-Control-Allow-Headers']='Content-Type, Authorization'
#             response.headers['Access-Control-Allow-Credentials']='true'
#             return response
#         return super(IrHttp, cls)._dispatch()
#
#     # 192.168.100.140
#   #     res.setHeader('Access-Control-Allow-Origin', '*'); // Allow requests from any origin
#   # res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'); // Allow specific HTTP methods
#   # res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization'); // Allow specific headers
#   # res.setHeader('Access-Control-Allow-Credentials', true);
#   #
#
#
# # date_s = datetime.now()
# # # date_s=date_s.replace(hour=20)
# # if date_s.hour<8 :#or date_s.hour>18
# #     date_s = date_s - timedelta(days=2)
# # else:
# #     date_s = date_s - timedelta(days=1)
# # date_s=date_s.replace(hour=17, minute=0, second=0)
# # date_e = date_s+timedelta(hours=14)
# # print(date_s)
# # print(date_e)
        
    