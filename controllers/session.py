from odoo import http
from odoo.http import request

class SessionController(http.Controller):
    
    # @http.route('/api/check-session', type='json', methods=['OPTIONS', 'POST'], auth="Public",cors="*",csrf=True)
    @http.route('/api/check_session', type='json', methods=['OPTIONS', 'POST'], auth="user",cors="*",csrf=True)
    def api_get_check_session(self,**kw):
        print("############# api_get_check_session")
        # response_json = json.dumps({'the connected user is ':request.env.user.display_name})
        # response=request.env['aa.notification'].get_current_notifs()
        # response_json = json.dumps(response, default=convert_for_dumps)
        return {'f':11}