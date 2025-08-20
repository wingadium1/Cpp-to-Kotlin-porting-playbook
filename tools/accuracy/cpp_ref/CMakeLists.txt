cmake_minimum_required(VERSION 3.15)
project(cpp_ref)
set(CMAKE_CXX_STANDARD 17)
add_executable(cpp_ref main.cpp)
# Assume we're building inside repo; include JsonCpp headers and source
include_directories(${CMAKE_SOURCE_DIR}/../../include)
add_subdirectory(${CMAKE_SOURCE_DIR}/../../src ${CMAKE_BINARY_DIR}/jsoncpp-src)
target_link_libraries(cpp_ref jsoncpp_object)
