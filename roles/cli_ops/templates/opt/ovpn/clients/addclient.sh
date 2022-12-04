#!/bin/bash
EASYROOT="{{ easyrsa_root }}"
EASYSRC="{{ easyrsa_src }}"
EASYPKI="{{ easyrsa_pki }}"
OVPNPKI="{{ ovpn_pki }}"
EASYSERV_K="{{ easyrsa_srv_k }}"
CLIROOT="{{ client_root }}"
CLILIST="${CLIROOT}/clientlist"


# Create random filename for the client
while [ true ]
do
	RND1=$(openssl rand -hex 3)
	CLICONF="${CLIROOT}/cli_${RND1}"
	if [ ! -f ${CLICONF} ]
	then
		break
	fi
done

# Create random passowrd for the client
export CLIPASS=$(tr -dc 'A-Za-z0-9!#$%&()*+,-./:;<=>?@[\]^_{|}~' </dev/urandom | head -c 13)

# Generate cert files for client
cd ${EASYSRC}
./easyrsa --pki-dir=${EASYPKI} --batch --passin=file:${EASYSERV_K} --passout=env:CLIPASS build-client-full cli_${RND1} &>/dev/null
if [ $? -ne 0 ]
then
	unset CLIPASS
	exit 1
fi
echo ${CLIPASS}
unset CLIPASS

# Build client config

cat ${CLIROOT}/template.ovpn >> ${CLICONF}
echo "" >> ${CLICONF}

# Add ca cert to the client config file
echo "<ca>" >> ${CLICONF}
openssl x509 -in ${OVPNPKI}/ca.crt >> ${CLICONF}
if [ $? -ne 0 ]
then
	exit 1
fi
echo "</ca>" >> ${CLICONF}

# Add client certificate to client config file
echo "<cert>" >> ${CLICONF}
openssl x509 -in ${EASYPKI}/issued/cli_${RND1}.crt >> ${CLICONF}
echo "</cert>" >> ${CLICONF}

# Add client key to client config file
echo "<key>" >> ${CLICONF}
cat ${EASYPKI}/private/cli_${RND1}.key >> ${CLICONF}
echo "</key>" >> ${CLICONF}

# For ansible to get the file path
echo ${CLICONF}

# Remove client key and cert files from the server
rm -f ${EASYPKI}/issued/cli_${RND1}.crt
rm -f ${EASYPKI}/private/cli_${RND1}.key

# Increase client counter by one
touch ${CLILIST}
echo ${RND1} >> ${CLILIST}

exit 0
