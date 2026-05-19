<VirtualHost *:80>
	ServerName %hostname
	RewriteEngine On
	RewriteRule ^ https://%%{HTTP_HOST}%%{REQUEST_URI} [R=301,L]
</VirtualHost>

<VirtualHost *:443>
	ServerName %hostname
	DocumentRoot "%app_instance_path/frontend"

	SSLEngine on
	SSLCertificateFile %tls_cert_file
	SSLCertificateKeyFile %tls_key_file
	SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
	SSLCipherSuite "ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384"
	SSLHonorCipherOrder on
	SSLSessionCache shmcb:/var/run/apache2/ssl_scache(512000)

	ErrorLog /var/log/apache2/%{hostname}-error.log
	CustomLog /var/log/apache2/%{hostname}-access.log combined

	Alias /sitestatic/ "%app_instance_path/sitestatic/"
	Alias /media/ "%app_instance_path/media/"

	<Directory "%app_instance_path/frontend">
		Require all granted
		Options FollowSymLinks
		AllowOverride All
		FallbackResource /index.html
	</Directory>

	<Directory "%app_instance_path/sitestatic">
		Require all granted
	</Directory>

	<Directory "%app_instance_path/media">
		Require all granted
	</Directory>

	ProxyPass /sitestatic/ !
	ProxyPass /media/ !
	ProxyPassMatch ^/(api|accounts|autodiscover)(.*)$ unix:%uwsgi_socket_path|uwsgi://localhost/$1$2

%{extra_config}
</VirtualHost>
