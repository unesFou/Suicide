from odoo import _, http,models
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        # if request.httprequest.method == 'OPTIONS':
        #     headers = {
        #         'Access-Control-Max-Age': 60 * 60 * 24,
        #         'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode',
        #         'Access-Control-Allow-Origin':'*'
        #     }
        #     return request.make_response({}, headers)

        # context = dict(request.context)
        # if 'editable' in request.httprequest.args and 'editable' not in context:
        #     context['editable'] = True
        # if 'edit_translations' in request.httprequest.args and 'edit_translations' not in context:
        #     context['edit_translations'] = True
        # if context.get('edit_translations') and 'translatable' not in context:
        #     context['translatable'] = True
        # request.context = context
        # authorized_ip = "http://105.157.12.122:3000"
        if request.httprequest.headers.get("Origin",False):
            authorized_ip = request.httprequest.headers['Origin']
            
            # authorized_ip = "http://192.168.100.172:3000"
            # print("request.httprequest.base_url=",request.httprequest.base_url)
    
            # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
            # request.httprequest.headers.set('Access-Control-Allow-Headers', 'http://127.0.0.1:3000')
            # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
            # request.httprequest.headers.set('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
            if request.httprequest.method == 'OPTIONS':
                # return request._json_response(result={'1':1})
                headers={
                'Access-Control-Allow-Origin':  authorized_ip,
                'Access-Control-Allow-Headers':'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Credentials':'true',
                # 'Access-Control-Allow-Methods': 'GET',
                }
                response = request.make_response(data={"preflight":"HHHHHHHHHHHHH"},headers=headers)
                # if hasattr(response, 'set_cookie'):
                #     delattr(response, 'set_cookie')
                # else:
                #     print(1)
                return response
            _logger.info("______________ the remote ip is - %s "%request.httprequest.remote_addr)
            # if request.httprequest.remote_addr in ('127.0.0.1','192.168.100.172'):
            response=super(IrHttp, cls)._dispatch()
            response.headers['Access-Control-Allow-Origin']=authorized_ip
            response.headers['Access-Control-Allow-Headers']='Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials']='true'
            return response
        # else:
        #     print(1)
        return super(IrHttp, cls)._dispatch()


    # 192.168.100.140
  #     res.setHeader('Access-Control-Allow-Origin', '*'); // Allow requests from any origin
  # res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'); // Allow specific HTTP methods
  # res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization'); // Allow specific headers
  # res.setHeader('Access-Control-Allow-Credentials', true);
  #