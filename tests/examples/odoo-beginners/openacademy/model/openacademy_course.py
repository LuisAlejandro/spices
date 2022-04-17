# -*- coding: utf-8 -*-

'''
This module creates the database model of Course
'''

from openerp import api, fields, models, _


class Course(models.Model):
    '''
    This class creates the database model of Course
    '''
    _name = 'openacademy.course'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    responsible_id = fields.Many2one('res.users', ondelete='set null',
                                     string="Responsible", index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         _( "The title of the course should not be the description")),

        ('name_unique',
         'UNIQUE(name)',
        _("The course title must be unique")),
    ]

    @api.one
    def copy(self, default=None):

        if default is None:
            default = {}

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])

        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)
