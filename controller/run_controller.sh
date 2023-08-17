PYTHON_LIB_DIR=$(python3 -c "from distutils import sysconfig; print(sysconfig.get_python_lib(prefix='', standard_lib=True, plat_specific=True))")

export PYTHONPATH=$SDE_INSTALL/$PYTHON_LIB_DIR/site-packages/tofino/bfrt_grpc:$PYTHONPATH
export PYTHONPATH=$SDE_INSTALL/$PYTHON_LIB_DIR/site-packages:$PYTHONPATH
export PYTHONPATH=$SDE_INSTALL/$PYTHON_LIB_DIR/site-packages/tofino:$PYTHONPATH
export PYTHONPATH=$SDE_INSTALL/$PYTHON_LIB_DIR/site-packages/${ARCH}pd:$PYTHONPATH
export PYTHONPATH=$SDE_INSTALL/$PYTHON_LIB_DIR/site-packages/p4testutils:$PYTHONPATH
export PYTHONPATH=$HOME/hd/P4/p4-projects/copy_switchtree/ML:$PYTHONPATH

python3 $1
