/** Canonical UTC timestamps only; rejects impossible calendar dates and HTML. */
export function isIsoTimestamp(value){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value))return false;
 const time=Date.parse(value);return Number.isFinite(time)&&new Date(time).toISOString()===value;
}
