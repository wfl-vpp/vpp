#!/bin/bash
EASYROOT="{{ easyrsa_root }}"
EASYSRC="{{ easyrsa_src }}"
EASYPKI="{{ easyrsa_pki }}"
OVPNPKI="{{ ovpn_pki }}"
EASYSERV_K="{{ easyrsa_srv_k }}"
CLIROOT="{{ client_root }}"
CLILIST="${CLIROOT}/clientlist"
CLICONF_LIST=""
CLIPASS_LIST=""
DO_ENC="{{ easyrsa_encrypt_cli_key }}"
CLN=$1

	
add_the_client()
{
	# Create random filename for the client
	while [ true ]
	do
		RND1=$(openssl rand -hex 3)
		CLICONF="${CLIROOT}/cli_${RND1}.ovpn"
		if [ ! -f ${CLICONF} ]
		then
			break
		fi
	done
	
	# Create random passowrd for the client
	export CLIPASS=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 13)
	
	# Generate cert files for client
	cd ${EASYSRC}
	if [[ ${DO_ENC} ]]
	then
		./easyrsa --pki-dir=${EASYPKI} --batch --passin=file:${EASYSERV_K} --passout=env:CLIPASS build-client-full cli_${RND1} &>/dev/null
	else
		./easyrsa --pki-dir=${EASYPKI} --batch --passin=file:${EASYSERV_K} build-client-full cli_${RND1} &>/dev/null
	fi
	
	if [ $? -ne 0 ]
	then
		unset CLIPASS
		exit 1
	fi
	#echo ${CLIPASS}
	CLIPASS_LIST+=${CLIPASS},
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
	CLICONF_LIST+=${CLICONF},
	
	# Remove client key file from the server
	# rm -f ${EASYPKI}/issued/cli_${RND1}.crt
	rm -f ${EASYPKI}/private/cli_${RND1}.key
	
	# Increase client counter by one
	touch ${CLILIST}
	echo ${RND1} >> ${CLILIST}
	
}

counter=0
while [ ${counter} -lt ${CLN} ]
do
	add_the_client
	let counter=$counter+1
done

echo ${CLIPASS_LIST%?}
echo ${CLICONF_LIST%?}

exit 0
