# Test Execution Commands - Quick Reference

## 🚀 Automated Test Execution (Recommended)

### **Option 1: Using Shell Script (Linux/Mac)**

```bash
# Make script executable (first time only)
chmod +x run_tests.sh

# Run the complete test suite
./run_tests.sh
```

The script will automatically:
- Clean previous results
- Run all tests
- Generate Allure report
- Start HTTP server
- Open report in browser

### **Option 2: Using Batch File (Windows)**

```cmd
run_tests.bat
```

---

## 📝 Manual Test Execution

### **Complete Test Suite Execution (One-Liner)**

```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v && \
cp categories.json allure-results/ && \
allure generate allure-results --clean -o allure-report && \
cd allure-report && python3 -m http.server 8000
```

Then open: **http://localhost:8000**

---

## 🎯 Step-by-Step Manual Execution

### **Step 1: Run Tests**
```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v
```

### **Step 2: Copy Categories**
```bash
cp categories.json allure-results/
```

### **Step 3: Generate Allure Report**
```bash
allure generate allure-results --clean -o allure-report
```

### **Step 4: View Report**

**Method A - Using Allure Server:**
```bash
allure open allure-report
```

**Method B - Using Python HTTP Server:**
```bash
cd allure-report
python3 -m http.server 8000
```
Then open: http://localhost:8000

---

## 🔍 Specific Test Execution

### **Run Specific Test File**

```bash
# Boundary Hierarchy tests
pytest tests/test_boundary_hierarchy_service.py --alluredir=allure-results -v

# Boundary Management tests
pytest tests/test_boundary_management_service.py --alluredir=allure-results -v

# Boundary Relationships tests
pytest tests/test_boundary_relationships_service.py --alluredir=allure-results -v

# Filestore tests
pytest tests/test_filestore_service.py --alluredir=allure-results -v

# Localization tests
pytest tests/test_localization_service.py --alluredir=allure-results -v
```

### **Run Single Test Function**

```bash
pytest tests/test_boundary_management_service.py::test_generate_boundary_data --alluredir=allure-results -v
```

### **Run Tests by Feature (if markers added)**

```bash
pytest tests/ -m "boundary_management" --alluredir=allure-results -v
```

---

## 🛠️ Test Execution Options

### **Verbose Output**
```bash
pytest tests/ --alluredir=allure-results -v
```

### **Extra Verbose (More Details)**
```bash
pytest tests/ --alluredir=allure-results -vv
```

### **Show Print Statements**
```bash
pytest tests/ --alluredir=allure-results -v -s
```

### **Stop on First Failure**
```bash
pytest tests/ --alluredir=allure-results -v -x
```

### **Run Tests in Parallel (requires pytest-xdist)**
```bash
pytest tests/ --alluredir=allure-results -v -n 4
```

### **Quiet Mode (Minimal Output)**
```bash
pytest tests/ --alluredir=allure-results -q
```

### **Show Test Duration**
```bash
pytest tests/ --alluredir=allure-results -v --durations=10
```

---

## 📊 Report Generation Commands

### **Generate Report (Clean)**
```bash
allure generate allure-results --clean -o allure-report
```

### **Generate Report (Without Clean)**
```bash
allure generate allure-results -o allure-report
```

### **Serve Report with Allure**
```bash
allure serve allure-results
```
*This generates and serves the report in one command*

### **Open Existing Report**
```bash
allure open allure-report
```

---

## 🔧 Utility Commands

### **View Generated Test Data**

```bash
# View all generated IDs
cat output/ids.txt

# Get latest hierarchy type
grep "Hierarchy Type:" output/ids.txt | tail -1

# Get all Generate Resource IDs
grep "Generate Resource ID:" output/ids.txt

# Get all FileStore IDs
grep "FileStore ID:" output/ids.txt
```

### **Clean Up Generated Files**

```bash
# Remove Allure results
rm -rf allure-results/

# Remove Allure report
rm -rf allure-report/

# Clean output files
rm output/ids.txt

# Clean all generated files
rm -rf allure-results/ allure-report/ output/ids.txt
```

### **Stop HTTP Server**

```bash
# Kill server on port 8000
pkill -f "python3 -m http.server 8000"

# Alternative method
lsof -ti:8000 | xargs kill -9
```

---

## 🔄 Continuous Integration Commands

### **CI Pipeline Command (No Browser)**
```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v && \
cp categories.json allure-results/ && \
allure generate allure-results --clean -o allure-report
```

### **CI with HTML Report Archive**
```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v && \
cp categories.json allure-results/ && \
allure generate allure-results --clean -o allure-report && \
tar -czf allure-report.tar.gz allure-report/
```

---

## 🐛 Debug Commands

### **Run with Debug Logs**
```bash
pytest tests/ --alluredir=allure-results -v -s --log-cli-level=DEBUG
```

### **Run with Coverage**
```bash
pytest tests/ --alluredir=allure-results -v --cov=. --cov-report=html
```

### **List All Tests**
```bash
pytest --collect-only tests/
```

### **Run Tests with PDB (Python Debugger)**
```bash
pytest tests/ --pdb
```

---

## 💡 Pro Tips

### **Alias for Quick Execution**

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Quick test runner
alias run-tests='cd /path/to/API_Automation && ./run_tests.sh'

# Quick test with report
alias test-report='pytest tests/ --alluredir=allure-results --clean-alluredir -v && cp categories.json allure-results/ && allure generate allure-results --clean -o allure-report && allure open allure-report'
```

### **Watch Mode (Re-run on File Change)**

Install pytest-watch:
```bash
pip install pytest-watch
```

Run:
```bash
ptw tests/ -- --alluredir=allure-results -v
```

---

## 📋 Command Cheat Sheet

| Task | Command |
|------|---------|
| **Run all tests (automated)** | `./run_tests.sh` |
| **Run all tests (manual)** | `pytest tests/ --alluredir=allure-results -v` |
| **Generate report** | `allure generate allure-results --clean -o allure-report` |
| **Open report** | `allure open allure-report` |
| **Serve report** | `cd allure-report && python3 -m http.server 8000` |
| **View latest hierarchy** | `grep "Hierarchy Type:" output/ids.txt \| tail -1` |
| **Clean results** | `rm -rf allure-results/ allure-report/` |
| **Stop server** | `pkill -f "python3 -m http.server 8000"` |

---

## 🎬 Quick Start Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run tests with automated script
./run_tests.sh

# Done! Report opens automatically in browser
```

---

**For more detailed information, see [README.md](README.md)**
