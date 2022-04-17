# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by:   Humberto Arocha <hbto@vauxoo.com>
#                Angelica Barrios angelicaisabelb@gmail.com
#               Jordi Esteve <jesteve@zikzakmedia.com>
#               Javier Duran <javieredm@gmail.com>
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

import copy
import time
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import osv


class AccountBalance(report_sxw.rml_parse):
    _name = 'afr.parser'

    def __init__(self, cr, uid, name, context):
        super(AccountBalance, self).__init__(cr, uid, name, context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.sum_balance = 0.00
        self.sum_debit_fy = 0.00
        self.sum_credit_fy = 0.00
        self.sum_balance_fy = 0.00
        self.to_currency_id = None
        self.from_currency_id = None
        self.date_lst = []
        self.date_lst_string = ''
        self.localcontext.update({
            'getattr': getattr,
            'time': time,
            'lines': self.lines,
            'get_fiscalyear_text': self.get_fiscalyear_text,
            'get_periods_and_date_text': self.get_periods_and_date_text,
            'get_informe_text': self.get_informe_text,
            'get_month': self.get_month,
            'exchange_name': self.exchange_name,
            'get_vat_by_country': self.get_vat_by_country,
        })
        self.context = context

    def get_vat_by_country(self, form):
        """
        Return the vat of the partner by country
        """
        rc_obj = self.pool.get('res.company')
        country_code = rc_obj.browse(
            self.cr, self.uid,
            form['company_id'][0]).partner_id.country_id.code or ''
        string_vat = rc_obj.browse(self.cr, self.uid,
                                   form['company_id'][0]).partner_id.vat or ''
        if string_vat:
            if country_code == 'MX':
                return ['%s' % (string_vat[2:])]
            elif country_code == 'VE':
                return ['- %s-%s-%s' % (string_vat[2:3], string_vat[3:11],
                                        string_vat[11:12])]
            else:
                return [string_vat]
        else:
            return [_('VAT OF COMPANY NOT AVAILABLE')]

    def get_fiscalyear_text(self, form):
        """
        Returns the fiscal year text used on the report.
        """
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = None
        if form.get('fiscalyear'):
            fiscalyear = fiscalyear_obj.browse(
                self.cr, self.uid, form['fiscalyear'])
            return fiscalyear.name or fiscalyear.code
        else:
            fiscalyear = fiscalyear_obj.browse(
                self.cr, self.uid, fiscalyear_obj.find(self.cr, self.uid))
            return "%s*" % (fiscalyear.name or fiscalyear.code)

    def get_informe_text(self, form):
        """
        Returns the header text used on the report.
        """
        afr_id = form['afr_id'] and isinstance(form['afr_id'], (list, tuple)) \
            and form['afr_id'][0] or form['afr_id']
        if afr_id:
            name = self.pool.get('afr').browse(self.cr, self.uid, afr_id).name
        elif form['analytic_ledger'] and form['columns'] == 'four' and \
                form['inf_type'] == 'BS':
            name = _('Analytic Ledger')
        elif form['inf_type'] == 'BS':
            name = _('Balance Sheet')
        elif form['inf_type'] == 'IS':
            name = _('Income Statement')
        if form['columns'] == 'currency':
            name = _('End Balance Multicurrency')
        return name

    def get_month(self, form):
        '''
        return day, year and month
        '''
        if form['filter'] in ['bydate', 'all']:
            return _('From ') + self.formatLang(form['date_from'], date=True) \
                + _(' to ') + self.formatLang(form['date_to'], date=True)
        elif form['filter'] in ['byperiod', 'all']:
            aux = []
            period_obj = self.pool.get('account.period')

            for period in period_obj.browse(self.cr, self.uid,
                                            form['periods']):
                aux.append(period.date_start)
                aux.append(period.date_stop)
            sorted(aux)
            return _('From ') + self.formatLang(aux[0], date=True) + _(' to ')\
                + self.formatLang(aux[-1], date=True)

    def get_periods_and_date_text(self, form):
        """
        Returns the text with the periods/dates used on the report.
        """
        period_obj = self.pool.get('account.period')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        periods_str = None
        fiscalyear_id = form['fiscalyear'] or fiscalyear_obj.find(self.cr,
                                                                  self.uid)
        period_ids = period_obj.search(self.cr, self.uid, [(
            'fiscalyear_id', '=', fiscalyear_id), ('special', '=', False)])
        if form['filter'] in ['byperiod', 'all']:
            period_ids = form['periods']
        periods_str = ', '.join([period.name or period.code for period in
                                 period_obj.browse(self.cr, self.uid,
                                                   period_ids)])

        dates_str = None
        if form['filter'] in ['bydate', 'all']:
            dates_str = self.formatLang(form['date_from'], date=True) + \
                ' - ' + self.formatLang(form['date_to'], date=True) + ' '
        return {'periods': periods_str, 'date': dates_str}

    def special_period(self, periods):
        period_obj = self.pool.get('account.period')
        period_brw = period_obj.browse(self.cr, self.uid, periods)
        period_counter = [True for i in period_brw if not i.special]
        if not period_counter:
            return True
        return False

    def exchange_name(self, form):
        self.from_currency_id = \
            self.get_company_currency(
                form['company_id'] and
                isinstance(form['company_id'], (list, tuple)) and
                form['company_id'][0] or form['company_id'])
        if not form['currency_id']:
            self.to_currency_id = self.from_currency_id
        else:
            self.to_currency_id = form['currency_id'] and \
                isinstance(form['currency_id'], (list, tuple)) and \
                form['currency_id'][0] or form['currency_id']
        return self.pool.get('res.currency').browse(self.cr, self.uid,
                                                    self.to_currency_id).name

    def exchange(self, from_amount):
        if self.from_currency_id == self.to_currency_id:
            return from_amount
        curr_obj = self.pool.get('res.currency')
        return curr_obj.compute(self.cr, self.uid, self.from_currency_id,
                                self.to_currency_id, from_amount)

    def get_company_currency(self, company_id):
        rc_obj = self.pool.get('res.company')
        return rc_obj.browse(self.cr, self.uid, company_id).currency_id.id

    def get_company_accounts(self, company_id, acc='credit'):
        rc_obj = self.pool.get('res.company')
        if acc == 'credit':
            return [brw.id for brw in
                    rc_obj.browse(self.cr, self.uid,
                                  company_id).credit_account_ids]
        else:
            return [brw.id for brw in
                    rc_obj.browse(self.cr, self.uid,
                                  company_id).debit_account_ids]

    def _get_partner_balance(self, account, init_period, ctx=None):
        res = []
        ctx = ctx or {}
        if account['type'] in ('other', 'liquidity', 'receivable', 'payable'):
            sql_query = """
                SELECT
                    CASE
                        WHEN aml.partner_id IS NOT NULL
                        THEN (SELECT name FROM res_partner
                                WHERE aml.partner_id = id)
                    ELSE 'UNKNOWN'
                        END AS partner_name,
                    CASE
                        WHEN aml.partner_id IS NOT NULL
                       THEN aml.partner_id
                    ELSE 0
                        END AS p_idx,
                    %s,
                    %s,
                    %s,
                    %s
                FROM account_move_line AS aml
                INNER JOIN account_account aa ON aa.id = aml.account_id
                INNER JOIN account_move am ON am.id = aml.move_id
                %s
                GROUP BY p_idx, partner_name
                """

            where_posted = ''
            if ctx.get('state', 'posted') == 'posted':
                where_posted = "AND am.state = 'posted'"

            cur_periods = ', '.join([str(i) for i in ctx['periods']])
            init_periods = ', '.join([str(i) for i in init_period])

            where = """
                WHERE aml.period_id IN (%s)
                    AND aa.id = %s
                    AND aml.state <> 'draft'
                    """ % (init_periods, account['id'])
            query_init = sql_query % ('SUM(aml.debit) AS init_dr',
                                      'SUM(aml.credit) AS init_cr',
                                      '0.0 AS bal_dr',
                                      '0.0 AS bal_cr',
                                      where + where_posted)

            where = """
                WHERE aml.period_id IN (%s)
                    AND aa.id = %s
                    AND aml.state <> 'draft'
                    """ % (cur_periods, account['id'])

            query_bal = sql_query % ('0.0 AS init_dr',
                                     '0.0 AS init_cr',
                                     'SUM(aml.debit) AS bal_dr',
                                     'SUM(aml.credit) AS bal_cr',
                                     where + where_posted)

            query = '''
                SELECT
                    partner_name,
                    p_idx,
                    SUM(init_dr)-SUM(init_cr) AS balanceinit,
                    SUM(bal_dr) AS debit,
                    SUM(bal_cr) AS credit,
                    SUM(init_dr) - SUM(init_cr) + SUM(bal_dr) - SUM(bal_cr)
                        AS balance
                FROM (
                    SELECT
                    *
                    FROM (%s) vinit
                    UNION ALL (%s)
                ) v
                GROUP BY p_idx, partner_name
                ORDER BY partner_name
                ''' % (query_init, query_bal)

            self.cr.execute(query)
            res_dict = self.cr.dictfetchall()
            unknown = False
            for det in res_dict:
                inicial, debit, credit, balance = det['balanceinit'], det[
                    'debit'], det['credit'], det['balance'],
                if not any([inicial, debit, credit, balance]):
                    continue
                data = {
                    'partner_name': det['partner_name'],
                    'balanceinit': inicial,
                    'debit': debit,
                    'credit': credit,
                    'balance': balance,
                }
                if not det['p_idx']:
                    unknown = data
                    continue
                res.append(data)
            if unknown:
                res.append(unknown)
        return res

    def _get_analytic_ledger(self, account, ctx=None):
        """
        TODO
        """
        ctx = ctx or {}
        res = []
        aml_obj = self.pool.get('account.move.line')
        if account['type'] in ('other', 'liquidity', 'receivable', 'payable'):
            # TODO: When period is empty fill it with all periods from
            # fiscalyear but the especial period
            periods = ', '.join([str(i) for i in ctx['periods']])
            # periods = str(tuple(ctx['periods']))
            where = """where aml.period_id in (%s) and aa.id = %s
            and aml.state <> 'draft'""" % (periods, account['id'])
            if ctx.get('currency_id', False):
                where = where + \
                    """ and aml.currency_id = {currency_id}""".format(
                        currency_id=ctx['currency_id'])
            if ctx.get('partner_id', False):
                where = where + \
                    """ and aml.partner_id = {partner_id}""".format(
                        partner_id=ctx['partner_id'])
            if ctx.get('state', 'posted') == 'posted':
                where += "AND am.state = 'posted'"
            sql_detalle = """select aml.id as id, aj.name as diario,
                aa.name as descripcion,
                (select name from res_partner where aml.partner_id = id)
                as partner,
                aa.code as cuenta, aa.id as aa_id, aml.name as name,
                aml.ref as ref,
                (select name from res_currency where aml.currency_id = id)
                as currency,
                aml.currency_id as currency_id,
                aml.partner_id as partner_id,
                aml.amount_currency as amount_currency,
                case when aml.debit is null then 0.00 else aml.debit end
                as debit,
                case when aml.credit is null then 0.00 else aml.credit end
                as credit,
                (select code from account_analytic_account
                where  aml.analytic_account_id = id) as analitica,
                aml.date as date, ap.name as periodo,
                am.name as asiento
                from account_move_line aml
                inner join account_journal aj on aj.id = aml.journal_id
                inner join account_account aa on aa.id = aml.account_id
                inner join account_period ap on ap.id = aml.period_id
                inner join account_move am on am.id = aml.move_id """ \
                + where + """ order by date, am.name"""

            self.cr.execute(sql_detalle)
            resultat = self.cr.dictfetchall()
            balance = account['balanceinit']
            company_currency = self.pool.get('res.currency').browse(
                self.cr, self.uid,
                self.get_company_currency(ctx['company_id'])).name
            # title = u'''
            # \t\t{date:<15}
            # \t\t{periodo:<12}
            # \t\t{partner:<150}
            # \t\t{asiento:<20}
            # '''
            for det in resultat:
                balance += det['debit'] - det['credit']
                res.append({
                    'aa_id': det['aa_id'],
                    'cuenta': det['cuenta'],
                    'id': det['id'],
                    'aml_brw': aml_obj.browse(self.cr, self.uid, det['id'],
                                              context=ctx),
                    'date': det['date'],
                    'journal': det['diario'],
                    # 'title': title.format(dict([i for i in
                    # det.iteritems()])),
                    'partner_id': det['partner_id'],
                    'partner': det['partner'],
                    'name': det['name'],
                    'entry': det['asiento'],
                    'ref': det['ref'],
                    'debit': det['debit'],
                    'credit': det['credit'],
                    'analytic': det['analitica'],
                    'period': det['periodo'],
                    'balance': balance,
                    'currency': det['currency'] or company_currency,
                    'currency_id': det['currency_id'],
                    'amount_currency': det['amount_currency'],
                    'amount_company_currency': det['debit'] - det['credit'] if
                    det['currency'] is None else 0.0,
                    'differential': det['debit'] - det['credit']
                    if det['currency'] is not None and not
                    det['amount_currency'] else 0.0,
                })
        return res

    def _get_balance_multicurrency(self, account, ctx=None):
        """
        @return the lines of the balance multicurrency report.
        """
        ctx = ctx or {}
        raw_aml_list = self._get_analytic_ledger(account, ctx=ctx)
        all_res = self.result_master(raw_aml_list, account, ctx)
        detail_level = ctx['lines_detail']
        res = []
        if ctx['group_by'] == 'currency':
            if detail_level == 'detail':
                for (key, value) in all_res['currency'].iteritems():
                    aux_res = list()
                    aux_res.append(self.create_report_line(
                        u'Resume Currency {0}'.format(key), {'currency': key}))
                    aux_res.append(value['init_balance'])
                    aux_res.extend(value['filter_lines'])
                    if value['xchange_total']:
                        aux_res.append(value['xchange_total'])
                    aux_res.append(value['real_total'])
                    res.append(aux_res)
            elif detail_level == 'total':
                for (key, value) in all_res['currency'].iteritems():
                    aux_res = list()
                    aux_res.append(self.create_report_line(
                        u'Resume Currency {0}'.format(key), {'currency': key}))
                    aux_res.append(value['init_balance'])
                    if value['xchange_total']:
                        aux_res.append(value['xchange_total'])
                    aux_res.append(value['real_total'])
                    res.append(aux_res)
            elif detail_level == 'full':
                for (key, value) in all_res['currency'].iteritems():
                    aux_res = list()
                    aux_res.append(self.create_report_line(
                        u'Resume Currency {0}'.format(key), {'currency': key}))
                    aux_res.append(value['init_balance'])
                    aux_res.extend(value['lines'])
                    for line in value['filter_lines']:
                        line['title'] = 'Total for ' + line['partner']
                    aux_res.extend(value['filter_lines'])
                    if value['xchange_total']:
                        aux_res.append(value['xchange_total'])
                    aux_res.append(value['real_total'])
                    res.append(aux_res)
        elif ctx['group_by'] == 'partner':
            partner_data = self.get_group_by_partner(all_res)
            if detail_level in ['detail', 'full']:
                for (key, value) in partner_data.iteritems():
                    aux_res = list()
                    aux_res.append(self.create_report_line(
                        u'Resume of partner {0}'.format(key),
                        {'partner': key}))
                    aux_res.extend(value['init_balance'])
                    aux_res.extend(value['filter_lines'])
                    if value['xchange_total']:
                        aux_res.extend(value['xchange_total'])
                    aux_res.extend(value['real_total'])
                    res.append(aux_res)
            if detail_level == 'total':
                for (key, value) in partner_data.iteritems():
                    aux_res = list()
                    aux_res.append(self.create_report_line(
                        u'Resume of partner {0}'.format(key),
                        {'partner': key}))
                    aux_res.extend(value['init_balance'])
                    if value['xchange_total']:
                        aux_res.extend(value['xchange_total'])
                    aux_res.extend(value['real_total'])
                    res.append(aux_res)
        return res

    def get_group_by_partner(self, all_res):
        """
        TODO
        """
        basic = dict(
            init_balance=[], total=[], lines=[], real_total=[],
            xchange_lines=[], xchange_total=[], filter_lines=[],
        )

        partner_keys = set()
        for values in all_res['currency'].values():
            for (partner, values2) in values['partner'].iteritems():
                partner_keys.add(partner)

        partner_keys = list(partner_keys)
        partner_data = {}.fromkeys(partner_keys)
        for key in partner_data.keys():
            partner_data[key] = copy.deepcopy(basic)

        for (curr, values) in all_res['currency'].iteritems():
            for (rp, values2) in values['partner'].iteritems():
                for field in values2.keys():
                    aux_val = \
                        copy.deepcopy(
                            all_res['currency'][curr]['partner'][rp][field])
                    if aux_val:
                        partner_data[rp][field] += \
                            isinstance(aux_val, list) and aux_val or [aux_val]
        return partner_data

    def check_result(self, all_res):
        """
        check that the dictionary is ok
        """
        for value in all_res.values():
            for (curr_key, value2) in value.iteritems():
                for (cval_key, value3) in value2.iteritems():

                    if cval_key in ['lines', 'xchange_lines', 'filter_lines']:
                        error = [line for line in value3 if line if
                                 line['currency'] != curr_key or
                                 value3.count(line) != 1]
                        if error:
                            raise osv.except_osv(
                                'error',
                                'lines with other currencys in ' + cval_key)
                    elif cval_key in ['real_total', 'init_balance', 'total',
                                      'xchange_total']:
                        error = (
                            value3 and (value3['currency'] != curr_key or
                                        value3['partner']) and value3 or False)
                        if error:
                            raise osv.except_osv(
                                'error',
                                'lines with other currencys in ' + cval_key)
                    elif cval_key == 'partner':
                        for (partner_key, value4) in value3.iteritems():
                            for (pval_key, val5) in value4.iteritems():
                                if pval_key in ['lines', 'xchange_lines',
                                                'filter_lines']:
                                    error = [
                                        line for line in val5 if line
                                        if line['currency'] != curr_key or
                                        line['partner'] != partner_key or
                                        val5.count(line) != 1]
                                    if error:
                                        raise osv.except_osv(
                                            'error',
                                            ('lines with other currencys in ' +
                                             pval_key))
                                elif pval_key in ['real_total', 'init_balance',
                                                  'total', 'xchange_total']:
                                    error = (
                                        val5 and (
                                            val5['currency'] != curr_key or
                                            val5['partner'] != partner_key) and
                                        val5 or False)
                                    if error:
                                        raise osv.except_osv(
                                            'error',
                                            ('lines with other currencys in '
                                             '%s' % pval_key))
                    else:
                        raise osv.except_osv(
                            'error', 'missing case ' + cval_key)

        raise osv.except_osv('its', 'ok')

    def aml_group_by_keys(self, aml_list, group_by_keys):
        """
        given a list of amls return a dictionary of groups given for
        group_by_keys
        @param aml_list: and aml list is a list of dictionaries where every
        dictionary represent a report line.
        @param group_by_keys: a list of the aml keys that you want to group
        @return: a dictiory { (group_by_x, group_by_y, ..): [ amls.. ] }
        """
        res = dict()
        for item in aml_list:
            key = tuple([item[col] for col in group_by_keys])
            res[key] = res.get(key, False) and res[key] + [item] or [item]
        return res

    def result_master(self, aml_list, account, ctx=None):
        """
        @param aml_list: and aml list is a list of dictionaries where every
        dictionary represent a report line.
        @param group_by_keys: a list of the aml keys that you want to group
        @return: a dictiory { (group_by_x, group_by_y, ..): [ amls.. ] }
        """
        ctx = ctx or {}
        res = dict()
        main_keys = {'currency': ['partner']}

        for key in main_keys.keys():
            res[key] = {}

        res_init = copy.deepcopy(res)
        res_init = self.get_initial_balance(
            res_init, account, main_keys, ctx=ctx.copy())

        res = self.fill_result(res, aml_list, main_keys, context=ctx)
        res = self.update_init_balance(res, res_init, main_keys)

        return res

    def update_init_balance(self, res, res_init, main_keys):
        """
        TODO
        """
        for (key, values1) in res_init.iteritems():
            for (key_id, values2) in values1.iteritems():
                line = {key: key_id}
                res = self.init_report_line_group(res, line, key, [])
                for subkey_list in main_keys.values():
                    for sk in subkey_list:
                        for sk_id in values2[sk].keys():
                            line = {key: key_id, sk: sk_id}
                            res = self.init_report_line_group(res, line, key,
                                                              [sk])

        for (key, values1) in res_init.iteritems():
            for (key_id, values2) in values1.iteritems():
                res_init[key][key_id]['total'].pop('title')
                res[key][key_id]['init_balance'].update(
                    res_init[key][key_id]['total'])
                for subkey_list in main_keys.values():
                    for sk in subkey_list:
                        for sk_id in values2[sk].keys():
                            res_init[key][key_id][sk][sk_id]['total'].pop(
                                'title')
                            res[key][key_id][sk][sk_id]['init_balance'].update(
                                res_init[key][key_id][sk][sk_id]['total'])

        return res

    def remove_company_currency_exchange_line(self, res, main_keys,
                                              context=None):
        """
        Update the dictionary given in res. Remove the exchange line when the
        a group of currency is the company currency.
        @return True
        """
        cr, uid = self.cr, self.uid
        ctx = context or {}
        curr = self.pool.get('res.currency').browse(
            cr, uid, self.get_curr(ctx['company_id'])).name
        if res['currency'].get(curr, False):
            res['currency'][curr]['xchange_lines'] = []
            res['currency'][curr]['xchange_total'] = {}
            for subkey_list in main_keys.values():
                for sk in subkey_list:
                    for sk_id in res['currency'][curr][sk].keys():
                        # TODO: Ask to kathy@vauxoo.com why there are to
                        # assignment to same key with two different types
                        res['currency'][curr][sk][sk_id]['xchange_total'] = []
                        res['currency'][curr][sk][sk_id]['xchange_total'] = {}
        return res

    def init_report_line_group(self, res, line, key, subkeys):
        """
        Update the dictionary given in the paramenter res with the
        initialization values of the group a init dictionary used to defined
        the group.
        @param key: the name of the column in the report.
        @return True
        """
        basic = dict(
            init_balance={}, total={}, lines=[], real_total={},
            xchange_lines=[], xchange_total={}, filter_lines=[],
        )
        group_dict = copy.deepcopy(basic)
        for subkey in subkeys:
            group_dict[subkey] = {}

        rows = dict(
            total=u'Accumulated in {0}',
            real_total=u'Total in {0}',
            init_balance=u'Initial Balance in {0}',
            xchange_total=u'Exchange Differencial in {0}',
        )
        if not res[key].get(line[key], False):
            res[key][line[key]] = copy.deepcopy(group_dict)
            for (row, title_str) in rows.iteritems():
                res[key][line[key]][row] = self.create_report_line(
                    title_str.format(line[key]), {key: line[key]})

        for subkey in subkeys:
            if not res[key][line[key]][subkey].get(line[subkey], False):
                res[key][line[key]][subkey].update(
                    {line[subkey]: copy.deepcopy(basic)})
                for (row, title_str) in rows.iteritems():
                    res[key][line[key]][subkey][line[subkey]][row] = \
                        self.create_report_line(
                            title_str.format(line[subkey]) + u' in {0}'.
                            format(line[key]),
                            {key: line[key], subkey: line[subkey]})
        return res

    def get_initial_balance(self, res, account, main_keys, ctx):
        """
        This method update the res dictionary given with the inital balance of
        the accounts.
        @param main_keys: dictionary with the keys ans subkeys of every group.
        @return True
        """
        ctx = ctx or {}
        ctx['periods'] = self.get_previous_periods(ctx['periods'], ctx)
        previous_aml = self._get_analytic_ledger(account, ctx=ctx)
        res = self.fill_result(res, previous_aml, main_keys, context=ctx)
        return res

    def fill_result(self, res, aml_list, main_keys, context=None):
        """
        TODO
        """
        ctx = context or {}
        for line in aml_list:
            for (key, subkeys) in main_keys.iteritems():
                self.update_report_line(res, line, key, subkeys)

        res = self.get_real_totals(res, main_keys)
        res = self.get_filter_lines(res, main_keys)
        res = self.remove_company_currency_exchange_line(res, main_keys,
                                                         context=ctx.copy())

        # TODO: Uncomment this block of code to print the debug data.
        # topprint = \
        #    '{amount_company_currency:<8}{amount_currency:<8}{differential}'
        # for (key, values1) in res.iteritems():
        #     for (key_id, values2) in values1.iteritems():
        #         for subkey_list in main_keys.values():
        #             pprint.pprint((key_id,
        #                 [item['id'] for item in values2['lines']],
        #                 (topprint.format(**values2['total'])),
        #                 ))
        #             for subkey in subkey_list:
        #                 for (subkey_id, values3) in
        #                        values2[subkey].iteritems():
        #                      pprint.pprint((key_id, subkey_id,
        #                          [item['id'] for item in values3['lines']],
        #                          (topprint.format(**values3['total'])),
        #                          ))
        return res

    def get_previous_periods(self, period_ids, ctx=None):
        """
        @param period_ids: recieve a list of periods, period ids list.
        @return the previous period ids.
        """
        cr, uid = self.cr, self.uid
        ctx = ctx or {}
        ap_obj = self.pool.get('account.period')
        period_ids = isinstance(period_ids, (int, long)) and [period_ids] \
            or period_ids
        fy_id = ap_obj.browse(cr, uid, period_ids[0],
                              context=ctx).fiscalyear_id.id
        early_dt_start_ap_id = ap_obj.search(
            cr, uid, [('id', 'in', period_ids)],
            context=ctx, order='date_start asc', limit=1)[0]
        date_init = ap_obj.browse(
            cr, uid, early_dt_start_ap_id, context=ctx).date_start
        ap_ids = ap_obj.search(
            cr, uid, [('date_stop', '<=', date_init,),
                      ('fiscalyear_id', '=', fy_id)], context=ctx)
        return ap_ids

    def create_report_line(self, title, default_values=None):
        """
        return an empty dictionary to be use as a init balance line or a total
        line in the report.
        @param title: name show in the line of the report
        """
        default_values = default_values or {}
        res = {}.fromkeys(['id', 'date', 'journal', 'partner', 'title', 'name',
                           'entry', 'ref', 'debit', 'credit', 'analytic',
                           'period', 'balance', 'currency', 'amount_currency',
                           'amount_company_currency', 'differential'], str())
        res.update(
            debit=0.0, credit=0.0, balance=0.0, amount_currency=0.0,
            amount_company_currency=0.0, differential=0.0,
            title=title)
        res.update(default_values)
        return res

    def _update_report_line(self, res, line, key, subkey, line_field,
                            total_field):
        """
        TODO
        """
        update_fields_list = self.get_fields()[0]
        res[key][line[key]][line_field] += [line]
        res[key][line[key]][subkey][line[subkey]][line_field] += [line]
        for field in update_fields_list:
            res[key][line[key]][total_field][field] += line[field]
            res[key][line[key]][subkey][line[subkey]][total_field][field] += \
                line[field]
        res[key][line[key]][total_field].update({key: line[key]})
        res[key][line[key]][subkey][line[subkey]][total_field].update(
            {key: line[key], subkey: line[subkey]})

    def update_report_line(self, res, line, key, subkeys):
        """
        Update the dictionary given in res to add the lines associaed to the
        given group and to also update the total column while the move lines
        have benn grouping.
        @param key: the name of the column in the report.
        @return True
        """
        subkeys = subkeys or []
        res = self.init_report_line_group(res, line, key, subkeys)
        if not line['differential']:
            for subkey in subkeys:
                self._update_report_line(res, line, key, subkey, 'lines',
                                         'total')
        else:
            for subkey in subkeys:
                self._update_report_line(res, line, key, subkey,
                                         'xchange_lines', 'xchange_total')
        return True

    def get_filter_lines(self, res, main_keys):
        """
        Update the dictionary given in res to the filter lines of every group
        @param main_keys: dictionary { key: subkeys}
        @return True
        """
        for (key, subkeys) in main_keys.iteritems():
            for key_id in res[key].keys():
                for subkey in subkeys:
                    for (subkey_key, values) in \
                            res[key][key_id][subkey].iteritems():
                        res[key][key_id]['filter_lines'].\
                            append(values['total'])
                        res[key][key_id][subkey][subkey_key]['filter_lines'] =\
                            res[key][key_id][subkey][subkey_key]['lines']
        # TODO: add all the subkeys lines, need to filter this is some way to
        # only print one subkey lines.
        return res

    def get_fields(self):
        """
        TODO
        """
        update_fields_list = [
            'debit', 'credit', 'balance', 'amount_currency',
            'amount_company_currency', 'differential']
        copy_fields_list = [
            'id', 'date', 'journal', 'partner', 'title', 'name',
            'entry', 'ref', 'analytic', 'period', 'currency']
        return update_fields_list, copy_fields_list

    def _get_real_totals(self, res, overwrite_fields):
        """
        TODO
        """
        update_fields_list = self.get_fields()[0]
        for field in update_fields_list:
            res['real_total'][field] = \
                res['init_balance'][field] + \
                res['xchange_total'][field] + \
                res['total'][field]
        for field in overwrite_fields:
            res['real_total'][field] = \
                res['total'][field]
        return res

    def get_real_totals(self, res, main_keys):
        """
        Update the dictionary given in res to the real total of every group
        @return True
        """
        for (key, subkey_list) in main_keys.iteritems():
            for key_id in res[key].keys():
                self._get_real_totals(res[key][key_id], [key])
                for subkey in subkey_list:
                    for subkey_key in res[key][key_id][subkey].keys():
                        self._get_real_totals(
                            res[key][key_id][subkey][subkey_key],
                            [key, subkey])
        return res

    def get_group_total(self, group_list, total_str, main_group,
                        remove_lines=False):
        """
        @param group_list: list of dictionaries every list represent a group of
        aml lines, and every dictionary represent a aml line.
        @param remove_lines: Flag that indicate what to return. If not set
        (default False) will return all the group lines and plus the new line
        for the total of the group. If set (call with remove_lines=True) will
        only the line with the total of the group of lines.
        @return a list of lines to prin in the balance multicurrency report.
        Return one totalization line by a given lists of groups.

        Note: A list of groups is a list o dictionaries where every dictionary
        represent a report line.
        """
        total_group = dict()
        for aml_group in group_list:
            res3 = {}.fromkeys(['id', 'date', 'journal', 'partner', 'title',
                                'name', 'entry', 'ref', 'debit', 'credit',
                                'analytic', 'period', 'balance', 'currency',
                                'amount_currency', 'amount_company_currency',
                                'differential'])
            res3.update(
                title=aml_group[0] and total_str.format(**aml_group[0]) or
                'TOTAL',
                debit=0.0, credit=0.0, balance=0.0,
                amount_currency=0.0, amount_company_currency=0.0,
                differential=0.0,
                currency=aml_group[0]['currency'])
            for line in aml_group:
                res3['debit'] += line['debit']
                res3['credit'] += line['credit']
                res3['balance'] += line['balance']
                res3['amount_currency'] += line['amount_currency']
                res3['amount_company_currency'] += \
                    line['amount_company_currency']
                res3['differential'] += line['differential']

            key = aml_group[0][main_group]
            total_group[key] = total_group.get(key, False) and \
                total_group[key] + [res3] or [res3]
            aml_group += [res3]
        return total_group.values() if remove_lines else group_list

    def _get_journal_ledger(self, account, ctx=None):
        res = []
        am_obj = self.pool.get('account.move')
        if account['type'] in ('other', 'liquidity', 'receivable', 'payable'):
            # TODO: When period is empty fill it with all periods from
            # fiscalyear but the especial period
            periods = ', '.join([str(i) for i in ctx['periods']])
            # periods = str(tuple(ctx['periods']))
            where = \
                """where aml.period_id in (%s) and aa.id = %s
                    and aml.state <> 'draft'""" % (periods, account['id'])
            if ctx.get('state', 'posted') == 'posted':
                where += "AND am.state = 'posted'"
            sql_detalle = """SELECT
                DISTINCT am.id as am_id,
                aj.name as diario,
                am.name as name,
                am.date as date,
                ap.name as periodo
                from account_move_line aml
                inner join account_journal aj on aj.id = aml.journal_id
                inner join account_account aa on aa.id = aml.account_id
                inner join account_period ap on ap.id = aml.period_id
                inner join account_move am on am.id = aml.move_id """ \
                    + where + """ order by date, am.name"""

            self.cr.execute(sql_detalle)
            resultat = self.cr.dictfetchall()
            for det in resultat:
                res.append({
                    'am_id': det['am_id'],
                    'journal': det['diario'],
                    'name': det['name'],
                    'date': det['date'],
                    'period': det['periodo'],
                    'obj': am_obj.browse(self.cr, self.uid, det['am_id'])
                })
        return res

    def lines(self, form, level=0):
        """
        Returns all the data needed for the report lines (account info plus
        debit/credit/balance in the selected period and the full year)
        """
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        fiscalyear_obj = self.pool.get('account.fiscalyear')

        def _get_children_and_consol(cr, uid, ids, level, context=None,
                                     change_sign=False):
            aa_obj = self.pool.get('account.account')
            ids2 = []
            for aa_brw in aa_obj.browse(cr, uid, ids, context):
                if aa_brw.child_id and aa_brw.level < \
                        level and aa_brw.type != 'consolidation':
                    if not change_sign:
                        ids2.append([aa_brw.id, True, False, aa_brw])
                    ids2 += _get_children_and_consol(
                        cr, uid, [x.id for x in aa_brw.child_id], level,
                        context, change_sign=change_sign)
                    if change_sign:
                        ids2.append(aa_brw.id)
                    else:
                        ids2.append([aa_brw.id, False, True, aa_brw])
                else:
                    if change_sign:
                        ids2.append(aa_brw.id)
                    else:
                        ids2.append([aa_brw.id, True, True, aa_brw])
            return ids2

        #######################################################################
        # CONTEXT FOR ENDIND BALANCE                                          #
        #######################################################################
        def _ctx_end(ctx):
            ctx_end = ctx
            ctx_end['filter'] = form.get('filter', 'all')
            ctx_end['fiscalyear'] = fiscalyear.id

            if ctx_end['filter'] not in ['bydate', 'none']:
                special = self.special_period(form['periods'])
            else:
                special = False

            if form['filter'] in ['byperiod', 'all']:
                if special:
                    ctx_end['periods'] = period_obj.search(
                        self.cr, self.uid,
                        [('id', 'in', form['periods'] or
                          ctx_end.get('periods', False))])
                else:
                    ctx_end['periods'] = period_obj.search(
                        self.cr, self.uid,
                        [('id', 'in', form['periods'] or
                          ctx_end.get('periods', False)),
                         ('special', '=', False)])

            if form['filter'] in ['bydate', 'all', 'none']:
                ctx_end['date_from'] = form['date_from']
                ctx_end['date_to'] = form['date_to']

            return ctx_end.copy()

        def missing_period(ctx_init):

            ctx_init['fiscalyear'] = fiscalyear_obj.search(
                self.cr, self.uid, [('date_stop', '<', fiscalyear.date_start)],
                order='date_stop') and \
                fiscalyear_obj.search(
                    self.cr, self.uid,
                    [('date_stop', '<', fiscalyear.date_start)],
                    order='date_stop')[-1] or []
            ctx_init['periods'] = period_obj.search(
                self.cr, self.uid,
                [('fiscalyear_id', '=', ctx_init['fiscalyear']),
                 ('date_stop', '<', fiscalyear.date_start)])
            return ctx_init
        #######################################################################
        # CONTEXT FOR INITIAL BALANCE                                         #
        #######################################################################

        def _ctx_init(ctx):
            ctx_init = self.context.copy()
            ctx_init['filter'] = form.get('filter', 'all')
            ctx_init['fiscalyear'] = fiscalyear.id

            if form['filter'] in ['byperiod', 'all']:
                ctx_init['periods'] = form['periods']
                if not ctx_init['periods']:
                    ctx_init = missing_period(ctx_init.copy())
                date_start = min(
                    [period.date_start for period in
                     period_obj.browse(self.cr, self.uid,
                                       ctx_init['periods'])])
                ctx_init['periods'] = period_obj.search(
                    self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                        ('date_stop', '<=', date_start)])
            elif form['filter'] in ['bydate']:
                ctx_init['date_from'] = fiscalyear.date_start
                ctx_init['date_to'] = form['date_from']
                ctx_init['periods'] = period_obj.search(
                    self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                        ('date_stop', '<=',
                                         ctx_init['date_to'])])
            elif form['filter'] == 'none':
                ctx_init['periods'] = period_obj.search(
                    self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                        ('special', '=', True)])
                date_start = min(
                    [period.date_start for period in
                     period_obj.browse(self.cr, self.uid,
                                       ctx_init['periods'])])
                ctx_init['periods'] = period_obj.search(
                    self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                        ('date_start', '<=', date_start),
                                        ('special', '=', True)])

            return ctx_init.copy()

        def zfunction(nval):
            return abs(nval) < 0.005 and 0.0 or nval
        self.context = dict(self.context)
        account_ids = []
        self.context['state'] = form['target_move'] or 'posted'

        self.from_currency_id = self.get_company_currency(
            form['company_id'] and
            isinstance(form['company_id'], (list, tuple)) and
            form['company_id'][0] or form['company_id'])
        if not form['currency_id']:
            self.to_currency_id = self.from_currency_id
        else:
            self.to_currency_id = form['currency_id'] and \
                isinstance(form['currency_id'], (list, tuple)) and \
                form['currency_id'][0] or form['currency_id']

        if 'account_list' in form and form['account_list']:
            account_ids = form['account_list']
            account_list = form['account_list']
            del form['account_list']

        credit_account_ids = self.get_company_accounts(
            form['company_id'] and
            isinstance(form['company_id'], (list, tuple)) and
            form['company_id'][0] or form['company_id'], 'credit')

        debit_account_ids = self.get_company_accounts(
            form['company_id'] and
            isinstance(form['company_id'], (list, tuple)) and
            form['company_id'][0] or form['company_id'], 'debit')

        if form.get('fiscalyear'):
            if isinstance(form.get('fiscalyear'), (list, tuple)):
                fiscalyear = form['fiscalyear'] and form['fiscalyear'][0]
            elif isinstance(form.get('fiscalyear'), (int,)):
                fiscalyear = form['fiscalyear']
        fiscalyear = fiscalyear_obj.browse(self.cr, self.uid, fiscalyear)

        ################################################################
        # Get the accounts                                             #
        ################################################################
        all_account_ids = _get_children_and_consol(
            self.cr, self.uid, account_ids, 100, self.context)

        account_ids = _get_children_and_consol(
            self.cr, self.uid, account_ids,
            form['display_account_level'] and
            form['display_account_level'] or 100, self.context)

        credit_account_ids = _get_children_and_consol(
            self.cr, self.uid, credit_account_ids, 100, self.context,
            change_sign=True)

        debit_account_ids = _get_children_and_consol(
            self.cr, self.uid, debit_account_ids, 100, self.context,
            change_sign=True)

        credit_account_ids = list(set(
            credit_account_ids) - set(debit_account_ids))
        #
        # Generate the report lines (checking each account)
        #

        tot_check = False

        if not form['periods']:
            form['periods'] = period_obj.search(
                self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                    ('special', '=', False)],
                order='date_start asc')
            if not form['periods']:
                raise osv.except_osv(_('UserError'), _(
                    'The Selected Fiscal Year Does not have Regular Periods'))

        if form['columns'] == 'qtr':
            period_ids = period_obj.search(
                self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                    ('special', '=', False)],
                order='date_start asc')
            aval = 0
            lval = []
            pval = []
            for xval in period_ids:
                aval += 1
                if aval < 3:
                    lval.append(xval)
                else:
                    lval.append(xval)
                    pval.append(lval)
                    lval = []
                    aval = 0
            tot_bal1 = 0.0
            tot_bal2 = 0.0
            tot_bal3 = 0.0
            tot_bal4 = 0.0
            tot_bal5 = 0.0
        elif form['columns'] == 'thirteen':
            period_ids = period_obj.search(
                self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id),
                                    ('special', '=', False)],
                order='date_start asc')
            tot_bal1 = 0.0
            tot_bal1 = 0.0
            tot_bal2 = 0.0
            tot_bal3 = 0.0
            tot_bal4 = 0.0
            tot_bal5 = 0.0
            tot_bal6 = 0.0
            tot_bal7 = 0.0
            tot_bal8 = 0.0
            tot_bal9 = 0.0
            tot_bal10 = 0.0
            tot_bal11 = 0.0
            tot_bal12 = 0.0
            tot_bal13 = 0.0
        else:
            ctx_end = _ctx_end(self.context.copy())
            tot_bin = 0.0
            tot_deb = 0.0
            tot_crd = 0.0
            tot_ytd = 0.0
            tot_eje = 0.0

        res = {}
        result_acc = []
        tot = {}

        ###############################################################
        # Calculations of credit, debit and balance,
        # without repeating operations.
        ###############################################################

        account_black_ids = account_obj.search(
            self.cr, self.uid, ([('id', 'in', [i[0] for i in all_account_ids]),
                                 ('type', 'not in', ('view',
                                                     'consolidation'))]))

        account_not_black_ids = account_obj.search(
            self.cr, self.uid, ([('id', 'in', [i[0] for i in all_account_ids]),
                                 ('type', '=', 'view')]))

        acc_cons_ids = account_obj.search(
            self.cr, self.uid, ([('id', 'in', [i[0] for i in all_account_ids]),
                                 ('type', 'in', ('consolidation',))]))

        account_consol_ids = acc_cons_ids and \
            account_obj._get_children_and_consol(self.cr, self.uid,
                                                 acc_cons_ids) or []

        account_black_ids += account_obj.search(self.cr, self.uid, (
            [('id', 'in', account_consol_ids),
             ('type', 'not in',
              ('view', 'consolidation'))]))

        account_black_ids = list(set(account_black_ids))

        c_account_not_black_ids = account_obj.search(self.cr, self.uid, ([
            ('id', 'in',
             account_consol_ids),
            ('type', '=', 'view')]))
        delete_cons = False
        if c_account_not_black_ids:
            delete_cons = set(account_not_black_ids) & set(
                c_account_not_black_ids) and True or False
            account_not_black_ids = list(
                set(account_not_black_ids) - set(c_account_not_black_ids))

        # This could be done quickly with a sql sentence
        account_not_black = account_obj.browse(
            self.cr, self.uid, account_not_black_ids)
        account_not_black.sorted(key=lambda x: x.level, reverse=True)
        account_not_black_ids = [i.id for i in account_not_black]

        c_account_not_black = account_obj.browse(
            self.cr, self.uid, c_account_not_black_ids)
        c_account_not_black.sorted(key=lambda x: x.level, reverse=True)
        c_account_not_black_ids = [i.id for i in c_account_not_black]

        if delete_cons:
            account_not_black_ids = c_account_not_black_ids + \
                account_not_black_ids
            account_not_black = c_account_not_black + account_not_black
        else:
            acc_cons_brw = account_obj.browse(
                self.cr, self.uid, acc_cons_ids)
            acc_cons_brw.sorted(key=lambda x: x.level, reverse=True)
            acc_cons_ids = [i.id for i in acc_cons_brw]

            account_not_black_ids = c_account_not_black_ids + \
                acc_cons_ids + account_not_black_ids
            account_not_black = c_account_not_black + \
                acc_cons_brw + account_not_black

        # All accounts per period
        all_ap = {}

        # Iteration limit depending on the number of columns
        if form['columns'] == 'thirteen':
            limit = 13
        elif form['columns'] == 'qtr':
            limit = 5
        else:
            limit = 1

        for p_act in range(limit):
            if limit != 1:
                if p_act == limit - 1:
                    form['periods'] = period_ids
                else:
                    if form['columns'] == 'thirteen':
                        form['periods'] = [period_ids[p_act]]
                    elif form['columns'] == 'qtr':
                        form['periods'] = pval[p_act]

            if form['inf_type'] == 'IS':
                ctx_to_use = _ctx_end(self.context.copy())
            else:
                ctx_i = _ctx_init(self.context.copy())
                ctx_to_use = _ctx_end(self.context.copy())

            account_black = account_obj.browse(
                self.cr, self.uid, account_black_ids, ctx_to_use)

            if form['inf_type'] == 'BS':
                account_black_init = account_obj.browse(
                    self.cr, self.uid, account_black_ids, ctx_i)

            # Black
            dict_black = {}
            for i in account_black:
                debit = i.debit
                credit = i.credit
                dict_black[i.id] = {
                    'obj': i,
                    'debit': debit,
                    'credit': credit,
                    'balance': debit - credit
                }
                if form['inf_type'] == 'BS':
                    dict_black[i.id]['balanceinit'] = 0.0

            # If the report is a balance sheet
            # Balanceinit values are added to the dictionary
            if form['inf_type'] == 'BS':
                for i in account_black_init:
                    dict_black[i.id]['balanceinit'] = i.balance

            # Not black
            dict_not_black = {}
            for i in account_not_black:
                dict_not_black[i.id] = {
                    'obj': i, 'debit': 0.0, 'credit': 0.0, 'balance': 0.0}
                if form['inf_type'] == 'BS':
                    dict_not_black[i.id]['balanceinit'] = 0.0

            # It makes a copy because they modify
            all_account = dict_black.copy()

            for acc_id in account_not_black_ids:
                acc_childs = dict_not_black[acc_id]['obj'].type == 'view' \
                    and dict_not_black[acc_id]['obj'].child_id \
                    or dict_not_black[acc_id]['obj'].child_consol_ids
                for child_id in acc_childs:
                    if child_id.type == 'consolidation' and delete_cons:
                        continue
                    if not all_account.get(child_id.id):
                        continue
                    dict_not_black[acc_id]['debit'] += \
                        all_account[child_id.id].get('debit')
                    dict_not_black[acc_id]['credit'] += \
                        all_account[child_id.id].get('credit')
                    dict_not_black[acc_id]['balance'] += \
                        all_account[child_id.id].get('balance')
                    if form['inf_type'] == 'BS':
                        dict_not_black[acc_id]['balanceinit'] += \
                            all_account[child_id.id].get('balanceinit')
                all_account[acc_id] = dict_not_black[acc_id]

            if p_act == limit - 1:
                all_ap['all'] = all_account
            else:
                if form['columns'] == 'thirteen':
                    all_ap[p_act] = all_account
                elif form['columns'] == 'qtr':
                    all_ap[p_act] = all_account

        ###############################################################
        # End of the calculations of credit, debit and balance
        #
        ###############################################################

        for aa_id in account_ids:
            idx = aa_id[0]
            if aa_id[3].type == 'consolidation' and delete_cons:
                continue
            #
            # Check if we need to include this level
            #
            if not form['display_account_level'] or \
                    aa_id[3].level <= form['display_account_level']:
                res = {
                    'id': idx,
                    'type': aa_id[3].type,
                    'code': aa_id[3].code,
                    'name': (aa_id[2] and not aa_id[1]) and 'TOTAL %s' %
                    (aa_id[3].name.upper()) or aa_id[3].name,
                    'parent_id': aa_id[3].parent_id and aa_id[3].parent_id.id,
                    'level': aa_id[3].level,
                    'label': aa_id[1],
                    'total': aa_id[2],
                    'change_sign': credit_account_ids and
                    (idx in credit_account_ids and -1 or 1) or 1
                }

                if form['columns'] == 'qtr':
                    for pn in range(1, 5):

                        if form['inf_type'] == 'IS':
                            debit, credit, balance = [zfunction(x) for x in (
                                all_ap[pn - 1][idx].get('debit', 0.0),
                                all_ap[pn - 1][idx].get('credit', 0.0),
                                all_ap[pn - 1][idx].get('balance', 0.0))]
                            res.update({
                                'dbr%s' % pn: self.exchange(debit),
                                'cdr%s' % pn: self.exchange(credit),
                                'bal%s' % pn: self.exchange(balance),
                            })
                        else:
                            i, debit, credit = [zfunction(x) for x in (
                                all_ap[pn - 1][idx].get('balanceinit', 0.0),
                                all_ap[pn - 1][idx].get('debit', 0.0),
                                all_ap[pn - 1][idx].get('credit', 0.0))]
                            balance = zfunction(i + debit - credit)
                            res.update({
                                'dbr%s' % pn: self.exchange(debit),
                                'cdr%s' % pn: self.exchange(credit),
                                'bal%s' % pn: self.exchange(balance),
                            })

                    if form['inf_type'] == 'IS':
                        debit, credit, balance = [zfunction(x) for x in (
                            all_ap['all'][idx].get('debit', 0.0),
                            all_ap['all'][idx].get('credit', 0.0),
                            all_ap['all'][idx].get('balance', 0.0))]
                        res.update({
                            'dbr5': self.exchange(debit),
                            'cdr5': self.exchange(credit),
                            'bal5': self.exchange(balance),
                        })
                    else:
                        i, debit, credit = [zfunction(x) for x in (
                            all_ap['all'][idx].get('balanceinit', 0.0),
                            all_ap['all'][idx].get('debit', 0.0),
                            all_ap['all'][idx].get('credit', 0.0))]
                        balance = zfunction(i + debit - credit)
                        res.update({
                            'dbr5': self.exchange(debit),
                            'cdr5': self.exchange(credit),
                            'bal5': self.exchange(balance),
                        })

                elif form['columns'] == 'thirteen':
                    pn = 1
                    for p_num in range(12):

                        if form['inf_type'] == 'IS':
                            debit, credit, balance = [zfunction(x) for x in (
                                all_ap[p_num][idx].get('debit', 0.0),
                                all_ap[p_num][idx].get('credit', 0.0),
                                all_ap[p_num][idx].get('balance', 0.0))]
                            res.update({
                                'dbr%s' % pn: self.exchange(debit),
                                'cdr%s' % pn: self.exchange(credit),
                                'bal%s' % pn: self.exchange(balance),
                            })
                        else:
                            i, debit, credit = [zfunction(x) for x in (
                                all_ap[p_num][idx].get('balanceinit', 0.0),
                                all_ap[p_num][idx].get('debit', 0.0),
                                all_ap[p_num][idx].get('credit', 0.0))]
                            balance = zfunction(i + debit - credit)
                            res.update({
                                'dbr%s' % pn: self.exchange(debit),
                                'cdr%s' % pn: self.exchange(credit),
                                'bal%s' % pn: self.exchange(balance),
                            })

                        pn += 1

                    if form['inf_type'] == 'IS':
                        debit, credit, balance = [zfunction(x) for x in (
                            all_ap['all'][idx].get('debit', 0.0),
                            all_ap['all'][idx].get('credit', 0.0),
                            all_ap['all'][idx].get('balance', 0.0))]
                        res.update({
                            'dbr13': self.exchange(debit),
                            'cdr13': self.exchange(credit),
                            'bal13': self.exchange(balance),
                        })
                    else:
                        i, debit, credit = [zfunction(x) for x in (
                            all_ap['all'][idx].get('balanceinit', 0.0),
                            all_ap['all'][idx].get('debit', 0.0),
                            all_ap['all'][idx].get('credit', 0.0))]
                        balance = zfunction(i + debit - credit)
                        res.update({
                            'dbr13': self.exchange(debit),
                            'cdr13': self.exchange(credit),
                            'bal13': self.exchange(balance),
                        })

                else:
                    i, debit, credit = [zfunction(x) for x in (
                        all_ap['all'][idx].get('balanceinit', 0.0),
                        all_ap['all'][idx].get('debit', 0.0),
                        all_ap['all'][idx].get('credit', 0.0))]
                    balance = zfunction(i + debit - credit)
                    res.update({
                        'balanceinit': self.exchange(i),
                        'debit': self.exchange(debit),
                        'credit': self.exchange(credit),
                        'ytd': self.exchange(debit - credit),
                    })

                    if form['inf_type'] == 'IS' and form['columns'] == 'one':
                        res.update({
                            'balance': self.exchange(debit - credit),
                        })
                    else:
                        res.update({
                            'balance': self.exchange(balance),
                        })

                #
                # Check whether we must include this line in the report or not
                #
                to_include = False

                if form['columns'] in ('thirteen', 'qtr'):
                    to_test = [False]
                    if form['display_account'] == 'mov' and aa_id[3].parent_id:
                        # Include accounts with movements
                        for xval in range(pn - 1):
                            to_test.append(res.get(
                                'dbr%s' % xval, 0.0) >= 0.005 and
                                True or False)
                            to_test.append(res.get(
                                'cdr%s' % xval, 0.0) >= 0.005 and
                                True or False)
                        if any(to_test):
                            to_include = True

                    elif form['display_account'] == 'bal' and \
                            aa_id[3].parent_id:
                        # Include accounts with balance
                        for xval in range(pn - 1):
                            to_test.append(res.get(
                                'bal%s' % xval, 0.0) >= 0.005 and
                                True or False)
                        if any(to_test):
                            to_include = True

                    elif form['display_account'] == 'bal_mov' and \
                            aa_id[3].parent_id:
                        # Include accounts with balance or movements
                        for xval in range(pn - 1):
                            to_test.append(res.get(
                                'bal%s' % xval, 0.0) >= 0.005 and
                                True or False)
                            to_test.append(res.get(
                                'dbr%s' % xval, 0.0) >= 0.005 and
                                True or False)
                            to_test.append(res.get(
                                'cdr%s' % xval, 0.0) >= 0.005 and
                                True or False)
                        if any(to_test):
                            to_include = True
                    else:
                        # Include all accounts
                        to_include = True
                elif form['columns'] in ('currency',):
                    to_include = True
                else:

                    if form['display_account'] == 'mov' and aa_id[3].parent_id:
                        # Include accounts with movements
                        if abs(debit) >= 0.005 or abs(credit) >= 0.005:
                            to_include = True
                    elif form['display_account'] == 'bal' and \
                            aa_id[3].parent_id:
                        # Include accounts with balance
                        if abs(balance) >= 0.005:
                            to_include = True
                    elif form['display_account'] == 'bal_mov' and \
                            aa_id[3].parent_id:
                        # Include accounts with balance or movements
                        if abs(balance) >= 0.005 or abs(debit) >= 0.005 or \
                                abs(credit) >= 0.005:
                            to_include = True
                    else:
                        # Include all accounts
                        to_include = True

                # ANALYTIC LEDGER
                if (to_include and form['analytic_ledger'] and
                        form['columns'] == 'four' and
                        form['inf_type'] == 'BS' and
                        res['type'] in ('other', 'liquidity', 'receivable',
                                        'payable')):
                    ctx_end.update(company_id=(form['company_id'] and
                                               isinstance(form['company_id'],
                                               (list, tuple)) and
                                               form['company_id'][0] or
                                               form['company_id']),
                                   report=form['columns'])
                    res['mayor'] = self._get_analytic_ledger(res, ctx=ctx_end)
                elif form['columns'] == 'currency':
                    ctx_end.update(
                        company_id=(form['company_id'] and
                                    isinstance(form['company_id'],
                                    (list, tuple)) and form['company_id'][0] or  # noqa
                                    form['company_id']),
                        group_by=form['group_by'],
                        lines_detail=form['lines_detail'],
                    )
                    res['mayor'] = self._get_balance_multicurrency(res,
                                                                   ctx=ctx_end)
                elif to_include and form['journal_ledger'] and \
                        form['columns'] == 'four' and form['inf_type'] == 'BS'\
                        and res['type'] in ('other', 'liquidity', 'receivable',
                                            'payable'):
                    res['journal'] = self._get_journal_ledger(res, ctx=ctx_end)
                elif to_include and form['partner_balance'] and \
                        form['columns'] == 'four' and form['inf_type'] == 'BS'\
                        and res['type'] in ('other', 'liquidity', 'receivable',
                                            'payable'):
                    res['partner'] = self._get_partner_balance(
                        res, ctx_i['periods'], ctx=ctx_end)
                else:
                    res['mayor'] = []

                if to_include:
                    result_acc.append(res)
                    #
                    # Check whether we must sumarize this line in the report or
                    # not
                    #
                    if form['tot_check'] and (res['id'] in account_list) and \
                            (res['id'] not in tot):
                        if form['columns'] == 'qtr':
                            tot_check = True
                            tot[res['id']] = True
                            tot_bal1 += res.get('bal1', 0.0)
                            tot_bal2 += res.get('bal2', 0.0)
                            tot_bal3 += res.get('bal3', 0.0)
                            tot_bal4 += res.get('bal4', 0.0)
                            tot_bal5 += res.get('bal5', 0.0)

                        elif form['columns'] == 'thirteen':
                            tot_check = True
                            tot[res['id']] = True
                            tot_bal1 += res.get('bal1', 0.0)
                            tot_bal2 += res.get('bal2', 0.0)
                            tot_bal3 += res.get('bal3', 0.0)
                            tot_bal4 += res.get('bal4', 0.0)
                            tot_bal5 += res.get('bal5', 0.0)
                            tot_bal6 += res.get('bal6', 0.0)
                            tot_bal7 += res.get('bal7', 0.0)
                            tot_bal8 += res.get('bal8', 0.0)
                            tot_bal9 += res.get('bal9', 0.0)
                            tot_bal10 += res.get('bal10', 0.0)
                            tot_bal11 += res.get('bal11', 0.0)
                            tot_bal12 += res.get('bal12', 0.0)
                            tot_bal13 += res.get('bal13', 0.0)
                        else:
                            tot_check = True
                            tot[res['id']] = True
                            tot_bin += res['balanceinit']
                            tot_deb += res['debit']
                            tot_crd += res['credit']
                            tot_ytd += res['ytd']
                            tot_eje += res['balance']

        if tot_check:
            str_label = form['lab_str']
            res2 = {
                'type': 'view',
                'name': 'TOTAL %s' % (str_label),
                'label': False,
                'total': True,
            }
            if form['columns'] == 'qtr':
                res2.update(
                    dict(
                        bal1=zfunction(tot_bal1),
                        bal2=zfunction(tot_bal2),
                        bal3=zfunction(tot_bal3),
                        bal4=zfunction(tot_bal4),
                        bal5=zfunction(tot_bal5),))
            elif form['columns'] == 'thirteen':
                res2.update(
                    dict(
                        bal1=zfunction(tot_bal1),
                        bal2=zfunction(tot_bal2),
                        bal3=zfunction(tot_bal3),
                        bal4=zfunction(tot_bal4),
                        bal5=zfunction(tot_bal5),
                        bal6=zfunction(tot_bal6),
                        bal7=zfunction(tot_bal7),
                        bal8=zfunction(tot_bal8),
                        bal9=zfunction(tot_bal9),
                        bal10=zfunction(tot_bal10),
                        bal11=zfunction(tot_bal11),
                        bal12=zfunction(tot_bal12),
                        bal13=zfunction(tot_bal13),))

            else:
                res2.update({
                    'balanceinit': tot_bin,
                    'debit': tot_deb,
                    'credit': tot_crd,
                    'ytd': tot_ytd,
                    'balance': tot_eje,
                })

            result_acc.append(res2)
        return result_acc


