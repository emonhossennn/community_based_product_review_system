#!/usr/bin/env python
"""
Simple Allure Test Runner for your existing project
Just adds Allure reporting to your current tests
"""
import os
import sys
import django
import subprocess
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()

def run_tests_with_allure():
    """Run your existing tests with Allure reporting"""
    print("🧪 Running tests with Allure reporting...")
    
    # Clean previous results
    if os.path.exists('allure-results'):
        import shutil
        shutil.rmtree('allure-results')
        print("✓ Cleaned previous results")
    
    # Run tests with Allure
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '--allure-dir=allure-results',
        '-v',
        '--tb=short'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Tests completed successfully!")
        return True
    else:
        print("⚠️ Some tests failed, but report will still be generated")
        return False

def generate_allure_report():
    """Generate Allure HTML report"""
    print("\n📊 Generating Allure report...")
    
    if not os.path.exists('allure-results'):
        print("❌ No test results found")
        return False
    
    try:
        # Generate HTML report
        cmd = ['allure', 'generate', 'allure-results', '--clean', '-o', 'allure-report']
        subprocess.run(cmd, check=True)
        
        report_path = Path('allure-report/index.html').absolute()
        print(f"✅ Report generated: {report_path}")
        print(f"🌐 Open in browser: file://{report_path}")
        
        # Try to serve the report
        try:
            print("\n🚀 Starting Allure server (Press Ctrl+C to stop)...")
            subprocess.run(['allure', 'serve', 'allure-results'])
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Allure CLI not found")
        print("Install with: npm install -g allure-commandline")
        print("Or download from: https://github.com/allure-framework/allure2/releases")
        return False

def create_simple_deployment():
    """Create simple files for sharing the report"""
    if not Path('allure-report').exists():
        print("❌ No allure-report folder found")
        return
    
    print("\n📦 Creating shareable package...")
    
    # Create simple index.html that redirects to allure report
    index_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Reports</title>
        <meta http-equiv="refresh" content="0; url=allure-report/index.html">
    </head>
    <body>
        <p>Redirecting to test reports... <a href="allure-report/index.html">Click here if not redirected</a></p>
    </body>
    </html>
    """
    
    with open('index.html', 'w') as f:
        f.write(index_content)
    
    print("✅ Created index.html for easy sharing")
    print("\n📋 To share your reports:")
    print("1. Upload the entire project folder to GitHub")
    print("2. Enable GitHub Pages from root folder")
    print("3. Your reports will be at: https://username.github.io/repo-name/")

def main():
    """Main function"""
    print("🧪 Adding Allure Reporting to Your Project")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Run tests with Allure
    run_tests_with_allure()
    
    # Generate report
    generate_allure_report()
    
    # Create deployment files
    create_simple_deployment()
    
    print("\n" + "=" * 50)
    print("✅ ALLURE REPORTING ADDED!")
    print("=" * 50)
    print("\nYour test reports are now ready to share!")
    print("The Allure reports show detailed test execution with:")
    print("• Test results and statistics")
    print("• Step-by-step test execution")
    print("• Test categorization and trends")
    print("• Professional test documentation")

if __name__ == "__main__":
    main()