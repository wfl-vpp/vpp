#!/bin/bash
EASYROOT="{{ easyrsa_root }}"
EASYSRC="{{ easyrsa_src }}"
EASYPKI="{{ easyrsa_pki }}"
OVPNPKI="{{ ovpn_pki }}"
EASYSERV_K="{{ easyrsa_srv_k }}"


cd ${EASYSRC}
echo "INIT:"
./easyrsa --pki-dir=${EASYPKI} --batch init-pki
if [ $? -ne 0 ]
then
	exit 1
fi
cp ${EASYROOT}/vars ${EASYPKI}
if [ $? -ne 0 ]
then
	exit 2
fi
echo "BUILD_CA:"
./easyrsa --pki-dir=${EASYPKI} --batch build-ca nopass
if [ $? -ne 0 ]
then
	exit 3
fi
echo "GEN-CRL:"
./easyrsa --pki-dir=${EASYPKI} --batch gen-crl
if [ $? -ne 0 ]
then
	exit
fi
./easyrsa --pki-dir=${EASYPKI} --batch --passout=file:${EASYSERV_K} build-server-full server
if [ $? -ne 0 ]
then
	exit 4
fi

cp -a ${EASYPKI}/ca.crt ${OVPNPKI}
cp -a ${EASYPKI}/issued/server.crt ${OVPNPKI}/server.crt
cp -a ${EASYPKI}/private/server.key ${OVPNPKI}/server.key

cd ${OVPNPKI}
echo "DHPARAM:"
openssl dhparam -out dh2048.pem 2048
if [ $? -ne 0 ]
then
	exit 5
fi

exit 0
