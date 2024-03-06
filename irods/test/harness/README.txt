SAMPLE RUNS

To build required images
------------------------

./build-docker.sh 


simple examples
---------------
./docker_container_driver.sh  tests/test_1.sh 
./docker_container_driver.sh  tests/test_2.sh 

Any script in a subdirectory of the repo (mounted at /prc within the container) can be
executed and will be able to find other scripts and source include files within the tree.
[See "experiment.sh" example below.]

Examples of options in driver script
------------------------------------

  1. To start container and run test script:
     C=$(  ./docker_container_driver.sh -c -L -u testuser  ../scripts/experiment.sh )

  2. To manually examine results afterward:
     docker exec -it $C bash 


