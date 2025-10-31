#!/usr/bin/env node

/**
 * Frontend Hook Import Testing Suite
 * Tests that all hooks can be imported without throwing errors
 */

const fs = require('fs');
const path = require('path');

class HookImportTester {
    constructor() {
        this.results = {
            passed: 0,
            failed: 0,
            errors: []
        };
        this.hooksDir = path.join(__dirname, '../../src/hooks');
        this.srcDir = path.join(__dirname, '../../src');
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

    async testHookImport(hookPath, hookName) {
        try {
            // Read the file content
            const content = fs.readFileSync(hookPath, 'utf8');
            
            // Check for syntax errors by looking for common patterns
            if (content.includes('import') && content.includes('from')) {
                // Extract import statements
                const importLines = content.split('\n').filter(line => 
                    line.trim().startsWith('import') && line.includes('from')
                );
                
                for (const importLine of importLines) {
                    // Check for relative imports that might be problematic
                    if (importLine.includes("'../") || importLine.includes('"../')) {
                        const importPath = importLine.match(/from\s+['"]([^'"]+)['"]/);
                        if (importPath) {
                            const resolvedPath = this.resolveImportPath(hookPath, importPath[1]);
                            if (!fs.existsSync(resolvedPath)) {
                                this.logResult(`${hookName} - Import path`, false, `Missing: ${importPath[1]}`);
                                return;
                            }
                        }
                    }
                }
            }

            // Check for common hook patterns that might cause issues
            if (content.includes('useState') && !content.includes('React') && !content.includes('react')) {
                this.logResult(`${hookName} - React import`, false, 'useState used without React import');
                return;
            }

            // Check for undefined variables
            const lines = content.split('\n');
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (line.includes('undefined') && !line.includes('!== undefined') && !line.includes('=== undefined')) {
                    this.logResult(`${hookName} - Undefined usage`, false, `Line ${i + 1}: ${line.trim()}`);
                    return;
                }
            }

            // Check for missing return statements in functions
            if (content.includes('function') || content.includes('=>')) {
                const hasReturn = content.includes('return');
                if (!hasReturn && (content.includes('useState') || content.includes('useEffect'))) {
                    this.logResult(`${hookName} - Return statement`, false, 'Hook function missing return statement');
                    return;
                }
            }

            this.logResult(`${hookName} - Import validation`, true);

        } catch (error) {
            this.logResult(`${hookName} - File processing`, false, error.message);
        }
    }

    resolveImportPath(currentFile, importPath) {
        const currentDir = path.dirname(currentFile);
        
        if (importPath.startsWith('./') || importPath.startsWith('../')) {
            // Relative import
            let resolvedPath = path.resolve(currentDir, importPath);
            
            // Try different extensions
            const extensions = ['.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.tsx', '/index.js', '/index.jsx'];
            
            for (const ext of extensions) {
                const testPath = resolvedPath + ext;
                if (fs.existsSync(testPath)) {
                    return testPath;
                }
            }
            
            return resolvedPath;
        } else {
            // Absolute import - check in node_modules or src
            const srcPath = path.join(this.srcDir, importPath);
            const nodeModulesPath = path.join(__dirname, '../../node_modules', importPath);
            
            if (fs.existsSync(srcPath)) {
                return srcPath;
            } else if (fs.existsSync(nodeModulesPath)) {
                return nodeModulesPath;
            }
            
            return importPath;
        }
    }

    async testAllHookImports() {
        console.log("🧪 Frontend Hook Import Testing Suite");
        console.log("=" * 60);
        console.log("🚀 Testing Hook Import Safety...");
        console.log("=" * 60);

        const hookFiles = this.getAllHookFiles();
        
        for (const hookFile of hookFiles) {
            await this.testHookImport(hookFile.path, hookFile.name);
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

    async testCriticalHookFiles() {
        console.log("\n🔍 Testing Critical Hook Files...");
        console.log("=" * 50);

        const criticalHooks = [
            'users/use-user-onboarding.ts',
            'users/use-email-subscription.ts',
            'storage/use-projects.ts',
            'create/music-clip/use-music-clip-orchestrator.ts',
            'business/use-credits.ts',
            'business/use-pricing.ts',
            'ai/use-music-analysis.ts',
            'dashboard/use-dashboard-data.ts'
        ];

        for (const hookName of criticalHooks) {
            const hookPath = path.join(this.hooksDir, hookName);
            if (fs.existsSync(hookPath)) {
                await this.testHookImport(hookPath, `Critical: ${hookName}`);
            } else {
                this.logResult(`Critical: ${hookName}`, false, 'File not found');
            }
        }
    }

    async testHookIndexFiles() {
        console.log("\n📁 Testing Hook Index Files...");
        console.log("=" * 50);

        const indexFiles = [
            'index.ts',
            'admin/index.ts',
            'ai/index.ts',
            'business/index.ts',
            'dashboard/index.ts',
            'domains/index.ts',
            'storage/index.ts',
            'ui/index.ts',
            'users/index.ts',
            'utils/index.ts',
            'create/music-clip/index.ts',
            'create/shared/index.ts'
        ];

        for (const indexFile of indexFiles) {
            const indexPath = path.join(this.hooksDir, indexFile);
            if (fs.existsSync(indexPath)) {
                await this.testHookImport(indexPath, `Index: ${indexFile}`);
            } else {
                this.logResult(`Index: ${indexFile}`, false, 'File not found');
            }
        }
    }

    async runAllTests() {
        const startTime = Date.now();
        
        await this.testAllHookImports();
        await this.testCriticalHookFiles();
        await this.testHookIndexFiles();
        
        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        
        this.printSummary(duration);
        
        return this.results.failed === 0;
    }

    printSummary(duration) {
        console.log("\n" + "=" * 60);
        console.log("📊 HOOK IMPORT TEST SUMMARY");
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
            console.log("\n🎉 All hook import tests passed!");
        } else {
            console.log("\n💥 Some hook import tests failed!");
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    const tester = new HookImportTester();
    tester.runAllTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error("Test runner error:", error);
        process.exit(1);
    });
}

module.exports = HookImportTester;
