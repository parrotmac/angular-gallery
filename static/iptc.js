/**
 * Created by isaac on 5/16/14.
 */
var bDebug = false;
var BinaryFile = function(strData, iDataOffset, iDataLength) {
var data = strData;
var dataOffset = iDataOffset || 0;
var dataLength = 0;
this.getRawData = function() {
        return data;
}
if (typeof strData == "string") {

        dataLength = iDataLength || data.length;

        this.getByteAt = function(iOffset) {
                return data.charCodeAt(iOffset + dataOffset);
        }
} else if (typeof strData == "unknown") {
        dataLength = iDataLength || IEBinary_getLength(data);

        this.getByteAt = function(iOffset) {
                return IEBinary_getByteAt(data, iOffset + dataOffset);
        }
}
this.getLength = function() {
        return dataLength;
}
this.getShortAt = function(iOffset, bBigEndian) {
        var iShort = bBigEndian ?
                (this.getByteAt(iOffset) << 8) + this.getByteAt(iOffset + 1)
                : (this.getByteAt(iOffset + 1) << 8) + this.getByteAt(iOffset)
        if (iShort < 0) {
            console.warn("iShort is < 0");
            iShort += 65536;
        }
        return iShort;
}
this.getStringAt = function(iOffset, iLength) {
        var aStr = [];
        for (var i=iOffset,j=0;i<iOffset+iLength;i++,j++) {
                aStr[j] = String.fromCharCode(this.getByteAt(i));
        }
        return aStr.join("");
}
}
var fieldMap = {
    25 : 'keywords'
};
function readIPTCKeywords(oFile, iStart, iLength) {
    var keywords = new Array();
    var data = {};
    var pictureKeywords = Array();
    if (oFile.getStringAt(iStart, 9) != "Photoshop") {
        if (bDebug) log("Not valid Photoshop data! " + oFile.getStringAt(iStart, 9));
        return false;
    }
    var fileLength = oFile.getLength();
    var length, offset, fieldStart, title, value;
    var FILE_SEPARATOR_CHAR = 28;
    var START_OF_TEXT_CHAR = 2;
    var JPEG_MARKER = 0xFF;
    for (var i = 0; i < iLength; i++) {
        fieldStart = iStart + i;
        if(oFile.getByteAt(fieldStart) == JPEG_MARKER) { break; }
        if(oFile.getByteAt(fieldStart) == START_OF_TEXT_CHAR && oFile.getByteAt(fieldStart + 1) in fieldMap) {
            length = 0;
            offset = 2;
            while(
                fieldStart + offset < fileLength &&
                oFile.getByteAt(fieldStart + offset) != FILE_SEPARATOR_CHAR &&
                oFile.getByteAt(fieldStart + offset + 1) != START_OF_TEXT_CHAR) { offset++; length++; }
            if(!length) { continue; }
            title = fieldMap[oFile.getByteAt(fieldStart + 1)];
            value = oFile.getStringAt(iStart + i + 2, length) || '';
            value = value.replace('\000','').trim();
            if(title == "keywords") {
                keywords.push(value);
            }
            data[title] += value;
            i+=length-1;
        }
    }
    return keywords;
}

function findIPTCKeywordsinJPEG(oFile) {
    var aMarkers = [];
    if (oFile.getByteAt(0) != 0xFF || oFile.getByteAt(1) != 0xD8) {
        return false; // not a valid jpeg
    }
    var iOffset = 2;
    var iLength = oFile.getLength();
    while (iOffset < iLength) {
        if (oFile.getByteAt(iOffset) != 0xFF) {
            if (bDebug) console.log("Not a valid marker at offset " + iOffset + ", found: " + oFile.getByteAt(iOffset));
            return false; // not a valid marker, something is wrong
        }
        var iMarker = oFile.getByteAt(iOffset+1);
        if (iMarker == 237) {
            if (bDebug) console.log("Found 0xFFED marker");
            return readIPTCKeywords(oFile, iOffset + 4, oFile.getShortAt(iOffset+2, true)-2);
        } else {
            iOffset += 2 + oFile.getShortAt(iOffset+2, true);
        }
    }
}