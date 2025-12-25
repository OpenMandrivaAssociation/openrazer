%define dkms_name openrazer-driver
%define dkms_version 3.11.0

#define gitcommit 6ae1f7d55bf10cc6b5cb62a5ce99ff22c43e0701

Name: openrazer
Version: 3.11.0
Release: 2
Summary: Open source driver and user-space daemon for managing Razer devices

License: GPL-2.0
URL: https://github.com/openrazer/openrazer
Source0: https://github.com/openrazer/openrazer/releases/download/v%{version}/openrazer-%{version}.tar.xz
BuildRequires:  make

BuildArch: noarch

Requires: openrazer-kernel-modules-dkms
Requires: openrazer-daemon
Requires: python-openrazer

%description
Meta package for installing all required openrazer packages.


%package -n openrazer-kernel-modules-dkms
Summary: OpenRazer Driver DKMS package
Group: System Environment/Kernel

Obsoletes: razer-kernel-modules-dkms
Provides: razer-kernel-modules-dkms
Requires: dkms
Requires: make
Requires: udev
Requires(pre): shadow
Requires(post): dkms

%description -n openrazer-kernel-modules-dkms
Kernel driver for Razer devices (DKMS-variant)

%package -n openrazer-daemon
Summary: OpenRazer Service package
Group: System Environment/Daemons
Obsoletes: razer-daemon
Provides: razer-daemon
BuildRequires: python-devel
BuildRequires: python-setuptools
Requires: openrazer-kernel-modules-dkms
Requires: python

Requires: typelib(Gdk) = 3.0
Requires: python3-dbus
Requires: python-gobject3
Requires: python-gi
Requires: python-setproctitle
Requires: python3dist(pyudev)
Requires: python-daemonize
Requires: xautomation
Requires: libnotify

%description -n openrazer-daemon
Userspace daemon that abstracts access to the kernel driver. Provides a DBus service for applications to use.

%package -n python-openrazer
Summary: OpenRazer Python library
Group: System Environment/Libraries
Provides: python3-razer
BuildRequires: python3-devel
BuildRequires: python3-setuptools
Requires: openrazer-daemon
Requires: python
Requires: python3-dbus
Requires: python-gobject3
Requires: python-numpy

%description -n python-openrazer
Python library for accessing the daemon from Python.

%prep
%autosetup -n openrazer-%{version} -p1

%build
# noop

%install
rm -rf $RPM_BUILD_ROOT
# setup_dkms & udev_install -> razer-kernel-modules-dkms
# daemon_install -> razer_daemon
# python_library_install -> python3-razer
make DESTDIR=$RPM_BUILD_ROOT setup_dkms udev_install daemon_install python_library_install


%clean
rm -rf $RPM_BUILD_ROOT


%pre -n openrazer-kernel-modules-dkms
#!/bin/sh
set -e

getent group plugdev >/dev/null || groupadd -r plugdev

%posttrans -n openrazer-kernel-modules-dkms
#!/bin/sh
set -e

dkms install %{dkms_name}/%{dkms_version}

echo -e "\e[31m********************************************"
echo -e "\e[31m* To complete installation, please run:    *"
echo -e "\e[31m* # sudo gpasswd -a <yourUsername> plugdev *"
echo -e "\e[31m********************************************"
echo -e -n "\e[39m"

%preun -n openrazer-kernel-modules-dkms
#!/bin/sh

if [ "$(dkms status -m %{dkms_name} -v %{dkms_version})" ]; then
  dkms remove -m %{dkms_name} -v %{dkms_version} --all
fi



%files
# meta package is empty

%files -n openrazer-kernel-modules-dkms
%defattr(-,root,root,-)
# A bit hacky but it works
%{_udevrulesdir}/../razer_mount
%{_udevrulesdir}/99-razer.rules
%{_usrsrc}/%{dkms_name}-%{dkms_version}/

%files -n openrazer-daemon
%{_bindir}/openrazer-daemon
%{python_sitelib}/openrazer_daemon/
%{python_sitelib}/openrazer_daemon-*.egg-info/
%{_datadir}/openrazer/
%{_datadir}/dbus-1/services/org.razer.service
%{_prefix}/lib/systemd/user/openrazer-daemon.service
%{_mandir}/man5/razer.conf.5*
%{_mandir}/man8/openrazer-daemon.8*

%files -n python-openrazer
%{python_sitelib}/openrazer/
%{python_sitelib}/openrazer-*.egg-info/
