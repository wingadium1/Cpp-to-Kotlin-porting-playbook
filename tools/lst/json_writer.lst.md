# LST Summary: src/lib_json/json_writer.cpp

- Version: `0.1`
- Source length: `36026` bytes
- Source hash (sha256): `ffb0cac91aea2ce089d676626fafacad396cef9df2518b47938b0e49e105de9b`
- Node counts: include=13, macro=5, namespace=1, other=20

## Tree

- other · 244 bytes (L1-5 B0-244)
- macro #if !defined(JSON_IS_AMALGAMATION) (L5-6 B244-279)

```
#if !defined(JSON_IS_AMALGAMATION)
```

- other · 1 bytes (L6-7 B279-280)
- include #include "json_tool.h" (L7-7 B280-302)

```
#include "json_tool.h"
```

- other · 1 bytes (L7-8 B302-303)
- include #include <json/writer.h> (L8-8 B303-327)

```
#include <json/writer.h>
```

- other · 1 bytes (L8-9 B327-328)
- macro #endif // if !defined(JSON_IS_AMALGAMATION) (L9-9 B328-371)

```
#endif // if !defined(JSON_IS_AMALGAMATION)
```

- other · 1 bytes (L9-10 B371-372)
- include #include <algorithm> (L10-10 B372-392)

```
#include <algorithm>
```

- other · 1 bytes (L10-11 B392-393)
- include #include <cassert> (L11-11 B393-411)

```
#include <cassert>
```

- other · 1 bytes (L11-12 B411-412)
- include #include <cctype> (L12-12 B412-429)

```
#include <cctype>
```

- other · 1 bytes (L12-13 B429-430)
- include #include <cmath> (L13-13 B430-446)

```
#include <cmath>
```

- other · 1 bytes (L13-14 B446-447)
- include #include <cstdio> (L14-14 B447-464)

```
#include <cstdio>
```

- other · 1 bytes (L14-15 B464-465)
- include #include <cstring> (L15-15 B465-483)

```
#include <cstring>
```

- other · 1 bytes (L15-16 B483-484)
- include #include <iomanip> (L16-16 B484-502)

```
#include <iomanip>
```

- other · 1 bytes (L16-17 B502-503)
- include #include <memory> (L17-17 B503-520)

```
#include <memory>
```

- other · 1 bytes (L17-18 B520-521)
- include #include <set> (L18-18 B521-535)

```
#include <set>
```

- other · 1 bytes (L18-19 B535-536)
- include #include <sstream> (L19-19 B536-554)

```
#include <sstream>
```

- other · 1 bytes (L19-20 B554-555)
- include #include <utility> (L20-20 B555-573)

```
#include <utility>
```

- other · 1 bytes (L20-21 B573-574)
- macro #if defined(_MSC_VER) (L21-22 B574-596)

```
#if defined(_MSC_VER)
```

- other · 51 bytes (L22-24 B596-647)
- macro #pragma warning(disable : 4996) (L24-24 B647-678)

```
#pragma warning(disable : 4996)
```

- other · 1 bytes (L24-25 B678-679)
- macro #endif (L25-25 B679-685)

```
#endif
```

- other · 1 bytes (L25-26 B685-686)
- namespace Json (L26-1201 B686-36007)

```
namespace Json
```

  - using using StreamWriterPtr = std::unique_ptr<StreamWriter>; (L28-29 B704-759)
  
```
using StreamWriterPtr = std::unique_ptr<StreamWriter>;
```

  - function valueToString (L30-45 B760-1207)
  
```
String valueToString(LargestInt value)
```

  - function valueToString (L46-53 B1208-1403)
  
```
String valueToString(LargestUInt value)
```

  - macro #if defined(JSON_HAS_INT64) (L54-55 B1404-1432)
  
```
#if defined(JSON_HAS_INT64)
```

  - function valueToString (L56-57 B1433-1510)
  
```
String valueToString(Int value)
```

  - function valueToString (L58-59 B1511-1590)
  
```
String valueToString(UInt value)
```

  - macro #endif // # if defined(JSON_HAS_INT64) (L60-61 B1591-1630)
  
```
#endif // # if defined(JSON_HAS_INT64)
```

  - function valueToString (L64-108 B1644-3157)
  
```
String valueToString(double value, bool useSpecialFloats,
                     unsigned int precision, PrecisionType precisionType)
```

  - function valueToString (L110-114 B3173-3350)
  
```
String valueToString(double value, unsigned int precision,
                     PrecisionType precisionType)
```

  - function valueToString (L115-116 B3351-3421)
  
