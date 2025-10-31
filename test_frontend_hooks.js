#!/usr/bin/env node
/**
 * Frontend Hooks Testing Script
 * Tests all React hooks and API integrations
 */

const fs = require('fs');
const path = require('path');

class FrontendTester {
    constructor() {
        this.testResults = {
            passed: 0,
            failed: 0,
            errors: []
        };
        this.hooksDir = path.join(__dirname, 'src', 'hooks');
        this.apiDir = path.join(__dirname, 'src', 'lib', 'api');
    }

    logResult(testName, success, error = null) {
        if (success) {
            this.testResults.passed++;
            console.log(`✅ ${testName}`);
        } else {
            this.testResults.failed++;
            this.testResults.errors.push(`${testName}: ${error}`);
            console.log(`❌ ${testName}: ${error}`);
        }
    }

    testHookFile(hookFile) {
        const filePath = path.join(this.hooksDir, hookFile);
        
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            
            // Check for common hook patterns
            const hasUseState = content.includes('useState');
            const hasUseEffect = content.includes('useEffect');
            const hasUseCallback = content.includes('useCallback');
            const hasUseMemo = content.includes('useMemo');
            const hasReturn = content.includes('return');
            const hasExport = content.includes('export');
            
            // Check for API calls
            const hasApiCalls = content.includes('api.') || content.includes('API.');
            
            // Check for error handling
            const hasErrorHandling = content.includes('try') && content.includes('catch') || 
                                   content.includes('error') || content.includes('Error');
            
            // Check for TypeScript types
            const hasTypes = content.includes(': ') && content.includes('interface');
            
            const checks = [
                { name: 'Has export', condition: hasExport },
                { name: 'Has return', condition: hasReturn },
                { name: 'Has React hooks', condition: hasUseState || hasUseEffect || hasUseCallback || hasUseMemo },
                { name: 'Has API calls', condition: hasApiCalls },
                { name: 'Has error handling', condition: hasErrorHandling },
                { name: 'Has TypeScript types', condition: hasTypes }
            ];
            
            let allPassed = true;
            checks.forEach(check => {
                if (!check.condition) {
                    allPassed = false;
                    this.logResult(`${hookFile} - ${check.name}`, false, 'Missing required pattern');
                }
            });
            
            if (allPassed) {
                this.logResult(`${hookFile} structure`, true);
            }
            
        } catch (error) {
            this.logResult(`${hookFile} file read`, false, error.message);
        }
    }

    testApiFile(apiFile) {
        const filePath = path.join(this.apiDir, apiFile);
        
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            
            // Check for API patterns
            const hasClass = content.includes('class ');
            const hasMethods = content.includes('async ') || content.includes('function ');
            const hasHttpMethods = content.includes('GET') || content.includes('POST') || 
                                 content.includes('PUT') || content.includes('DELETE');
            const hasErrorHandling = content.includes('try') && content.includes('catch');
            const hasTypes = content.includes(': ') && content.includes('interface');
            
            const checks = [
                { name: 'Has class or functions', condition: hasClass || hasMethods },
                { name: 'Has HTTP methods', condition: hasHttpMethods },
                { name: 'Has error handling', condition: hasErrorHandling },
                { name: 'Has TypeScript types', condition: hasTypes }
            ];
            
            let allPassed = true;
            checks.forEach(check => {
                if (!check.condition) {
                    allPassed = false;
                    this.logResult(`${apiFile} - ${check.name}`, false, 'Missing required pattern');
                }
            });
            
            if (allPassed) {
                this.logResult(`${apiFile} structure`, true);
            }
            
        } catch (error) {
            this.logResult(`${apiFile} file read`, false, error.message);
        }
    }

    testAllHooks() {
        console.log('\n🎣 Testing React Hooks...');
        
        try {
            const hookFiles = fs.readdirSync(this.hooksDir, { recursive: true })
                .filter(file => file.endsWith('.ts') || file.endsWith('.tsx'))
                .filter(file => !file.includes('.test.') && !file.includes('.spec.'));
            
            hookFiles.forEach(hookFile => {
                this.testHookFile(hookFile);
            });
            
        } catch (error) {
            this.logResult('Hooks directory read', false, error.message);
        }
    }

    testAllApis() {
        console.log('\n🌐 Testing API Files...');
        
        try {
            const apiFiles = fs.readdirSync(this.apiDir, { recursive: true })
                .filter(file => file.endsWith('.ts') || file.endsWith('.tsx'))
                .filter(file => !file.includes('.test.') && !file.includes('.spec.'));
            
            apiFiles.forEach(apiFile => {
                this.testApiFile(apiFile);
            });
            
        } catch (error) {
            this.logResult('API directory read', false, error.message);
        }
    }

    testPackageJson() {
        console.log('\n📦 Testing Package Configuration...');
        
        try {
            const packagePath = path.join(__dirname, 'package.json');
            const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
            
            // Check for required dependencies
            const requiredDeps = ['react', 'next', 'typescript'];
            const requiredDevDeps = ['@types/react', '@types/node'];
            
            requiredDeps.forEach(dep => {
                if (packageJson.dependencies && packageJson.dependencies[dep]) {
                    this.logResult(`Dependency: ${dep}`, true);
                } else {
                    this.logResult(`Dependency: ${dep}`, false, 'Missing from dependencies');
                }
            });
            
            requiredDevDeps.forEach(dep => {
                if (packageJson.devDependencies && packageJson.devDependencies[dep]) {
                    this.logResult(`Dev dependency: ${dep}`, true);
                } else {
                    this.logResult(`Dev dependency: ${dep}`, false, 'Missing from devDependencies');
                }
            });
            
        } catch (error) {
            this.logResult('Package.json read', false, error.message);
        }
    }

    runAllTests() {
        console.log('🚀 Starting Frontend Testing Suite...');
        console.log('=' * 60);
        
        const startTime = Date.now();
        
        this.testPackageJson();
        this.testAllHooks();
        this.testAllApis();
        
        const endTime = Date.now();
        
        // Print summary
        console.log('\n' + '='.repeat(60));
        console.log('📊 TEST SUMMARY');
        console.log('='.repeat(60));
        console.log(`✅ Passed: ${this.testResults.passed}`);
        console.log(`❌ Failed: ${this.testResults.failed}`);
        console.log(`⏱️  Total time: ${(endTime - startTime) / 1000}s`);
        
        if (this.testResults.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.testResults.errors.forEach(error => {
                console.log(`  - ${error}`);
            });
        }
        
        const successRate = (this.testResults.passed / (this.testResults.passed + this.testResults.failed)) * 100;
        console.log(`\n🎯 Success Rate: ${successRate.toFixed(1)}%`);
        
        return this.testResults.failed === 0;
    }
}

// Run tests
const tester = new FrontendTester();
const success = tester.runAllTests();

if (success) {
    console.log('\n🎉 All frontend tests passed!');
    process.exit(0);
} else {
    console.log('\n💥 Some frontend tests failed!');
    process.exit(1);
}
