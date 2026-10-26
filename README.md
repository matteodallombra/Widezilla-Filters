# Widezilla filter data

This repository distributes declarative WebKit content-blocking **data only**. It contains no Widezilla application source, binaries, executable scripts or user data.

EasyList and EasyPrivacy by the EasyList authors: https://easylist.to/ . Original sources: https://easylist.to/easylist/easylist.txt and https://easylist.to/easylist/easyprivacy.txt . The lists and their adapted native JSON are distributed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); see LICENSE.txt. You may use, adapt and redistribute this filter data under that licence.

`latest.json` contains a versioned snapshot and its SHA-256. `provenance.json` records generation time, source hashes, conversion settings and unsupported-rule counts. Native WebKit limitations mean some source rules cannot be represented. Advanced JavaScript filtering is disabled.

Data is generated with the unmodified standalone [SafariConverterLib 4.3.1](https://github.com/AdguardTeam/SafariConverterLib/tree/v4.3.1) (GPLv3), using Safari 26 format. That tool is not distributed here or linked into Widezilla. Its licence applies to the tool; the input lists' CC BY-SA licence applies to these converted data files.

A separate private publishing workflow refreshes this data daily. Failed publication leaves the last working snapshot available. This repository's data licence does not license Widezilla's separate proprietary application source.