```
String valueToString(bool value)
```

  - function doesAnyCharRequireEscaping (L117-124 B3422-3627)
  
```
static bool doesAnyCharRequireEscaping(char const* s, size_t n)
```

  - function std::any_of (L120-123 B3508-3623)
  
```
return std::any_of(s, s + n, [](unsigned char c)
```

  - function utf8ToCodepoint (L125-175 B3628-5322)
  
```
static unsigned int utf8ToCodepoint(const char*& s, const char* e)
```

  - function toHex16Bit (L193-203 B6317-6603)
  
```
static String toHex16Bit(unsigned int x)
```

  - function appendRaw (L204-207 B6604-6694)
  
```
static void appendRaw(String& result, unsigned ch)
```

  - function appendHex (L208-211 B6695-6797)
  
```
static void appendHex(String& result, unsigned ch)
```

  - function valueToQuotedStringN (L212-288 B6798-9197)
  
```
static String valueToQuotedStringN(const char* value, size_t length,
                                   bool emitUTF8 = false)
```

  - function valueToQuotedString (L289-292 B9198-9301)
  
```
String valueToQuotedString(const char* value)
```

  - function valueToQuotedString (L293-296 B9302-9413)
  
```
String valueToQuotedString(const char* value, size_t length)
```

  - function FastWriter::enableYAMLCompatibility (L308-309 B9663-9744)
  
```
void FastWriter::enableYAMLCompatibility()
```

  - function FastWriter::dropNullPlaceholders (L310-311 B9745-9819)
  
```
void FastWriter::dropNullPlaceholders()
```

  - function FastWriter::omitEndingLineFeed (L312-313 B9820-9890)
  
```
void FastWriter::omitEndingLineFeed()
```

  - function FastWriter::write (L314-321 B9891-10051)
  
```
String FastWriter::write(const Value& root)
```

  - function FastWriter::writeValue (L322-374 B10052-11509)
  
```
void FastWriter::writeValue(const Value& value)
```

  - function StyledWriter::write (L380-390 B11644-11903)
  
```
String StyledWriter::write(const Value& root)
```

  - function StyledWriter::writeValue (L391-450 B11904-13459)
  
```
void StyledWriter::writeValue(const Value& value)
```

  - function StyledWriter::writeArrayValue (L451-493 B13460-14619)
  
```
void StyledWriter::writeArrayValue(const Value& value)
```

  - function StyledWriter::isMultilineArray (L494-520 B14620-15585)
  
```
bool StyledWriter::isMultilineArray(const Value& value)
```

  - function StyledWriter::pushValue (L521-527 B15586-15729)
  
```
void StyledWriter::pushValue(const String& value)
```

  - function StyledWriter::writeIndent (L528-538 B15730-16011)
  
```
void StyledWriter::writeIndent()
```

  - function StyledWriter::writeWithIndent (L539-543 B16012-16111)
  
```
void StyledWriter::writeWithIndent(const String& value)
```

  - function StyledWriter::indent (L544-545 B16112-16187)
  
```
void StyledWriter::indent()
```

  - function StyledWriter::unindent (L546-550 B16188-16329)
  
```
void StyledWriter::unindent()
```

  - function StyledWriter::writeCommentBeforeValue (L551-569 B16330-16853)
  
```
void StyledWriter::writeCommentBeforeValue(const Value& root)
```

  - function StyledWriter::writeCommentAfterValueOnSameLine (L570-580 B16854-17178)
  
```
void StyledWriter::writeCommentAfterValueOnSameLine(const Value& root)
```

  - function StyledWriter::hasCommentForValue (L581-586 B17179-17379)
  
```
bool StyledWriter::hasCommentForValue(const Value& value)
```

  - function StyledStreamWriter::write (L594-608 B17648-18039)
  
```
void StyledStreamWriter::write(OStream& out, const Value& root)
```

  - function StyledStreamWriter::writeValue (L609-668 B18040-19603)
  
```
void StyledStreamWriter::writeValue(const Value& value)
```

  - function StyledStreamWriter::writeArrayValue (L669-714 B19604-20861)
  
```
void StyledStreamWriter::writeArrayValue(const Value& value)
```

  - function StyledStreamWriter::isMultilineArray (L715-741 B20862-21833)
  
```
bool StyledStreamWriter::isMultilineArray(const Value& value)
```

  - function StyledStreamWriter::pushValue (L742-748 B21834-21984)
  
