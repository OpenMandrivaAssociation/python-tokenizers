%undefine _debugsource_packages

# Recreate the vendor archive after a version bump:
#   tar xf tokenizers-VERSION.tar.gz
#   cd tokenizers-VERSION/bindings/python
#   cargo vendor --locked ../../vendor
#   cd ../..
#   tar cJf python-tokenizers-VERSION-vendor.tar.xz vendor
#   abb store python-tokenizers-VERSION-vendor.tar.xz

Name:		python-tokenizers
Version:	0.23.1
Release:	2
Summary:	Fast state-of-the-art tokenizers for research and production
License:	Apache-2.0
Group:		Development/Python
URL:		https://github.com/huggingface/tokenizers
Source0:	https://files.pythonhosted.org/packages/source/t/tokenizers/tokenizers-%{version}.tar.gz
Source1:	%{name}-%{version}-vendor.tar.xz
# The Python module does not import huggingface_hub. from_pretrained uses
# the Rust hf-hub crate. Cooker has huggingface-hub 2.1.1.
Patch0:		python-tokenizers-0.23.1-hub2.patch

BuildSystem:	python
BuildRequires:	cargo
BuildRequires:	cmake
BuildRequires:	pkgconfig(oniguruma)
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	rust-packaging

%description
Provides an implementation of today's most used tokenizers, with a
focus on performance and versatility. Python bindings over the Rust
implementation.

%prep -a
tar xf %{SOURCE1}
%cargo_prep -v vendor
# cargo_prep writes a CWD-relative path; maturin/cargo also run from
# bindings/python/
sed -i "s#directory = \"vendor\"#directory = \"$PWD/vendor\"#" .cargo/config.toml

%build -p
export CARGO_HOME=$PWD/.cargo
export CARGO_NET_OFFLINE=true
export RUSTONIG_SYSTEM_LIBONIG=1

%build -a
rm -rf bindings/python/.cargo
ln -sfn ../../.cargo bindings/python/.cargo
pushd bindings/python
%cargo_license_summary
%{cargo_license} > ../../LICENSES.dependencies
popd

%files
%doc bindings/python/README.md
%license tokenizers/LICENSE LICENSES.dependencies
%{python_sitearch}/tokenizers
%{python_sitearch}/tokenizers-%{version}.dist-info
