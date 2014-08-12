#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Luis Alejandro Martínez Faneyth
#
# This file is part of Condiment.
#
# Condiment is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Condiment is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# def django_deployserver():
#     """
#     """
#     env.condiment_static_dir = get_path([BASEDIR, 'condiment', 'data', 'static'])

#     env.condiment_supervisor_config = get_path([CONFDIR, 'data',
#                                              'condiment.supervisor.conf'])
#     env.condiment_uwsgi_config = get_path([CONFDIR, 'data',
#                                         'condiment.uwsgi.ini'])
#     env.condiment_nginx_config = get_path([CONFDIR, 'data',
#                                         'condiment.nginx.conf'])

#     docker_kill_all_containers()
#     local(('echo "'
#            'upstream uwsgi {\n'
#            '\tserver\t\t\t\tunix:///var/run/condiment/uwsgi.sock;\n'
#            '}\n'
#            '\n'
#            'server {\n'
#            '\tlisten\t\t\t\t8000;\n'
#            '\tserver_name\t\t\t127.0.0.1;\n'
#            '\tcharset\t\t\t\tutf-8;\n'
#            '\n'
#            '\tlocation /static {\n'
#            '\t\talias\t\t\t%(condiment_static_dir)s;\n'
#            '\t}\n'
#            '\n'
#            '\tlocation / {\n'
#            '\t\tuwsgi_pass\t\tuwsgi;\n'
#            '\t\tinclude\t\t\t/etc/nginx/uwsgi_params;\n'
#            '\t}\n'
#            '}'
#            '" > %(condiment_nginx_config)s') % env, capture=False)
#     local(('echo "'
#            '[program:condiment-celery]\n'
#            'command = /usr/bin/python %(basedir)s/manage.py celeryd\n'
#            'directory = %(basedir)s\n'
#            'user = www-data\n'
#            'numprocs = 1\n'
#            'stdout_logfile = /var/log/condiment/celeryd.log\n'
#            'stderr_logfile = /var/log/condiment/celeryd.log\n'
#            'autostart = true\n'
#            'autorestart = true\n'
#            'startsecs = 10\n'
#            'stopwaitsecs = 30\n'
#            '\n'
#            '[program:condiment-celerybeat]\n'
#            'command = /usr/bin/python %(basedir)s/manage.py celerybeat\n'
#            'directory = %(basedir)s\n'
#            'user = www-data\n'
#            'numprocs = 1\n'
#            'stdout_logfile = /var/log/condiment/celerybeat.log\n'
#            'stderr_logfile = /var/log/condiment/celerybeat.log\n'
#            'autostart = true\n'
#            'autorestart = true\n'
#            'startsecs = 10\n'
#            'stopwaitsecs = 30\n'
#            '" > %(condiment_supervisor_config)s') % env, capture=False)
#     local(('echo "'
#            '[uwsgi]\n'
#            'chdir = %(basedir)s\n'
#            'env = DJANGO_SETTINGS_MODULE=condiment.config.web\n'
#            'wsgi-file = %(basedir)s/condiment/web/wsgi.py\n'
#            'logto = /var/log/condiment/uwsgi.log\n'
#            'pidfile = /var/run/condiment/uwsgi.pid\n'
#            'socket = /var/run/condiment/uwsgi.sock\n'
#            'plugin = python\n'
#            '" > %(condiment_uwsgi_config)s') % env, capture=False)
#     local(('echo "#!/usr/bin/env bash\n'
#            'ln -fs /proc/self/fd /dev/fd\n'
#            'ln -fs %(condiment_nginx_config)s /etc/nginx/sites-enabled/\n'
#            'ln -fs %(condiment_uwsgi_config)s /etc/uwsgi/apps-enabled/\n'
#            'ln -fs %(condiment_supervisor_config)s /etc/supervisor/conf.d/\n'
#            '%(start_services)s\n'
#            'sleep 1200\n'
#            'exit 0'
#            '" > %(condiment_django_runserver_script)s') % env, capture=False)
#     local(('sudo bash -c '
#            '"%(docker)s run -d -p 127.0.0.1:8000:8000 '
#            '--name="%(condiment_runtime_container)s" '
#            '%(mounts)s %(condiment_runtime_image)s '
#            'bash %(condiment_django_runserver_script)s"') % env)
