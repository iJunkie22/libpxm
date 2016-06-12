# Pixelmator (.pxm) - Reverse Engineered


part | bytes | value | meaning
---- | ----- | :-----: | -----
0 | `50584D44 4D455411` | `PXMDMETA` | start of file
1 | `24090000` | *2340* | length of **P2 + P3**
2 | `62706C69 737430` | `bplist0` | start of binary plist
3 | \* | [...] | plist content
4 |`504B0304 14000000 00000000 0000136E 658300F0 070000F0 07000D00 0000646F 63756D65 6E742F69 6E666F` | `PK`[...]`document/info` | separates plist from sqlite?
5 | `53 514C6974 6520666F 726D6174 2033` | `SQLite format 3` | start of SQLite db
6 | \* | [...] | sqlite db content


Parts **1**, **3**, and **6** vary. The length of part **1** is always 4 bytes, since it is a 4-bit integer. The format is little endian.


## SQLite DataBase format

### document_info
name | value
----- | ----
`TEXT` | `BLOB`
`PTImageIOFormatDocumentLayersLinkingInfoKey` | [bplist]
`PTImageIOFormatDocumentViewingOptionsInfoKey_PTImageIOPlatformMacOS` | [bplist]
`PTImageIOFormatDocumentSelectedLayersInfoKey` | [bplist]
`PTImageIOFormatDocumentIDInfoKey` | [uuid string]
`PTImageIOFormatDocumentKeywordsInfoKey`| [bplist]
`PTImageIOFormatDocumentBitsPerComponentInfoKey` | 8[string?]
`PTImageIOFormatDocumentCustomDataInfoKey` | [bplist]
`PTImageIOFormatDocumentResolutionUnitsInfoKey` | 1[int?]
`PTImageIOFormatDocumentResolutionSizeInfoKey` | `{300, 300}`
`PTImageIOFormatDocumentSizeInfoKey` | `{249, 300}`
`PTImageIOFormatDocumentOriginalExifDictionaryInfoKey` | [bplist]
`PTImageIOFormatDocumentGuidesInfoKey` | [bplist]
`PTImageIOFormatDocumentFileVersionSupportInfoKey` | [bplist]
`PTImageIOFormatDocumentSaveDateInfoKey` | [float (epoch?)]
`PTImageIOFormatDocumentBitmapDataFormatInfoKey` | 266760[int?]
`PTImageIOFormatDocumentNumberOfComponentsInfoKey` | 4[int?]
`PTImageIOFormatDocumentColorsyncProfileInfoKey` | [binary data (ColorProfile?)]




### document_layer
layer_uuid | parent_uuid | index_at_parent | type
---- | ----- | ----- | ----
`TEXT` | `TEXT` | `INTEGER` | `TEXT`



### layer_info
layer_uuid | name | value
----- | ----- | -----
`TEXT` | `TEXT` | `BLOB`
