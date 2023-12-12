type JSONObject = Record<string, any>;
// Checking if a variable is a JSON object
function isJSONObject(obj: any): obj is JSONObject {
  return typeof obj === 'object' && obj !== null && !Array.isArray(obj);
}

function snakeToCamel(str: string) {
  return str.replace(/_([a-z])/g, function (match, group) {
    return group.toUpperCase();
  });
}

export const searchObject = (obj: any, key: string) => {
  if(obj[key]){
    return obj[key]
  }
  else if(obj[snakeToCamel(key)]){
    return obj[snakeToCamel(key)]
  } else {
    let found: any = null
    for(const property in obj){
      if(isJSONObject(obj[property])){
        found = searchObject(obj[property], key)
      }else if (Array.isArray(obj[property])){
        for(const index in obj[property]){
          found = searchObject(obj[property][index], key);
          if(found){
            break;
          }
        }
      }
      if(found){
        break;
      }
    }
    return found;
  }
}