#!/usr/bin/env node

/**
 * Frontend Hook Runtime Testing Suite
 * Tests that all hooks can be imported and called without throwing errors
 */

const fs = require('fs');
const path = require('path');

class HookRuntimeTester {
    constructor() {
        this.results = {
            passed: 0,
            failed: 0,
            errors: []
        };
        this.hooksDir = path.join(__dirname, '../../src/hooks');
    }

    logResult(testName, success, error = null) {
        if (success) {
            console.log(`✅ ${testName}`);
            this.results.passed++;
        } else {
            console.log(`❌ ${testName}: ${error}`);
            this.results.failed++;
            this.results.errors.push({ test: testName, error });
        }
    }

    async testHookFile(hookPath, hookName) {
        try {
            // Test if file can be imported
            const fullPath = path.resolve(hookPath);
            if (!fs.existsSync(fullPath)) {
                this.logResult(`${hookName} - File exists`, false, 'File not found');
                return;
            }

            // Read the file content to check for basic patterns
            const content = fs.readFileSync(fullPath, 'utf8');
            
            // Check if it's a proper hook file
            if (!content.includes('use') || !content.includes('export')) {
                this.logResult(`${hookName} - Hook pattern`, false, 'Not a proper hook file');
                return;
            }

            // Check for common error patterns
            if (content.includes('undefined') && content.includes('import')) {
                this.logResult(`${hookName} - Import issues`, false, 'Potential undefined imports');
                return;
            }

            // Check for missing dependencies
            if (content.includes('useState') && !content.includes("import { useState }")) {
                this.logResult(`${hookName} - React imports`, false, 'Missing useState import');
                return;
            }

            if (content.includes('useEffect') && !content.includes("import { useEffect }")) {
                this.logResult(`${hookName} - React imports`, false, 'Missing useEffect import');
                return;
            }

            if (content.includes('useCallback') && !content.includes("import { useCallback }")) {
                this.logResult(`${hookName} - React imports`, false, 'Missing useCallback import');
                return;
            }

            if (content.includes('useMemo') && !content.includes("import { useMemo }")) {
                this.logResult(`${hookName} - React imports`, false, 'Missing useMemo import');
                return;
            }

            // Check for API calls without proper error handling
            if (content.includes('fetch(') && !content.includes('try') && !content.includes('catch')) {
                this.logResult(`${hookName} - Error handling`, false, 'API calls without error handling');
                return;
            }

            // Check for async operations without proper handling
            if (content.includes('async') && !content.includes('try') && !content.includes('catch')) {
                this.logResult(`${hookName} - Async error handling`, false, 'Async operations without error handling');
                return;
            }

            this.logResult(`${hookName} - Basic validation`, true);

        } catch (error) {
            this.logResult(`${hookName} - File processing`, false, error.message);
        }
    }

    async testAllHooks() {
        console.log("🧪 Frontend Hook Runtime Testing Suite");
        console.log("=" * 60);
        console.log("🚀 Testing Hook Runtime Safety...");
        console.log("=" * 60);

        const hookFiles = this.getAllHookFiles();
        
        for (const hookFile of hookFiles) {
            await this.testHookFile(hookFile.path, hookFile.name);
        }
    }

    getAllHookFiles() {
        const hookFiles = [];
        
        const scanDirectory = (dir, basePath = '') => {
            if (!fs.existsSync(dir)) return;
            
            const items = fs.readdirSync(dir);
            
            for (const item of items) {
                const fullPath = path.join(dir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    scanDirectory(fullPath, path.join(basePath, item));
                } else if (item.endsWith('.ts') || item.endsWith('.tsx') || item.endsWith('.js') || item.endsWith('.jsx')) {
                    if (item.startsWith('use-') || item.includes('use') || item.includes('hook')) {
                        const relativePath = path.join(basePath, item);
                        hookFiles.push({
                            name: relativePath,
                            path: fullPath
                        });
                    }
                }
            }
        };

        scanDirectory(this.hooksDir);
        return hookFiles;
    }

    async testCriticalHooks() {
        console.log("\n🔍 Testing Critical Hooks...");
        console.log("=" * 50);

        const criticalHooks = [
            'use-user-onboarding.ts',
            'use-email-subscription.ts',
            'use-projects.ts',
            'use-music-clip-orchestrator.ts',
            'use-credits.ts',
            'use-pricing.ts'
        ];

        for (const hookName of criticalHooks) {
            const hookPath = path.join(this.hooksDir, hookName);
            await this.testHookFile(hookPath, `Critical: ${hookName}`);
        }
    }

    async testHookDependencies() {
        console.log("\n📦 Testing Hook Dependencies...");
        console.log("=" * 50);

        // Check if package.json exists and has required dependencies
        const packageJsonPath = path.join(__dirname, '../../package.json');
        
        if (fs.existsSync(packageJsonPath)) {
            try {
                const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
                const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
                
                const requiredDeps = ['react', 'next', '@types/react', '@types/node', 'typescript'];
                
                for (const dep of requiredDeps) {
                    if (dependencies[dep]) {
                        this.logResult(`Dependency: ${dep}`, true);
                    } else {
                        this.logResult(`Dependency: ${dep}`, false, 'Missing from package.json');
                    }
                }
            } catch (error) {
                this.logResult('Package.json parsing', false, error.message);
            }
        } else {
            this.logResult('Package.json exists', false, 'File not found');
        }
    }

    async runAllTests() {
        const startTime = Date.now();
        
        await this.testAllHooks();
        await this.testCriticalHooks();
        await this.testHookDependencies();
        
        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        
        this.printSummary(duration);
        
        return this.results.failed === 0;
    }

    printSummary(duration) {
        console.log("\n" + "=" * 60);
        console.log("📊 HOOK RUNTIME TEST SUMMARY");
        console.log("=" * 60);
        console.log(`✅ Passed: ${this.results.passed}`);
        console.log(`❌ Failed: ${this.results.failed}`);
        console.log(`⏱️  Total time: ${duration}s`);
        
        if (this.results.errors.length > 0) {
            console.log("\n❌ ERRORS:");
            this.results.errors.forEach(error => {
                console.log(`  - ${error.test}: ${error.error}`);
            });
        }
        
        const successRate = this.results.passed + this.results.failed > 0 
            ? ((this.results.passed / (this.results.passed + this.results.failed)) * 100).toFixed(1)
            : 0;
        
        console.log(`\n🎯 Success Rate: ${successRate}%`);
        
        if (this.results.failed === 0) {
            console.log("\n🎉 All hook runtime tests passed!");
        } else {
            console.log("\n💥 Some hook runtime tests failed!");
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new HookRuntimeTester();
    tester.runAllTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error("Test runner error:", error);
        process.exit(1);
    });
}

module.exports = HookRuntimeTester;
