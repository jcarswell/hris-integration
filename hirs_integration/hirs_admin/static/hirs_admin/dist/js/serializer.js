function hashDiff(h1,h2) {
    var d={};
    for(var k in h2) {
        if(h1[k]!==h2[k]) d[k]=h2[k];
    }
    return d;
}
function convertSerializedArrayToHash(a) {
    var r={};
    for(var i=0;i<a.length;i++) { 
        r[a[i].name]=a[i].value;
    }
    return r;
}