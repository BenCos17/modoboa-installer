"""Apache2 related tools."""

import os

from .. import package
from .. import system
from .. import utils

from . import base
from .uwsgi import Uwsgi


class Apache2(base.Installer):
	"""Apache2 installer."""

	appname = "apache2"
	daemon_name = "apache2"
	packages = {
		"deb": ["apache2", "libapache2-mod-proxy-uwsgi", "ssl-cert"],
		"rpm": ["httpd", "mod_ssl"]
	}

	def pre_run(self):
		"""Normalize configuration before rendering files."""
		if package.backend.FORMAT == "rpm":
			self.config.set(self.appname, "config_dir", "/etc/httpd")

	def get_daemon_name(self):
		"""Return the platform-specific service name."""
		if package.backend.FORMAT == "rpm":
			return "httpd"
		return super().get_daemon_name()

	def get_template_context(self):
		"""Additional variables."""
		context = super().get_template_context()
		context.update({
			"app_instance_path": (
				self.config.get("modoboa", "instance_path")),
			"uwsgi_socket_path": (
				Uwsgi(self.config, self.upgrade, self.restore).get_socket_path("modoboa")
			)
		})
		return context

	def _setup_config(self, app, hostname=None, extra_config=None):
		"""Custom app configuration."""
		if hostname is None:
			hostname = self.config.get("general", "hostname")
		context = self.get_template_context()
		context.update({"hostname": hostname, "extra_config": extra_config})
		src = self.get_file_path("{}.conf.tpl".format(app))
		group = None
		if package.backend.FORMAT == "deb":
			dst = os.path.join(
				self.config_dir, "sites-available", "{}.conf".format(hostname))
			utils.copy_from_template(src, dst, context)
			link = os.path.join(
				self.config_dir, "sites-enabled", os.path.basename(dst))
			if os.path.exists(link):
				return
			os.symlink(dst, link)
			if self.config.has_section(app):
				group = self.config.get(app, "user")
			user = "www-data"
		else:
			dst = os.path.join(
				self.config_dir, "conf.d", "{}.conf".format(hostname))
			utils.copy_from_template(src, dst, context)
			group = "uwsgi"
			user = "apache"
		if user and group:
			system.add_user_to_group(user, group)

	def post_run(self):
		"""Additional tasks."""
		extra_modoboa_config = ""

		if package.backend.FORMAT == "deb":
			utils.exec_cmd("a2enmod proxy proxy_http proxy_uwsgi rewrite ssl headers")

		hostname = "autoconfig.{}".format(
			self.config.get("general", "domain"))
		self._setup_config("autoconfig", hostname)

		if self.config.get("radicale", "enabled"):
			extra_modoboa_config += """
	ProxyPass /radicale/ http://localhost:5232/
	ProxyPassReverse /radicale/ http://localhost:5232/
	RequestHeader set X-Script-Name "/radicale"
	RequestHeader set X-Forwarded-Proto "https"
"""
		self._setup_config(
			"modoboa", extra_config=extra_modoboa_config)

		if not os.path.exists("{}/dhparam.pem".format(self.config_dir)):
			cmd = "openssl dhparam -dsaparam -out dhparam.pem 4096"
			utils.exec_cmd(cmd, cwd=self.config_dir)
