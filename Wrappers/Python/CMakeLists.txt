option (BUILD_PYTHON_WRAPPER "Build Python Wrapper" ON)

if (BUILD_PYTHON_WRAPPER)
  find_package(PythonInterp REQUIRED)
  
  #set(PYTHON_DEST_DIR "" CACHE PATH "Directory of the Python wrappers")
  if (PYTHON_DEST_DIR)
    set(PYTHON_DEST "${PYTHON_DEST_DIR}")
  else() 
    message(STATUS "python version ${PYTHON_DEST}")
    execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/CMake/sp_dir.py 
      OUTPUT_VARIABLE SP_DIR)
    # remove trailing newline  
    string(REGEX REPLACE "\n$" "" PYTHON_DEST ${SP_DIR})
    # append default site-packages
    set(PYTHON_DEST "${PYTHON_DEST}/site-packages")
  endif()

  file(TO_CMAKE_PATH ${PYTHON_DEST} TMP)
  set (PYTHON_DEST ${TMP})
  unset (TMP)

  message(STATUS "Python wrappers will be installed in " ${PYTHON_DEST})

  message("CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS}")

  set(CMAKE_BUILD_TYPE "Release")
  
  find_package(PythonLibs)
  if (PYTHONINTERP_FOUND)
    message(STATUS "Found PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE}")
    message(STATUS "Python version ${PYTHON_VERSION_STRING}")
  endif()
  if (PYTHONLIBS_FOUND)
    message(STATUS "Found PYTHON_INCLUDE_DIRS=${PYTHON_INCLUDE_DIRS}")
    message(STATUS "Found PYTHON_LIBRARIES=${PYTHON_LIBRARIES}")
  endif()

  if (PYTHONINTERP_FOUND)
      message("Python found " ${PYTHON_EXECUTABLE})
      set(SETUP_PY    "${CMAKE_CURRENT_SOURCE_DIR}/setup.py")
      set(OUTPUT      "${CMAKE_CURRENT_BINARY_DIR}/timestamp")
      file(GLOB_RECURSE DEPS ${CMAKE_CURRENT_SOURCE_DIR}/cil/*.py )
      
      # adds the CIL_VERSION to the setup.py
      if (EXISTS ${SETUP_PY})
        file(REMOVE ${SETUP_PY})
      endif()
      configure_file(${CMAKE_CURRENT_SOURCE_DIR}/CMake/setup.py.in ${SETUP_PY})
      # adds the version.py file to the source code with correct version string.
      if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/cil/version.py)
        file(REMOVE ${CMAKE_CURRENT_SOURCE_DIR}/cil/version.py)
      endif()
      configure_file(${CMAKE_CURRENT_SOURCE_DIR}/CMake/version.py.in ${CMAKE_CURRENT_SOURCE_DIR}/cil/version.py)



      # add to add_custom_command DEPENDS the list of python files of the project.
      # as a hack I remove ${OUTPUT}. This should trigger the new build.
      file( REMOVE ${OUTPUT} )
      
      
      if (CONDA_BUILD)
        add_custom_target(pythonsetup ALL
                        COMMAND ${CMAKE_COMMAND} -E env ${PYTHON_EXECUTABLE} ${SETUP_PY} -vv install
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        COMMAND ${CMAKE_COMMAND} -E touch ${OUTPUT}
                        DEPENDS cilacc)

      else()
        if (WIN32)
          add_custom_target(pythonsetup ALL
                        COMMAND ${CMAKE_COMMAND} -E env PREFIX=${CMAKE_SOURCE_DIR}/src/
                                                 LIBRARY_INC=${CMAKE_SOURCE_DIR}/src/include
                                                 LIBRARY_LIB=${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}
                                                 ${PYTHON_EXECUTABLE} ${SETUP_PY} build_py
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        COMMAND ${CMAKE_COMMAND} -E touch ${OUTPUT}
                        DEPENDS cilacc)

          install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/build/lib/cil
                DESTINATION ${PYTHON_DEST} )
                
        else()
          add_custom_target(pythonsetup ALL  
                        COMMAND ${CMAKE_COMMAND} -E env PREFIX=${CMAKE_SOURCE_DIR}/src/
                                                 LIBRARY_INC=${CMAKE_SOURCE_DIR}/src/include
                                                 LIBRARY_LIB=${CMAKE_BINARY_DIR}/
                                                 ${PYTHON_EXECUTABLE} ${SETUP_PY} build_py --verbose --build-lib=${CMAKE_CURRENT_BINARY_DIR}/build/lib
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        
                        COMMAND ${CMAKE_COMMAND} -E touch ${OUTPUT}
                        DEPENDS cilacc 
                        )
        endif()
        #set (PYTHON_DEST ${CMAKE_INSTALL_PREFIX}/python/)

        if (NOT WIN32)
          install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/build/lib/cil
                DESTINATION ${PYTHON_DEST} )

        endif()
        install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/data/ DESTINATION ${CMAKE_INSTALL_PREFIX}/share/cil)
        #file(TOUCH ${PYTHON_DEST}/edo/__init__.py)
        
      endif()
      
      
      #add_custom_target(PythonWrapper ALL DEPENDS ${OUTPUT})
      add_custom_target(PythonWrapper ALL DEPENDS pythonsetup)
       
  endif()

endif()
