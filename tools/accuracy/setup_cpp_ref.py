#!/usr/bin/env python3
import os, subprocess, json, sys, shutil, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CPP_DIR = ROOT / 'tools' / 'accuracy' / 'cpp_ref'

MAIN = r'''
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
'''

CMAKELISTS = r'''cmake_minimum_required(VERSION 3.15)
project(cpp_ref)
set(CMAKE_CXX_STANDARD 17)
add_executable(cpp_ref main.cpp)
# Assume we're building inside repo; include JsonCpp headers and source
include_directories(${CMAKE_SOURCE_DIR}/../../include)
add_subdirectory(${CMAKE_SOURCE_DIR}/../../src ${CMAKE_BINARY_DIR}/jsoncpp-src)
target_link_libraries(cpp_ref jsoncpp_object)
'''

def has_cmd(cmd: str) -> bool:
  return shutil.which(cmd) is not None


def build_with_cmake(build: Path) -> Path:
  (CPP_DIR / 'CMakeLists.txt').write_text(CMAKELISTS)
  build.mkdir(exist_ok=True)
  subprocess.check_call(['cmake', '..'], cwd=str(build))
  subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=str(build))
  return build / 'cpp_ref'


def build_with_compiler(build: Path) -> Path:
  # Fallback: compile directly with clang++/g++ linking jsoncpp sources
  compiler = shutil.which('clang++') or shutil.which('g++')
  if not compiler:
    print('No C++ compiler (clang++/g++) found in PATH', file=sys.stderr)
    sys.exit(2)
  build.mkdir(exist_ok=True)
  main_cpp = build / 'main.cpp'
  main_cpp.write_text(MAIN)
  include_dir = ROOT / 'include'
  src_glob = str(ROOT / 'src' / 'lib_json' / '*.cpp')
  src_files = sorted(glob.glob(src_glob))
  if not src_files:
    print('No JsonCpp source files found under src/lib_json', file=sys.stderr)
    sys.exit(2)
  out = build / 'cpp_ref'
  cmd = [compiler, '-std=gnu++17', '-O2', f'-I{include_dir}', str(main_cpp)] + src_files + ['-o', str(out)]
  subprocess.check_call(cmd)
  return out


def main():
  CPP_DIR.mkdir(parents=True, exist_ok=True)
  (CPP_DIR / 'main.cpp').write_text(MAIN)
  build = CPP_DIR / 'build'
  try:
    if has_cmd('cmake'):
      exe = build_with_cmake(build)
    else:
      exe = build_with_compiler(build)
  except subprocess.CalledProcessError as e:
    # If cmake path failed, try compiler fallback once
    if 'exe' not in locals() and not has_cmd('cmake'):
      raise
    print('CMake build failed, attempting direct compile fallback...', file=sys.stderr)
    exe = build_with_compiler(build)
  print('Built C++ reference at', exe)

if __name__ == '__main__':
  main()
