<VirtualHost *:80>
	ServerName %hostname
	DocumentRoot "%app_instance_path"

	ErrorLog /var/log/apache2/%{hostname}-error.log
	CustomLog /var/log/apache2/%{hostname}-access.log combined

	ProxyPassMatch "^/(mail/config-v1.1.xml|mobileconfig)$" "unix:%uwsgi_socket_path|uwsgi://localhost/"
</VirtualHost>
