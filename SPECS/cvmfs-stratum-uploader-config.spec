Name:           cvmfs-stratum-uploader-config
Version:        0.3.2
Release:        1
Summary:        Provides example configuration for cvmfs-stratum-uploader.

Group:          Development/Libraries
License:        Apache License
URL:            git://github.com/stfc/cvmfs-stratum-uploader-config.git
Source0:        %name
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-${version}-${release}-root-%(%{__id_u} -n)

Vendor:         Science & Technology Facilities Council UK
Packager:       Michal Knapik <Michal.Knapik@stfc.ac.uk>

%define APPLICATION_ROOT        "/var/www/cvmfs-stratum-uploader"
%define CERTIFICATE_PATH        "/etc/grid-security"
%define PYTHON_PATH             `python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
%define SITES_AVAILABLE_PATH    "/etc/httpd/conf.d"
%define SECRET_KEY              "`openssl rand -base64 32`"
%define CSRF_MIDDLEWARE_SECRET  "`openssl rand -base64 32`"
%define HOSTNAME                `hostname`
#BuildRequires:  

AutoReqProv: no
Requires: openssl, httpd >= 2.2.15, cvmfs-stratum-uploader >= 0.3.2

%description
Provides configuration for cvmfs-stratum-uploader.

%prep

%build

%install
rm -rf $RPM_BUILD_ROOT
# create dirs
install -d $RPM_BUILD_ROOT/var
install -d $RPM_BUILD_ROOT/var/www
install -d $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader
install -d $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/db
install -d $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/media
install -d $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/static
# create files
install %{SOURCE0}/var/www/cvmfs-stratum-uploader/site.httpd.conf $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/
install %{SOURCE0}/var/www/cvmfs-stratum-uploader/application.cfg $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/
install %{SOURCE0}/var/www/cvmfs-stratum-uploader/db/db.sqlite3 $RPM_BUILD_ROOT/var/www/cvmfs-stratum-uploader/db/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(700,apache,apache) /var/www/cvmfs-stratum-uploader/db
%attr(744,apache,apache) /var/www/cvmfs-stratum-uploader/media
%attr(744,apache,apache) /var/www/cvmfs-stratum-uploader/static
%config %attr(644,-,-) /var/www/cvmfs-stratum-uploader/site.httpd.conf
%config %attr(644,-,-) /var/www/cvmfs-stratum-uploader/application.cfg
%config %attr(700,apache,apache) /var/www/cvmfs-stratum-uploader/db
%config %attr(600,apache,apache) /var/www/cvmfs-stratum-uploader/db/db.sqlite3
%defattr(-,root,root,-)
%doc

%post
echo 'Setup application config'
sed -i -e 's|__SECRET_KEY__|'%{SECRET_KEY}'|g' %{APPLICATION_ROOT}/application.cfg
sed -i -e 's|__CSRF_MIDDLEWARE_SECRET__|'%{CSRF_MIDDLEWARE_SECRET}'|g' %{APPLICATION_ROOT}/application.cfg
sed -i -e 's|__APPLICATION_ROOT__|'%{APPLICATION_ROOT}'|g' %{APPLICATION_ROOT}/application.cfg

echo 'Setup httpd site'
sed -i -e 's|__FULL_HOST_NAME__|'%{HOSTNAME}'|g' %{APPLICATION_ROOT}/site.httpd.conf
sed -i -e 's|__APPLICATION_ROOT__|'%{APPLICATION_ROOT}'|g' %{APPLICATION_ROOT}/site.httpd.conf
sed -i -e 's|__CERTIFICATE_PATH__|'%{CERTIFICATE_PATH}'|g' %{APPLICATION_ROOT}/site.httpd.conf
sed -i -e 's|__PYTHON_PATH__|'%{PYTHON_PATH}'|g' %{APPLICATION_ROOT}/site.httpd.conf

ln -sf %{APPLICATION_ROOT}/site.httpd.conf %{SITES_AVAILABLE_PATH}/cvmfs-stratum-uploader.conf

echo 'Setup database'
DJANGO_CONFIG_FILE=%{APPLICATION_ROOT}/application.cfg DJANGO_CONFIGURATION=production manage-cvmfs-stratum-uploader.py syncdb --verbosity=0
DJANGO_CONFIG_FILE=%{APPLICATION_ROOT}/application.cfg DJANGO_CONFIGURATION=production manage-cvmfs-stratum-uploader.py migrate --verbosity=0
echo 'Create static pages'
DJANGO_CONFIG_FILE=%{APPLICATION_ROOT}/application.cfg DJANGO_CONFIGURATION=production manage-cvmfs-stratum-uploader.py init_flatpages %{HOSTNAME} --verbosity=0

echo 'Unpack static files'
DJANGO_CONFIG_FILE=%{APPLICATION_ROOT}/application.cfg DJANGO_CONFIGURATION=production manage-cvmfs-stratum-uploader.py collectstatic --noinput --verbosity=0

%postun
rm %{SITES_AVAILABLE_PATH}/cvmfs-stratum-uploader.conf
rm -r %{APPLICATION_ROOT}/static

%changelog

