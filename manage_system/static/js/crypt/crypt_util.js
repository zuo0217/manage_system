var crypt_util = {
	public_key : ""

	doEncrypt : function(_data) {
		var encrypt = new JSEncrypt();
		encrypt.setPublicKey(crypt_util.public_key);
		var result = encrypt.encrypt(_data);
		return result;
	},
};
