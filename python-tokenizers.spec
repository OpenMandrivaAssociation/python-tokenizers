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
Release:	3
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
BuildRequires:	pkgconfig(python3)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(wheel)

%description
Provides an implementation of today's most used tokenizers, with a
focus on performance and versatility. Python bindings over the Rust
implementation.

%prep -a
# Crates are already vendored. rust-packaging pulls python-rust2rpm, which
# still requires Python 3.14.
tar -xf %{SOURCE1}
mkdir -p .cargo
cat > .cargo/config.toml << EOF
[net]
offline = true

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "$PWD/vendor"
EOF

%build -p
export CARGO_HOME=$PWD/.cargo
export CARGO_NET_OFFLINE=true
export RUSTONIG_SYSTEM_LIBONIG=1
# pyo3 0.28.2 abi3-py310 falls back to the 3.14 stable ABI on 3.15.
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

%build -a
rm -rf bindings/python/.cargo
ln -sfn ../../.cargo bindings/python/.cargo
pushd bindings/python
cargo tree --locked --offline --edges no-build,no-dev,no-proc-macro \
	--prefix none --format '{l}: {p}' \
	| sed -e "s: ($(pwd)[^)]*)::g" -e 's: / :/:g' -e 's:/: OR :g' \
	| sort -u > ../../LICENSES.dependencies
popd

%files
%doc bindings/python/README.md
%license tokenizers/LICENSE LICENSES.dependencies
%{python_sitearch}/tokenizers
%{python_sitearch}/tokenizers-%{version}.dist-info
