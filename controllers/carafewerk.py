from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class CarafewerkController(http.Controller):
    @http.route('/carafewerk/', auth='public', website=True)
    def index(self, **kw):
        return redirect('/carafewerk/static/src/html/index.html')
