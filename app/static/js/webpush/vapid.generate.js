/**
 * Originally this code wasn't part of SnitchDNS and it directed users to visit https://web-push-codelab.glitch.me in
 * order to generate their keypair. However, just before SnitchDNS's release the VAPID key generation website wan't
 * working anymore, therefore the WayBack Machine was used to obtain the JS code of the key generation and adapt it to
 * work within this app.
 *
 * I couldn't find any GitHub repo or License information - if you're aware of any please let me know and I'll update
 * this accordingly.
 *
 * To be precise, this JS file was used:
 *  https://web.archive.org/web/20181127105930js_/http://web-push-codelab.glitch.me/scripts/application-server-key.js
 */
var VAPIDKeyGeneration = {
    generate: function(pubSelector, privSelector)
    {
        VAPIDKeyGeneration.generateKeys().then((newKeys) => {
            $(pubSelector).val(newKeys.public);
            $(privSelector).val(newKeys.private);
        })
    },

    generateKeys: function() {
        return crypto.subtle.generateKey(
            {name: 'ECDH', namedCurve: 'P-256'},
            true,
            ['deriveBits']
        ).then((keys) => {
            return VAPIDKeyGeneration.cryptoKeyToUrlBase64(keys.publicKey, keys.privateKey);
        });
    },

    cryptoKeyToUrlBase64: function(publicKey, privateKey) {
        const promises = [];
        promises.push(
            crypto.subtle.exportKey(
                'jwk',
                publicKey
            ).then((jwk) => {
                const x = VAPIDKeyGeneration.base64UrlToUint8Array(jwk.x);
                const y = VAPIDKeyGeneration.base64UrlToUint8Array(jwk.y);

                const publicKey = new Uint8Array(65);
                publicKey.set([0x04], 0);
                publicKey.set(x, 1);
                publicKey.set(y, 33);

                return publicKey;
            })
        );

        promises.push(
            crypto.subtle.exportKey(
                'jwk',
                privateKey
            ).then((jwk) => {
                return VAPIDKeyGeneration.base64UrlToUint8Array(jwk.d);
            })
        );

        return Promise.all(promises).then((exportedKeys) => {
            return {
                public: VAPIDKeyGeneration.uint8ArrayToBase64Url(exportedKeys[0]),
                private: VAPIDKeyGeneration.uint8ArrayToBase64Url(exportedKeys[1])
            }
        });
    },

    base64UrlToUint8Array: function(base64UrlData) {
        const padding = '='.repeat((4 - base64UrlData.length % 4) % 4);
        const base64 = (base64UrlData + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const buffer = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            buffer[i] = rawData.charCodeAt(i);
        }
        return buffer;
    },

    uint8ArrayToBase64Url: function(uint8Array, start, end) {
        start = start || 0;
        end = end || uint8Array.byteLength;

        const base64 = window.btoa(String.fromCharCode.apply(null, uint8Array.subarray(start, end)));
        return base64
            .replace(/\=/g, '')
            .replace(/\+/g, '-')
            .replace(/\//g, '_');
    }
};