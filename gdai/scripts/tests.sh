#!/bin/bash
# GDAI Test Runner Script
# Executes all tests with coverage reporting

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GDAI Test Suite Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-yes}"
VERBOSE="${3:-no}"

# Function to run tests
run_tests() {
    local test_path="$1"
    local test_name="$2"
    local cov_source="$3"

    echo -e "${YELLOW}Running ${test_name}...${NC}"

    if [ "$COVERAGE" = "yes" ]; then
        if [ "$VERBOSE" = "yes" ]; then
            uv run pytest "${test_path}" \
                --cov="${cov_source}" \
                --cov-report=term-missing \
                --cov-report=html \
                -v
        else
            uv run pytest "${test_path}" \
                --cov="${cov_source}" \
                --cov-report=term-missing \
                --cov-report=html \
                -q
        fi
    else
        if [ "$VERBOSE" = "yes" ]; then
            uv run pytest "${test_path}" -v
        else
            uv run pytest "${test_path}" -q
        fi
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ ${test_name} passed!${NC}"
    else
        echo -e "${RED}✗ ${test_name} failed!${NC}"
        return $exit_code
    fi

    echo ""
}

# Change to project root
cd "${PROJECT_ROOT}"

# Run tests based on type
case "$TEST_TYPE" in
    unit)
        echo -e "${BLUE}Running Unit Tests Only${NC}"
        echo ""
        run_tests "tests/unit/" "Unit Tests" "gdai"
        ;;

    integration)
        echo -e "${BLUE}Running Integration Tests Only${NC}"
        echo ""
        run_tests "tests/integration/" "Integration Tests" "gdai"
        ;;

    api)
        echo -e "${BLUE}Running API Tests Only${NC}"
        echo ""
        run_tests "tests/api/" "API Tests" "gdai"
        ;;

    commons)
        echo -e "${BLUE}Running Commons Module Tests${NC}"
        echo ""
        run_tests "tests/unit/test_commons.py" "Commons Tests" "gdai.commons"
        ;;

    repositories)
        echo -e "${BLUE}Running Repository Tests${NC}"
        echo ""
        run_tests "tests/integration/test_repositories.py" "Repository Tests" "gdai.repositories"
        ;;

    llms)
        echo -e "${BLUE}Running LLM Tests${NC}"
        echo ""
        run_tests "tests/integration/test_llms.py" "LLM Tests" "gdai.llms"
        ;;

    embeddings)
        echo -e "${BLUE}Running Embedding Tests${NC}"
        echo ""
        run_tests "tests/integration/test_embeddings.py" "Embedding Tests" "gdai.embeddings"
        ;;

    all)
        echo -e "${BLUE}Running All Tests${NC}"
        echo ""

        # Run unit tests
        run_tests "tests/unit/" "Unit Tests" "gdai" || exit 1

        # Run integration tests
        run_tests "tests/integration/" "Integration Tests" "gdai" || exit 1

        # Run API tests
        run_tests "tests/api/" "API Tests" "gdai" || exit 1

        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  All Test Suites Passed! ✓${NC}"
        echo -e "${GREEN}========================================${NC}"
        ;;

    quick)
        echo -e "${BLUE}Running Quick Test Suite (no coverage)${NC}"
        echo ""
        COVERAGE="no"
        run_tests "tests/unit/" "Unit Tests" "gdai" || exit 1
        run_tests "tests/api/" "API Tests" "gdai" || exit 1
        ;;

    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [test_type] [coverage] [verbose]"
        echo ""
        echo "Test types:"
        echo "  all           - Run all tests (default)"
        echo "  unit          - Run only unit tests"
        echo "  integration   - Run only integration tests"
        echo "  api           - Run only API tests"
        echo "  commons       - Run commons module tests"
        echo "  repositories  - Run repository tests"
        echo "  llms          - Run LLM tests"
        echo "  embeddings    - Run embedding tests"
        echo "  quick         - Run quick test suite (unit + api, no coverage)"
        echo ""
        echo "Coverage (optional):"
        echo "  yes - Generate coverage report (default)"
        echo "  no  - Skip coverage"
        echo ""
        echo "Verbose (optional):"
        echo "  yes - Verbose output"
        echo "  no  - Quiet output (default)"
        echo ""
        echo "Examples:"
        echo "  $0                        # Run all tests with coverage"
        echo "  $0 unit                   # Run unit tests with coverage"
        echo "  $0 integration no         # Run integration tests without coverage"
        echo "  $0 all yes yes            # Run all tests with coverage, verbose"
        echo "  $0 quick                  # Quick test (unit + api, no coverage)"
        exit 1
        ;;
esac

# Show coverage report location if generated
if [ "$COVERAGE" = "yes" ]; then
    echo ""
    echo -e "${BLUE}Coverage report generated:${NC}"
    echo -e "  HTML: ${GREEN}file://${PROJECT_ROOT}/htmlcov/index.html${NC}"
    echo -e "  Open with: ${YELLOW}open htmlcov/index.html${NC}"
fi

echo ""
echo -e "${GREEN}Done! ✓${NC}"
