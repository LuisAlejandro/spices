# coding: utf-8
###########################################################################
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by:   Humberto Arocha humberto@openerp.com.ve
#                Angelica Barrios angelicaisabelb@gmail.com
#               Jordi Esteve <jesteve@zikzakmedia.com>
#    Planified by: Humberto Arocha
#    Finance by: LUBCAN COL S.A.S http://www.lubcancol.com
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
{
    "name": "Account Financial Reports",
    "version": "2.0",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "controller_report_xls",
    ],
    "category": "Accounting",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "report/layouts.xml",
        "report/template.xml",
        "report/template_analytic_ledger.xml",
        "report/template_journal_ledger.xml",
        "report/template_partner_balance.xml",
        "view/report.xml",
        "view/wizard.xml",
        "view/company_view.xml",
        "view/account_financial_report_view.xml",
    ],
    "installable": True
}
