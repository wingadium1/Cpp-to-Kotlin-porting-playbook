
#include <json/json.h>
#include <iostream>
#include <sstream>
#include <string>

int main(int argc, char** argv) {
  // read stdin as a raw JSON string (not parsed JSON)
  std::string input((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
  // argv[1]: indentation; argv[2]: precision; argv[3]: precisionType; argv[4]: emitUTF8; argv[5]: useSpecialFloats
  std::string indentation = argc > 1 ? argv[1] : "\t";
  unsigned precision = argc > 2 ? (unsigned)std::stoi(argv[2]) : 17;
  std::string precisionType = argc > 3 ? argv[3] : "significant";
  bool emitUTF8 = argc > 4 ? std::string(argv[4]) == "1" : false;
  bool useSpecialFloats = argc > 5 ? std::string(argv[5]) == "1" : false;
  bool enableYAMLCompatibility = argc > 6 ? std::string(argv[6]) == "1" : false;
  bool dropNullPlaceholders = argc > 7 ? std::string(argv[7]) == "1" : false;

  Json::CharReaderBuilder rb;
  std::string errs;
  Json::Value root;
  std::istringstream iss(input);
  if (!Json::parseFromStream(rb, iss, &root, &errs)) {
    std::cerr << "parse error: " << errs << std::endl;
    return 2;
  }

  Json::StreamWriterBuilder b;
  b["indentation"] = indentation;
  b["precision"] = precision;
  b["precisionType"] = precisionType;
  b["emitUTF8"] = emitUTF8;
  b["useSpecialFloats"] = useSpecialFloats;
  b["enableYAMLCompatibility"] = enableYAMLCompatibility;
  b["dropNullPlaceholders"] = dropNullPlaceholders;

  std::unique_ptr<Json::StreamWriter> w(b.newStreamWriter());
  std::ostringstream oss;
  w->write(root, &oss);
  std::cout << oss.str();
  return 0;
}
