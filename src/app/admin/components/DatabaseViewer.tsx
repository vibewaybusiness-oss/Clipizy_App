"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/ui/use-toast";
import { 
  Database, 
  Table, 
  Search, 
  RefreshCw, 
  ChevronLeft, 
  ChevronRight,
  Info,
  Eye,
  Code,
  BarChart3,
  Server,
  X,
  Copy,
  CheckCircle
} from "lucide-react";

interface TableInfo {
  name: string;
  row_count: number;
  table_size: string;
  columns: Array<{
    name: string;
    type: string;
    nullable: boolean;
    default: string | null;
    max_length: number | null;
  }>;
}

interface TableData {
  data: any[];
  pagination: {
    limit: number;
    offset: number;
    total_count: number;
    has_more: boolean;
  };
}

interface DatabaseOverview {
  database: {
    name: string;
    size: string;
    version: string;
  };
  tables: Array<{
    name: string;
    schema: string;
    live_tuples: number;
    dead_tuples: number;
    inserts: number;
    updates: number;
    deletes: number;
  }>;
}

export default function DatabaseViewer() {
  const [overview, setOverview] = useState<DatabaseOverview | null>(null);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableInfo, setTableInfo] = useState<TableInfo | null>(null);
  const [tableData, setTableData] = useState<TableData | null>(null);
  const [currentOffset, setCurrentOffset] = useState(0);
  const [customQuery, setCustomQuery] = useState("");
  const [queryResult, setQueryResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCell, setSelectedCell] = useState<{value: any, column: string, row: number} | null>(null);
  const [copiedValue, setCopiedValue] = useState<string | null>(null);
  const { toast } = useToast();

  const limit = 50;

  const handleCellClick = (value: any, column: string, row: number) => {
    setSelectedCell({ value, column, row });
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedValue(text);
      setTimeout(() => setCopiedValue(null), 2000);
      toast({
        title: "Copied",
        description: "Value copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy to clipboard",
        variant: "destructive"
      });
    }
  };

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/database/overview');
      
      if (!response.ok) {
        throw new Error('Failed to fetch overview');
      }
      const data = await response.json();
      setOverview(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch overview');
    } finally {
      setLoading(false);
    }
  };

  const fetchTables = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/database/tables');
      
      if (!response.ok) throw new Error('Failed to fetch tables');
      const data = await response.json();
      setTables(data.tables);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tables');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch overview and tables
      await Promise.all([fetchOverview(), fetchTables()]);
      
      // If a table is currently selected, refresh its data
      if (selectedTable) {
        await fetchTableInfo(selectedTable);
        await fetchTableData(selectedTable, currentOffset);
      }
      
      toast({
        title: "Data Refreshed",
        description: "Database information has been updated",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
      toast({
        title: "Refresh Failed",
        description: "Failed to refresh database data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchTableInfo = async (tableName: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/database/tables/${tableName}/info`);
      
      if (!response.ok) throw new Error('Failed to fetch table info');
      const data = await response.json();
      setTableInfo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch table info');
    } finally {
      setLoading(false);
    }
  };

  const fetchTableData = async (tableName: string, offset: number = 0) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/database/tables/${tableName}/data?limit=${limit}&offset=${offset}`);
      
      if (!response.ok) throw new Error('Failed to fetch table data');
      const data = await response.json();
      setTableData(data);
      setCurrentOffset(offset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch table data');
    } finally {
      setLoading(false);
    }
  };

  const executeCustomQuery = async () => {
    if (!customQuery.trim()) {
      toast({
        title: "Error",
        description: "Please enter a query",
        variant: "destructive"
      });
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`/api/admin/database/query?query=${encodeURIComponent(customQuery)}`);
      
      if (!response.ok) throw new Error('Query execution failed');
      const data = await response.json();
      setQueryResult(data);
      
      toast({
        title: "Success",
        description: `Query executed successfully. Found ${data.row_count} rows.`,
      });
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Query execution failed',
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTableSelect = (tableName: string) => {
    setSelectedTable(tableName);
    fetchTableInfo(tableName);
    fetchTableData(tableName, 0);
  };

  const handlePageChange = (direction: 'prev' | 'next') => {
    if (!selectedTable || !tableData) return;
    
    const newOffset = direction === 'next' 
      ? currentOffset + limit 
      : Math.max(0, currentOffset - limit);
    
    fetchTableData(selectedTable, newOffset);
  };

  useEffect(() => {
    fetchOverview();
    fetchTables();
  }, []);

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database Viewer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-destructive">{error}</p>
            <Button onClick={refreshData} className="mt-4" disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Database Overview
              </CardTitle>
              <CardDescription>
                Real-time database statistics and information
              </CardDescription>
            </div>
            <Button 
              onClick={refreshData} 
              disabled={loading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh Data
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {overview ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Database</Label>
                <p className="text-2xl font-bold">{overview.database.name}</p>
                <p className="text-sm text-muted-foreground">Size: {overview.database.size}</p>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Tables</Label>
                <p className="text-2xl font-bold">{overview.tables.length}</p>
                <p className="text-sm text-muted-foreground">Total tables</p>
              </div>
              <div className="space-y-2">
                <Label className="text-sm font-medium">Total Rows</Label>
                <p className="text-2xl font-bold">
                  {overview.tables.reduce((sum, table) => sum + table.live_tuples, 0).toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">Across all tables</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
              <p>Loading database overview...</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="tables" className="space-y-6">
        <TabsList>
          <TabsTrigger value="tables">Tables</TabsTrigger>
          <TabsTrigger value="query">Custom Query</TabsTrigger>
        </TabsList>

        <TabsContent value="tables" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Table className="h-5 w-5" />
                    Database Tables
                  </CardTitle>
                  <CardDescription>
                    Select a table to view its data and structure
                  </CardDescription>
                </div>
                <Button 
                  onClick={refreshData} 
                  disabled={loading}
                  variant="outline"
                  size="sm"
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">Table Name</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tables.map((table) => (
                        <tr 
                          key={table} 
                          className={`border-b hover:bg-muted/30 transition-colors cursor-pointer ${
                            selectedTable === table ? 'bg-primary/10' : ''
                          }`}
                          onClick={() => handleTableSelect(table)}
                        >
                          <td className="px-4 py-3 text-sm font-medium">
                            {table}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8"
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Data
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </CardContent>
          </Card>

          {selectedTable && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Table className="h-5 w-5" />
                      Table: {selectedTable}
                    </CardTitle>
                    <CardDescription>
                      Table structure and data
                    </CardDescription>
                  </div>
                  <Button 
                    onClick={() => {
                      if (selectedTable) {
                        fetchTableInfo(selectedTable);
                        fetchTableData(selectedTable, currentOffset);
                      }
                    }} 
                    disabled={loading}
                    variant="outline"
                    size="sm"
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh Table
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {tableInfo && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label className="text-sm font-medium">Rows</Label>
                        <p className="text-xl font-bold">{tableInfo.row_count.toLocaleString()}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Size</Label>
                        <p className="text-xl font-bold">{tableInfo.table_size}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Columns</Label>
                        <p className="text-xl font-bold">{tableInfo.columns.length}</p>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium mb-2 block">Column Structure</Label>
                      <div className="border rounded-lg overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse">
                            <thead className="bg-muted/50">
                              <tr>
                                <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">Column Name</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">Data Type</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">Nullable</th>
                              </tr>
                            </thead>
                            <tbody>
                              {tableInfo.columns.map((col, index) => (
                                <tr key={index} className="border-b hover:bg-muted/30 transition-colors">
                                  <td className="px-4 py-3 text-sm font-medium">
                                    {col.name}
                                  </td>
                                  <td className="px-4 py-3 text-sm">
                                    <Badge variant="secondary">{col.type}</Badge>
                                  </td>
                                  <td className="px-4 py-3 text-sm">
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                      col.nullable 
                                        ? 'bg-yellow-100 text-yellow-800' 
                                        : 'bg-red-100 text-red-800'
                                    }`}>
                                      {col.nullable ? 'NULL' : 'NOT NULL'}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {tableData && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label className="text-sm font-medium">
                        Data ({tableData.pagination.total_count.toLocaleString()} total rows)
                      </Label>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange('prev')}
                          disabled={currentOffset === 0 || loading}
                        >
                          <ChevronLeft className="h-4 w-4" />
                          Previous
                        </Button>
                        <span className="text-sm text-muted-foreground">
                          Page {Math.floor(currentOffset / limit) + 1}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange('next')}
                          disabled={!tableData.pagination.has_more || loading}
                        >
                          Next
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="border rounded-lg overflow-hidden">
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                          <thead className="bg-muted/50">
                            <tr>
                              {tableData.data.length > 0 && Object.keys(tableData.data[0]).map((key) => (
                                <th key={key} className="px-4 py-3 text-left text-sm font-semibold text-foreground border-b">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {tableData.data.map((row, index) => (
                              <tr key={index} className="border-b hover:bg-muted/30 transition-colors">
                                {Object.values(row).map((value, cellIndex) => {
                                  const columnName = Object.keys(row)[cellIndex];
                                  const isLongValue = typeof value === 'string' && value.length > 50;
                                  const isObject = typeof value === 'object' && value !== null;
                                  const isLongObject = isObject && JSON.stringify(value).length > 50;
                                  
                                  return (
                                    <td key={cellIndex} className="px-4 py-3 text-sm border-r last:border-r-0">
                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <button
                                            onClick={() => handleCellClick(value, columnName, index)}
                                            className="w-full text-left hover:bg-muted/50 rounded p-1 transition-colors"
                                          >
                                            {value === null ? (
                                              <span className="text-muted-foreground italic">NULL</span>
                                            ) : isObject ? (
                                              <code className="text-xs bg-muted px-2 py-1 rounded font-mono">
                                                {JSON.stringify(value).substring(0, 50)}
                                                {isLongObject ? '...' : ''}
                                              </code>
                                            ) : typeof value === 'boolean' ? (
                                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                              }`}>
                                                {value ? 'true' : 'false'}
                                              </span>
                                            ) : isLongValue ? (
                                              <span title={value} className="cursor-help">
                                                {String(value).substring(0, 50)}...
                                              </span>
                                            ) : (
                                              <span>{String(value)}</span>
                                            )}
                                          </button>
                                        </DialogTrigger>
                                        <DialogContent className="max-w-4xl max-h-[80vh] overflow-auto">
                                          <DialogHeader>
                                            <DialogTitle className="flex items-center gap-2">
                                              <Info className="h-5 w-5" />
                                              Cell Data - {columnName}
                                            </DialogTitle>
                                          </DialogHeader>
                                          <div className="space-y-4">
                                            <div className="grid grid-cols-2 gap-4 text-sm">
                                              <div>
                                                <Label className="font-medium">Column:</Label>
                                                <p className="text-muted-foreground">{columnName}</p>
                                              </div>
                                              <div>
                                                <Label className="font-medium">Row:</Label>
                                                <p className="text-muted-foreground">{index + 1}</p>
                                              </div>
                                            </div>
                                            <div>
                                              <Label className="font-medium">Value:</Label>
                                              <div className="mt-2 p-4 bg-muted rounded-lg">
                                                {value === null ? (
                                                  <span className="text-muted-foreground italic">NULL</span>
                                                ) : isObject ? (
                                                  <pre className="text-xs font-mono whitespace-pre-wrap overflow-auto">
                                                    {JSON.stringify(value, null, 2)}
                                                  </pre>
                                                ) : typeof value === 'boolean' ? (
                                                  <span className={`px-3 py-2 rounded text-sm font-medium ${
                                                    value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                  }`}>
                                                    {value ? 'true' : 'false'}
                                                  </span>
                                                ) : (
                                                  <pre className="text-sm whitespace-pre-wrap break-words">
                                                    {String(value)}
                                                  </pre>
                                                )}
                                              </div>
                                            </div>
                                            <div className="flex justify-end gap-2">
                                              <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => copyToClipboard(
                                                  value === null ? 'NULL' : 
                                                  isObject ? JSON.stringify(value, null, 2) : 
                                                  String(value)
                                                )}
                                              >
                                                {copiedValue === (value === null ? 'NULL' : 
                                                  isObject ? JSON.stringify(value, null, 2) : 
                                                  String(value)) ? (
                                                  <CheckCircle className="h-4 w-4 mr-2" />
                                                ) : (
                                                  <Copy className="h-4 w-4 mr-2" />
                                                )}
                                                Copy Value
                                              </Button>
                                            </div>
                                          </div>
                                        </DialogContent>
                                      </Dialog>
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="query" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Custom SQL Query
              </CardTitle>
              <CardDescription>
                Execute custom SQL queries (SELECT only for security)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="query">SQL Query</Label>
                <Textarea
                  id="query"
                  placeholder="SELECT * FROM users LIMIT 10;"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  className="min-h-[100px] font-mono"
                />
              </div>
              <Button onClick={executeCustomQuery} disabled={loading || !customQuery.trim()}>
                <Code className="h-4 w-4 mr-2" />
                {loading ? 'Executing...' : 'Execute Query'}
              </Button>

              {queryResult && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">
                      {queryResult.row_count} rows
                    </Badge>
                    <Badge variant="outline">
                      {queryResult.columns.length} columns
                    </Badge>
                  </div>

                  <div className="border rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-muted/50">
                          <tr>
                            {queryResult.columns.map((col: string) => (
                              <th key={col} className="px-4 py-2 text-left text-sm font-medium">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {queryResult.data.map((row: any, index: number) => (
                            <tr key={index} className="border-t">
                              {queryResult.columns.map((col: string, cellIndex: number) => (
                                <td key={cellIndex} className="px-4 py-2 text-sm">
                                  {row[col] === null ? (
                                    <span className="text-muted-foreground">NULL</span>
                                  ) : typeof row[col] === 'object' ? (
                                    <code className="text-xs bg-muted px-1 rounded">
                                      {JSON.stringify(row[col]).substring(0, 50)}
                                      {JSON.stringify(row[col]).length > 50 ? '...' : ''}
                                    </code>
                                  ) : (
                                    <span>{String(row[col]).substring(0, 100)}</span>
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
