#!/usr/bin/bash

PWD=$(pwd)
TESTDIR=$1
if [ ! -d "$TESTDIR" ] ; then
    echo "usage: $(basename $0) <testdir>" >&2
    exit 1
fi

(
# Go to script's directory
cd "$TESTDIR"

rc=0

# Check for python test files with invalid names
test_dirs=$(find . -type d -name 'test')
for test_dir in $test_dirs; do
    test_files=$(find $test_dir -name '*.py' | grep -v "__init__")
    for test_file in $test_files; do
        base_filename=$(basename $test_file)
        [[ ! "$base_filename" =~ ^test_.* ]] && echo "ERROR: Invalid test file name - $test_file" && rc=$(($rc+1))
    done
done

if [ "$TRAVIS_PYTHON_VERSION" != "" ]; then
    # Use always "coverage" executable for all Python versions in Travis
    py_cmd="coverage"
elif [ -f /usr/bin/coverage3 ]; then
    py_cmd="coverage3"
else
    py_cmd="coverage"
fi
# Find and run tests
$py_cmd run --source . -m unittest discover -v
rc=$(($rc+$?))

# Run pylint
find . -iname '*.py' | xargs pylint --rcfile=../pylintrc
rc=$(($rc+$?))

# Upload to Codecov.io after success
[ $rc -eq 0 ] && codecov

cd $PWD
exit $rc
)
