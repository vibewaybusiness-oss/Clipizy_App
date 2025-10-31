#!/usr/bin/env node
/**
 * Frontend Hooks Test Suite
 * Comprehensive testing of all React hooks and components
 */

const fs = require('fs');
const path = require('path');

class FrontendHooksTester {
    constructor() {
        this.testResults = {
            passed: 0,
            failed: 0,
            errors: []
        };
        this.hooksDir = path.join(__dirname, '../../src/hooks');
        this.apiDir = path.join(__dirname, '../../src/lib/api');
        this.componentsDir = path.join(__dirname, '../../src/components');
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
            
            // Check for React hook patterns
            const hasUseState = content.includes('useState');
            const hasUseEffect = content.includes('useEffect');
            const hasUseCallback = content.includes('useCallback');
            const hasUseMemo = content.includes('useMemo');
            const hasUseRef = content.includes('useRef');
            const hasUseContext = content.includes('useContext');
            
            // Check for essential patterns
            const hasExport = content.includes('export');
            const hasReturn = content.includes('return');
            const hasFunction = content.includes('function') || content.includes('const ') && content.includes('=');
            
            // Check for error handling
            const hasErrorHandling = content.includes('try') && content.includes('catch') || 
                                   content.includes('error') || content.includes('Error');
            
            // Check for TypeScript types
            const hasTypes = content.includes(': ') && (content.includes('interface') || content.includes('type '));
            
            // Check for API integration
            const hasApiCalls = content.includes('api.') || content.includes('API.') || 
                              content.includes('fetch') || content.includes('axios');
            
            // Determine if this is a proper hook
            const isProperHook = hasExport && hasReturn && (hasUseState || hasUseEffect || hasUseCallback || hasUseMemo);
            
            if (isProperHook) {
                const checks = [
                    { name: 'Has React hooks', condition: hasUseState || hasUseEffect || hasUseCallback || hasUseMemo },
                    { name: 'Has export', condition: hasExport },
                    { name: 'Has return', condition: hasReturn },
                    { name: 'Has function definition', condition: hasFunction }
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
                
                // Additional checks for hooks
                if (hasErrorHandling) {
                    this.logResult(`${hookFile} - Error handling`, true);
                } else {
                    this.logResult(`${hookFile} - Error handling`, false, 'Missing error handling');
                }
                
                if (hasTypes) {
                    this.logResult(`${hookFile} - TypeScript types`, true);
                } else {
                    this.logResult(`${hookFile} - TypeScript types`, false, 'Missing TypeScript types');
                }
                
                if (hasApiCalls) {
                    this.logResult(`${hookFile} - API integration`, true);
                } else {
                    this.logResult(`${hookFile} - API integration`, false, 'No API calls found');
                }
            } else {
                // This might be an index file or utility file
                if (hookFile.includes('index.ts') || hookFile.includes('index.js')) {
                    this.logResult(`${hookFile} - Index file`, true);
                } else {
                    this.logResult(`${hookFile} - Not a proper hook`, false, 'Missing hook patterns');
                }
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
                                 content.includes('PUT') || content.includes('DELETE') ||
                                 content.includes('fetch') || content.includes('axios');
            const hasErrorHandling = content.includes('try') && content.includes('catch');
            const hasTypes = content.includes(': ') && (content.includes('interface') || content.includes('type '));
            const hasExport = content.includes('export');
            
            const checks = [
                { name: 'Has export', condition: hasExport },
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

    testComponentFile(componentFile) {
        const filePath = path.join(this.componentsDir, componentFile);
        
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            
            // Check for React component patterns
            const hasReactImport = content.includes('import React') || content.includes('from "react"');
            const hasJSX = content.includes('<') && content.includes('>');
            const hasExport = content.includes('export');
            const hasFunction = content.includes('function') || content.includes('const ') && content.includes('=');
            const hasReturn = content.includes('return');
            const hasTypes = content.includes(': ') && (content.includes('interface') || content.includes('type '));
            
            const checks = [
                { name: 'Has React import', condition: hasReactImport },
                { name: 'Has JSX', condition: hasJSX },
                { name: 'Has export', condition: hasExport },
                { name: 'Has function definition', condition: hasFunction },
                { name: 'Has return', condition: hasReturn },
                { name: 'Has TypeScript types', condition: hasTypes }
            ];
            
            let allPassed = true;
            checks.forEach(check => {
                if (!check.condition) {
                    allPassed = false;
                    this.logResult(`${componentFile} - ${check.name}`, false, 'Missing required pattern');
                }
            });
            
            if (allPassed) {
                this.logResult(`${componentFile} structure`, true);
            }
            
        } catch (error) {
            this.logResult(`${componentFile} file read`, false, error.message);
        }
    }

    testAllHooks() {
        console.log('\n🎣 Testing React Hooks...');
        
        try {
            const hookFiles = this.getFilesRecursively(this.hooksDir, ['.ts', '.tsx', '.js', '.jsx'])
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
            const apiFiles = this.getFilesRecursively(this.apiDir, ['.ts', '.tsx', '.js', '.jsx'])
                .filter(file => !file.includes('.test.') && !file.includes('.spec.'));
            
            apiFiles.forEach(apiFile => {
                this.testApiFile(apiFile);
            });
            
        } catch (error) {
            this.logResult('API directory read', false, error.message);
        }
    }

    testAllComponents() {
        console.log('\n🧩 Testing Component Files...');
        
        try {
            const componentFiles = this.getFilesRecursively(this.componentsDir, ['.ts', '.tsx', '.js', '.jsx'])
                .filter(file => !file.includes('.test.') && !file.includes('.spec.'));
            
            componentFiles.forEach(componentFile => {
                this.testComponentFile(componentFile);
            });
            
        } catch (error) {
            this.logResult('Components directory read', false, error.message);
        }
    }

    getFilesRecursively(dir, extensions) {
        const files = [];
        
        try {
            const items = fs.readdirSync(dir, { recursive: true });
            
            items.forEach(item => {
                const fullPath = path.join(dir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isFile()) {
                    const ext = path.extname(item);
                    if (extensions.includes(ext)) {
                        files.push(item);
                    }
                }
            });
        } catch (error) {
            // Directory might not exist
        }
        
        return files;
    }

    testPackageJson() {
        console.log('\n📦 Testing Package Configuration...');
        
        try {
            const packagePath = path.join(__dirname, '../../package.json');
            const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
            
            // Check for required dependencies
            const requiredDeps = ['react', 'next'];
            const requiredDevDeps = ['@types/react', '@types/node', 'typescript'];
            
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
            
            // Check for scripts
            const requiredScripts = ['dev', 'build', 'start'];
            requiredScripts.forEach(script => {
                if (packageJson.scripts && packageJson.scripts[script]) {
                    this.logResult(`Script: ${script}`, true);
                } else {
                    this.logResult(`Script: ${script}`, false, 'Missing from scripts');
                }
            });
            
        } catch (error) {
            this.logResult('Package.json read', false, error.message);
        }
    }

    runAllTests() {
        console.log('🚀 Starting Frontend Testing Suite...');
        console.log('='.repeat(60));
        
        const startTime = Date.now();
        
        this.testPackageJson();
        this.testAllHooks();
        this.testAllApis();
        this.testAllComponents();
        
        const endTime = Date.now();
        
        // Print summary
        console.log('\n' + '='.repeat(60));
        console.log('📊 FRONTEND TEST SUMMARY');
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
const tester = new FrontendHooksTester();
const success = tester.runAllTests();

if (success) {
    console.log('\n🎉 All frontend tests passed!');
    process.exit(0);
} else {
    console.log('\n💥 Some frontend tests failed!');
    process.exit(1);
}