```
void StyledStreamWriter::pushValue(const String& value)
```

  - function StyledStreamWriter::writeIndent (L749-756 B21985-22287)
  
```
void StyledStreamWriter::writeIndent()
```

  - function StyledStreamWriter::writeWithIndent (L757-763 B22288-22435)
  
```
void StyledStreamWriter::writeWithIndent(const String& value)
```

  - function StyledStreamWriter::indent (L764-765 B22436-22505)
  
```
void StyledStreamWriter::indent()
```

  - function StyledStreamWriter::unindent (L766-770 B22506-22669)
  
```
void StyledStreamWriter::unindent()
```

  - function StyledStreamWriter::writeCommentBeforeValue (L771-788 B22670-23197)
  
```
void StyledStreamWriter::writeCommentBeforeValue(const Value& root)
```

  - function StyledStreamWriter::writeCommentAfterValueOnSameLine (L789-799 B23198-23525)
  
```
void StyledStreamWriter::writeCommentAfterValueOnSameLine(const Value& root)
```

  - function StyledStreamWriter::hasCommentForValue (L800-805 B23526-23732)
  
```
bool StyledStreamWriter::hasCommentForValue(const Value& value)
```

  - struct CommentStyle (L811-818 B23837-24067)
  
```
struct CommentStyle
```

  - struct BuiltStyledStreamWriter (L819-857 B24069-25373)
  
```
struct BuiltStyledStreamWriter : public StreamWriter
```

    - using using ChildValues = std::vector<String>; (L840-841 B24959-25002)
    
```
using ChildValues = std::vector<String>;
```

  - function BuiltStyledStreamWriter::write (L868-882 B26026-26404)
  
```
int BuiltStyledStreamWriter::write(Value const& root, OStream* sout)
```

  - function BuiltStyledStreamWriter::writeValue (L883-944 B26405-28102)
  
```
void BuiltStyledStreamWriter::writeValue(Value const& value)
```

  - function BuiltStyledStreamWriter::writeArrayValue (L945-994 B28103-29509)
  
```
void BuiltStyledStreamWriter::writeArrayValue(Value const& value)
```

  - function BuiltStyledStreamWriter::isMultilineArray (L995-1021 B29510-30486)
  
```
bool BuiltStyledStreamWriter::isMultilineArray(Value const& value)
```

  - function BuiltStyledStreamWriter::pushValue (L1022-1028 B30487-30638)
  
```
void BuiltStyledStreamWriter::pushValue(String const& value)
```

  - function BuiltStyledStreamWriter::writeIndent (L1029-1040 B30639-31020)
  
```
void BuiltStyledStreamWriter::writeIndent()
```

  - function BuiltStyledStreamWriter::writeWithIndent (L1041-1047 B31021-31169)
  
```
void BuiltStyledStreamWriter::writeWithIndent(String const& value)
```

  - function BuiltStyledStreamWriter::indent (L1048-1049 B31170-31244)
  
```
void BuiltStyledStreamWriter::indent()
```

  - function BuiltStyledStreamWriter::unindent (L1050-1054 B31245-31413)
  
```
void BuiltStyledStreamWriter::unindent()
```

  - function BuiltStyledStreamWriter::writeCommentBeforeValue (L1055-1074 B31414-31987)
  
```
void BuiltStyledStreamWriter::writeCommentBeforeValue(Value const& root)
```

  - function BuiltStyledStreamWriter::writeCommentAfterValueOnSameLine (L1075-1087 B31988-32340)
  
```
void BuiltStyledStreamWriter::writeCommentAfterValueOnSameLine(
    Value const& root)
```

  - function BuiltStyledStreamWriter::hasCommentForValue (L1090-1094 B32352-32562)
  
```
bool BuiltStyledStreamWriter::hasCommentForValue(const Value& value)
```

  - function StreamWriterBuilder::newStreamWriter (L1104-1145 B32859-34434)
  
```
StreamWriter* StreamWriterBuilder::newStreamWriter() const
```

  - function StreamWriterBuilder::validate (L1146-1168 B34435-35019)
  
```
bool StreamWriterBuilder::validate(Json::Value* invalid) const
```

  - function StreamWriterBuilder::setDefaults (L1174-1185 B35118-35586)
  
```
void StreamWriterBuilder::setDefaults(Json::Value* settings)
```

  - function writeString (L1186-1192 B35587-35810)
  
```
String writeString(StreamWriter::Factory const& factory, Value const& root)
```

- other · 19 bytes (L1201-1202 B36007-36026)
