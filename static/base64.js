// https://github.com/discohook/site/blob/main/common/base64/base64Decode.ts
export function base64Decode(urlSafeBase64) {
    const base64 = urlSafeBase64.replace(/-/g, "+").replace(/_/g, "/")
    const encoded = atob(base64)
        .split("")
        .map((char) => char.charCodeAt(0).toString(16))
        .map((hex) => `%${hex.padStart(2, "0").slice(-2)}`)
        .join("")

    return decodeURIComponent(encoded)
}

// https://github.com/discohook/site/blob/main/common/base64/base64Encode.ts
export function base64Encode(utf8) {
    const encoded = encodeURIComponent(utf8)

    const escaped = encoded.replace(/%[\dA-F]{2}/g, hex => {
      return String.fromCharCode(Number.parseInt(hex.slice(1), 16))
    })

    return btoa(escaped)
}

// https://github.com/discohook/site/blob/main/common/base64/base64UrlEncode.ts
export function base64UrlEncode(utf8) {
    return base64Encode(utf8)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=/g, "")
}
