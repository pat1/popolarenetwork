%define name popolarenetwork
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: recorder for popolare network radio broadcast
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GNU GPL v2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Paolo Patruno <p.patruno@iperbole.bologna.it>
Url: https://github.com/pat1/popolarenetwork
Requires: python3-pyserial python3-simplejson

%description
\ 
      recorder for popolare network radio broadcast
      https://github.com/pat1/popolarenetwork
      

%prep
%setup -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