class ReportAfr1Cols(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="afr.1cols"
    _name = 'report.afr.1cols'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report.afr_template'
    _wrapped_report_class = AccountBalance


class ReportAfrAnalyticLedger(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="afr.analytic.ledger"
    _name = 'report.afr.analytic.ledger'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report.afr_template_analytic_ledger'
    _wrapped_report_class = AccountBalance

report_sxw.report_sxw(
    'report.afr.rml.1cols',
    'wizard.report',
    'account_financial_report/report/balance_full.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.2cols',
    'wizard.report',
    'account_financial_report/report/balance_full_2_cols.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.4cols',
    'wizard.report',
    'account_financial_report/report/balance_full_4_cols.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.analytic.ledger',
    'wizard.report',
    'account_financial_report/report/balance_full_4_cols_analytic_ledger.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.multicurrency',
    'wizard.report',
    'account_financial_report/report/balance_multicurrency.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.partner.balance',
    'wizard.report',
    'account_financial_report/report/balance_full_4_cols_partner_balance.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.journal.ledger',
    'wizard.report',
    'account_financial_report/report/balance_full_4_cols_journal_ledger.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.5cols',
    'wizard.report',
    'account_financial_report/report/balance_full_5_cols.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.qtrcols',
    'wizard.report',
    'account_financial_report/report/balance_full_qtr_cols.rml',
    parser=AccountBalance,
    header=False)

report_sxw.report_sxw(
    'report.afr.rml.13cols',
    'wizard.report',
    'account_financial_report/report/balance_full_13_cols.rml',
    parser=AccountBalance,
    header=False)


class ReportAfrPartnerBalance(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="afr.partner.balance"
    _name = 'report.afr.partner.balance'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report.afr_template_partner_balance'
    _wrapped_report_class = AccountBalance


class ReportAfrJournalLedger(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="afr.journal.ledger"
    _name = 'report.afr.journal.ledger'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report.afr_template_journal_ledger'
    _wrapped_report_class = AccountBalance


class ReportAfr13Cols(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="afr.13cols'"
    _name = 'report.afr.13cols'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report.afr_template'
    _wrapped_report_class = AccountBalance
