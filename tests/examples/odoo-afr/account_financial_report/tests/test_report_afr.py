# coding: utf-8
###########################################################################
#    Module Writen to ODOO, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase
from openerp.addons.controller_report_xls.controllers.main import get_xls
import logging
from openerp import workflow
import openerp
import base64
import os
import xlrd
import tempfile

_logger = logging.getLogger(__name__)


class TestReportAFR(TransactionCase):

    def setUp(self):
        super(TestReportAFR, self).setUp()
        self.account_obj = self.env['account.account']
        self.invoice_obj = self.env['account.invoice']
        self.partner_obj = self.env['res.partner']
        self.wiz_rep_obj = self.env['wizard.report']
        self.attachment_obj = self.env['ir.attachment']

        self.invoice_demo = self.env.ref('account.test_invoice_1')
        self.account_cred = self.env.ref('account.a_pay')
        self.company_id = self.ref('base.main_company')
        self.fiscalyear_id = self.ref('account.data_fiscalyear')
        self.currency_id = self.ref('base.EUR')

    def test_lines_report_afr(self):
        _logger.info('I duplicate invoice demo to this test')
        account_id = self._duplicate_invoice()
        _logger.info('I generate the account financial report')
        self._generate_afr(account_id.id)

    def _duplicate_invoice(self):
        account_id = self.account_cred.copy({
            'name': 'Creditors - AFR',
            'code': 'X1111 - AFR'
        })
        invoice_id = self.invoice_demo.copy(
            {'account_id': account_id.id})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice_id.id, 'invoice_open',
            self.cr)
        return account_id

    def _generate_afr(self, account_id):
        wiz_id = self.wiz_rep_obj.create({
            'company_id': self.company_id,
            'inf_type': 'BS',
            'columns': 'four',
            'currency_id': self.currency_id,
            'report_format': 'xls',
            'display_account': 'bal_mov',
            'fiscalyear': self.fiscalyear_id,
            'display_account_level': 0,
            'target_move': 'posted',
            'account_list': [(4, account_id, 0)]})

        context = {
            'xls_report': True,
            'active_model': 'wizard.report',
            'active_ids': [wiz_id.id],
            'active_id': wiz_id.id,
        }
        data = wiz_id.with_context(context).print_report({})
        result = openerp.report.render_report(
            self.cr, self.uid, [wiz_id.id],
            'afr.1cols', data.get('data', {}), context=context)[0]
        report = get_xls(result)
        attach = self.attachment_obj.create({
            'name': 'xls_afr',
            'datas_fname': 'xls_afr.xls',
            'datas': base64.encodestring(report),
            'res_model': 'wizard.report',
            'res_id': wiz_id.id})
        self._check_file_xls(attach)

    def _check_file_xls(self, attachment):
        (fileno, fname) = tempfile.mkstemp('.xls', 'exchange_xls.xls')
        with open(fname, "wb") as fobj:
            fobj.write(base64.decodestring(attachment.datas))
        os.close(fileno)
        file_xls = fname
        book = xlrd.open_workbook(file_xls)
        sh = book.sheet_by_index(0)
        self.assertEquals(
            sh.nrows, 6,
            'the generated file contains more or less lines than expected')
