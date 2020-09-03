cmake_minimum_required(VERSION 3.15)
project(Small_Project)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lwiicpp -lstdc++fs -lsfml-graphics -lsfml-audio -lsfml-window -lsfml-system -I/usr/include/python3.6m")

find_package(Python 3.6 REQUIRED EXACT COMPONENTS Interpreter Development)

include_directories(/usr/local/include/wiic/)

message("${Python_LIBRARIES}")

add_executable(Small_Project main.cpp)
target_include_directories(Small_Project PRIVATE ${PYTHON_INCLUDE_DIRS})
target_link_libraries(Small_Project wiicpp sfml-graphics sfml-audio sfml-window sfml-system ${Python_LIRARIES} -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6m -lpthread -ldl  -lutil -lm stdc++fs)
