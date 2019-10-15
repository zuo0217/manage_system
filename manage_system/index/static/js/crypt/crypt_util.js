var crypt_util = {
	public_key : '-----BEGIN PUBLIC KEY-----\n'
			+ 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMqNExDMYadBXKNlC1SHfsW5pa\n'
			+ 'OYJmSL/fWmXEhvUZpeuif6saWQX6731hFeKa4houuAw5PxZGirmbFXdgukHWzJv7\n'
			+ 'AlwCB7Kv+9ww5809E1m8AsH9NYdeB9K9pRZ9Fiih5kjG3gV2/RCRkXKBhwhhiipu\n'
			+ 'WBMGNQgfpYNCGIzi6QIDAQAB\n' + '-----END PUBLIC KEY-----',

	doEncrypt : function(_data) {
		var encrypt = new JSEncrypt();
		encrypt.setPublicKey(crypt_util.public_key);
		var result = encrypt.encrypt(_data);
		return result;
	},
};
