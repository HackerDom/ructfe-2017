export default function cookie(cookieName) {
  let result;
  if (!cookieName) {
    result = {};
  }
  const cookies = document.cookie.split("; ") || [];
  const rdecode = /(%[0-9A-Z]{2})+/g;

  for (let i = 0; i < cookies.length; ++i) {
    const parts = cookies[i].split("=");
    let value = parts.slice(1).join("=");
    if (value.charAt(0) === '"') {
      value = value.slice(1, -1);
    }
    const name = parts[0].replace(rdecode, decodeURIComponent);
    if (cookieName === name) {
      result = value;
      break;
    }
    if (!cookieName) {
      result[name] = value;
    }
  }

  return result;
}
