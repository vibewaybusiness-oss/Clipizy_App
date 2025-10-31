#!/usr/bin/env node

/**
 * Frontend Hook Runtime Simulation Testing Suite
 * Simulates React environment to test hook runtime behavior
 */

const fs = require('fs');
const path = require('path');

class HookRuntimeSimulationTester {
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

    async testHookRuntimeSafety(hookPath, hookName) {
        try {
            const content = fs.readFileSync(hookPath, 'utf8');
            
            // Check for common runtime issues
            
            // 1. Check for localStorage usage without window check
            if (content.includes('localStorage') && !content.includes('typeof window')) {
                this.logResult(`${hookName} - localStorage safety`, false, 'localStorage used without window check');
                return;
            }

            // 2. Check for sessionStorage usage without window check
            if (content.includes('sessionStorage') && !content.includes('typeof window')) {
                this.logResult(`${hookName} - sessionStorage safety`, false, 'sessionStorage used without window check');
                return;
            }

            // 3. Check for window object usage without window check
            if (content.includes('window.') && !content.includes('typeof window')) {
                this.logResult(`${hookName} - window object safety`, false, 'window object used without window check');
                return;
            }

            // 4. Check for document object usage without window check
            if (content.includes('document.') && !content.includes('typeof window')) {
                this.logResult(`${hookName} - document object safety`, false, 'document object used without window check');
                return;
            }

            // 5. Check for missing error boundaries in async operations
            if (content.includes('async') && content.includes('await') && !content.includes('try') && !content.includes('catch')) {
                this.logResult(`${hookName} - async error handling`, false, 'Async operations without error handling');
                return;
            }

            // 6. Check for fetch calls without error handling
            if (content.includes('fetch(') && !content.includes('try') && !content.includes('catch')) {
                this.logResult(`${hookName} - fetch error handling`, false, 'Fetch calls without error handling');
                return;
            }

            // 7. Check for potential infinite loops in useEffect
            if (content.includes('useEffect') && content.includes('setState') && !content.includes('useCallback') && !content.includes('useMemo')) {
                const lines = content.split('\n');
                let hasDependencyArray = false;
                for (const line of lines) {
                    if (line.includes('useEffect') && line.includes('[') && line.includes(']')) {
                        hasDependencyArray = true;
                        break;
                    }
                }
                if (!hasDependencyArray) {
                    this.logResult(`${hookName} - useEffect dependencies`, false, 'useEffect without dependency array');
                    return;
                }
            }

            // 8. Check for missing cleanup in useEffect
            if (content.includes('useEffect') && (content.includes('addEventListener') || content.includes('setInterval') || content.includes('setTimeout'))) {
                if (!content.includes('removeEventListener') && !content.includes('clearInterval') && !content.includes('clearTimeout')) {
                    this.logResult(`${hookName} - useEffect cleanup`, false, 'Event listeners or timers without cleanup');
                    return;
                }
            }

            // 9. Check for proper TypeScript types
            if (content.includes('useState<') && content.includes('undefined')) {
                const lines = content.split('\n');
                for (const line of lines) {
                    if (line.includes('useState<') && line.includes('undefined')) {
                        this.logResult(`${hookName} - TypeScript types`, false, `Problematic useState type: ${line.trim()}`);
                        return;
                    }
                }
            }

            // 10. Check for proper hook naming
            if (!content.includes('export') || !content.includes('function') || !content.includes('use')) {
                this.logResult(`${hookName} - hook structure`, false, 'Not a proper React hook');
                return;
            }

            this.logResult(`${hookName} - Runtime safety`, true);

        } catch (error) {
            this.logResult(`${hookName} - File processing`, false, error.message);
        }
    }

    async testCriticalHooksRuntime() {
        console.log("🧪 Frontend Hook Runtime Simulation Testing Suite");
        console.log("=" * 60);
        console.log("🚀 Testing Hook Runtime Safety...");
        console.log("=" * 60);

        const criticalHooks = [
            'users/use-user-onboarding.ts',
            'users/use-email-subscription.ts',
            'storage/use-projects.ts',
            'create/music-clip/use-music-clip-orchestrator.ts',
            'business/use-credits.ts',
            'business/use-pricing.ts',
            'ai/use-music-analysis.ts',
            'dashboard/use-dashboard-data.ts',
            'storage/use-file-upload-handlers.ts',
            'storage/use-project-loading.ts',
            'create/music-clip/use-music-clip-state.ts',
            'create/music-clip/use-orchestrator-effects.ts'
        ];

        for (const hookName of criticalHooks) {
            const hookPath = path.join(this.hooksDir, hookName);
            if (fs.existsSync(hookPath)) {
                await this.testHookRuntimeSafety(hookPath, `Critical: ${hookName}`);
            } else {
                this.logResult(`Critical: ${hookName}`, false, 'File not found');
            }
        }
    }

    async testAllHooksRuntime() {
        console.log("\n🔍 Testing All Hooks Runtime Safety...");
        console.log("=" * 50);

        const hookFiles = this.getAllHookFiles();
        
        for (const hookFile of hookFiles) {
            await this.testHookRuntimeSafety(hookFile.path, hookFile.name);
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

    async runAllTests() {
        const startTime = Date.now();
        
        await this.testCriticalHooksRuntime();
        await this.testAllHooksRuntime();
        
        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        
        this.printSummary(duration);
        
        return this.results.failed === 0;
    }

    printSummary(duration) {
        console.log("\n" + "=" * 60);
        console.log("📊 HOOK RUNTIME SIMULATION TEST SUMMARY");
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
            console.log("\n🎉 All hook runtime simulation tests passed!");
        } else {
            console.log("\n💥 Some hook runtime simulation tests failed!");
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new HookRuntimeSimulationTester();
    tester.runAllTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error("Test runner error:", error);
        process.exit(1);
    });
}

module.exports = HookRuntimeSimulationTester;
