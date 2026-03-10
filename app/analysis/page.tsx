'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TriangleAlert as AlertTriangle, Copy, CircleCheck as CheckCircle2, CircleAlert as AlertCircle, Circle as XCircle, Upload } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';

interface AnalysisData {
  profile: {
    total_rows: number;
    total_columns: number;
    health_score: number;
    missing_values: {
      total_missing_values: number;
      columns_with_missing: Record<string, { count: number; percentage: number }>;
    };
    duplicates: {
      total_duplicate_rows: number;
      duplicate_percentage: number;
      columns_with_duplicates: Record<string, number>;
    };
    outliers: {
      columns_with_outliers: Record<string, any>;
      total_outlier_columns: number;
    };
    datatypes: Record<string, {
      datatype: string;
      non_null_count: number;
      null_count: number;
      unique_values: number;
    }>;
  };
  recommendations: Array<{
    column: string;
    issue: string;
    severity: string;
    problem: string;
    recommendation: string;
  }>;
  categorized_recommendations: Record<string, Array<any>>;
  cleaning_code: {
    basic: string;
    advanced: string;
  };
}

export default function AnalysisPage() {
  const router = useRouter();
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [codeCopied, setCodeCopied] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [codeType, setCodeType] = useState<'basic' | 'advanced'>('basic');

  useEffect(() => {
    // Check if user has uploaded a file in the upload page
    const storedFile = localStorage.getItem('uploadedFile');
    if (storedFile) {
      try {
        const fileData = JSON.parse(storedFile);
        performAnalysis(fileData);
      } catch (err) {
        setError('Session file data corrupted. Please upload again.');
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const performAnalysis = async (fileData: any) => {
    try {
      setLoading(true);
      setError(null);

      // Reconstruct file from stored data
      const byteArray = new Uint8Array(fileData.data);
      const file = new File([byteArray], fileData.name, { type: fileData.type });
      setUploadedFile(file);

      // Call analyze endpoint for full analysis with timeout
      const formData = new FormData();
      formData.append('file', file);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      try {
        // log file information for debugging
      console.log('Sending file to /analyze', file.name, file.size, file.type);
      const response = await fetch('http://127.0.0.1:9000/analyze', {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Response error:', response.status, errorText);
          // include error text in thrown error so UI can display it
          throw new Error(`Analysis failed with status ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        
        setAnalysisData({
          profile: data.profile,
          recommendations: data.recommendations,
          categorized_recommendations: data.categorized_recommendations,
          cleaning_code: data.cleaning_code,
        });
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Analysis took too long. Please try with a smaller dataset.');
        }
        throw fetchError;
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(`Failed to analyze dataset: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTestData = () => {
    // CSV content: Name,Age,Salary,Department...
    const csvContent = `Name,Age,Salary,Department
Alice,30,50000,HR
Bob,35,60000,Sales
Charlie,28,55000,IT
Diana,32,65000,HR
Eve,29,58000,Sales
Frank,31,62000,IT
Grace,33,,Sales
Henry,27,52000,HR
Ivy,30,59000,IT`;
    
    const encoder = new TextEncoder();
    const uint8Array = encoder.encode(csvContent);
    const fileData = {
      name: 'sample_data.csv',
      type: 'text/csv',
      data: Array.from(uint8Array),
    };
    localStorage.setItem('uploadedFile', JSON.stringify(fileData));
    performAnalysis(fileData);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Store file in localStorage for persistence
      const reader = new FileReader();
      reader.onload = (event) => {
        const arrayBuffer = event.target?.result as ArrayBuffer;
        const fileData = {
          name: file.name,
          type: file.type,
          data: Array.from(new Uint8Array(arrayBuffer)),
        };
        localStorage.setItem('uploadedFile', JSON.stringify(fileData));
        performAnalysis(fileData);
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const copyCode = () => {
    const code = codeType === 'basic' ? analysisData?.cleaning_code.basic : analysisData?.cleaning_code.advanced;
    if (code) {
      navigator.clipboard.writeText(code);
      setCodeCopied(true);
      setTimeout(() => setCodeCopied(false), 2000);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <Badge className="bg-red-100 text-red-700">High Priority</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-700">Medium Priority</Badge>;
      case 'low':
        return <Badge className="bg-blue-100 text-blue-700">Low Priority</Badge>;
      default:
        return null;
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-slate-600">Analyzing your dataset...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!analysisData || error) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Data Quality Analysis</h1>
            <p className="text-slate-600">AI-powered insights into your dataset quality</p>
          </div>

          <Card className="p-8 text-center">
            {error && (
              <div className="mb-4">
                <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">{error}</p>
              </div>
            )}

            <div className="mb-6">
              <p className="text-slate-600 mb-4">Upload a CSV or Excel file to analyze</p>
            </div>

            <div className="border-2 border-dashed border-slate-300 rounded-lg p-8">
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <div className="flex flex-col gap-4">
                <label htmlFor="file-upload">
                  <Button className="cursor-pointer" asChild>
                    <span className="flex items-center gap-2">
                      <Upload className="h-4 w-4" />
                      Upload Dataset
                    </span>
                  </Button>
                </label>
                <div className="text-slate-500 text-sm">or</div>
                <Button onClick={handleTestData} variant="outline" className="flex items-center gap-2">
                  <span>Test with Sample Data</span>
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  const issues = [
    {
      type: 'Missing Values',
      count: analysisData.profile.missing_values.total_missing_values,
      severity: analysisData.profile.missing_values.total_missing_values > 0 ? (Object.values(analysisData.profile.missing_values.columns_with_missing).some((col: any) => col.percentage > 50) ? 'high' : 'medium') : 'low',
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      columns: Object.keys(analysisData.profile.missing_values.columns_with_missing),
    },
    ...(analysisData.profile.duplicates.total_duplicate_rows > 0 ? [{
      type: 'Duplicate Rows',
      count: analysisData.profile.duplicates.total_duplicate_rows,
      severity: analysisData.profile.duplicates.duplicate_percentage > 10 ? 'high' : analysisData.profile.duplicates.duplicate_percentage > 5 ? 'medium' : 'low',
      icon: Copy,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      columns: [],
    }] : []),
    ...(Object.keys(analysisData.profile.outliers.columns_with_outliers).length > 0 ? [{
      type: 'Outliers',
      count: Object.values(analysisData.profile.outliers.columns_with_outliers).reduce((sum: number, col: any) => sum + col.count, 0),
      severity: 'medium',
      icon: AlertTriangle,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      columns: Object.keys(analysisData.profile.outliers.columns_with_outliers),
    }] : []),
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Data Quality Analysis</h1>
              <p className="text-slate-600">AI-powered insights into your dataset quality</p>
            </div>
            {uploadedFile && (
              <div className="text-right">
                <p className="text-sm text-slate-600">File: {uploadedFile.name}</p>
              </div>
            )}
          </div>
        </div>

        {/* Health Score Card */}
        <div className="mb-8">
          <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-2">Dataset Health Score</h2>
                <p className="text-slate-600 text-sm">Overall data quality assessment</p>
              </div>
              <div className={`text-5xl font-bold ${getHealthScoreColor(analysisData.profile.health_score)}`}>
                {analysisData.profile.health_score}
                <span className="text-xl text-slate-400 ml-2">/100</span>
              </div>
            </div>
            <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  analysisData.profile.health_score >= 80
                    ? 'bg-green-500'
                    : analysisData.profile.health_score >= 60
                    ? 'bg-yellow-500'
                    : analysisData.profile.health_score >= 40
                    ? 'bg-orange-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${analysisData.profile.health_score}%` }}
              ></div>
            </div>
          </Card>
        </div>

        {/* Dataset Overview */}
        <div className="mb-8">
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="p-6">
              <p className="text-sm text-slate-600 mb-2">Total Rows</p>
              <p className="text-2xl font-bold text-slate-900">{analysisData.profile.total_rows}</p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-slate-600 mb-2">Total Columns</p>
              <p className="text-2xl font-bold text-slate-900">{analysisData.profile.total_columns}</p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-slate-600 mb-2">Issues Found</p>
              <p className="text-2xl font-bold text-slate-900">{issues.filter(i => i.count > 0).length}</p>
            </Card>
          </div>
        </div>

        {/* Column Information */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Column Information</h2>
          <Card className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr className="bg-slate-50">
                    <th className="text-left py-3 px-4 font-semibold text-slate-900">Column Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-900">Data Type</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-900">Non-Null Count</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-900">Null Count</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-900">Unique Values</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData.profile.datatypes && Object.entries(analysisData.profile.datatypes).map(([colName, colData]: any) => (
                    <tr key={colName} className="border-b hover:bg-slate-50">
                      <td className="py-3 px-4 font-mono text-slate-900">{colName}</td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {colData.datatype}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-600">{colData.non_null_count}</td>
                      <td className="py-3 px-4 text-slate-600">{colData.null_count}</td>
                      <td className="py-3 px-4 text-slate-600">{colData.unique_values}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        {/* Detected Issues */}
        {issues.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">Detected Issues</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {issues.map((issue, idx) => {
                const Icon = issue.icon;
                return (
                  <Card key={idx} className={`p-6 border-l-4 ${issue.borderColor}`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${issue.bgColor}`}>
                          <Icon className={`h-5 w-5 ${issue.color}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900">{issue.type}</h3>
                          {getSeverityBadge(issue.severity)}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-600">Count</span>
                        <span className="font-semibold text-slate-900">{issue.count}</span>
                      </div>

                      {issue.columns.length > 0 && (
                        <div>
                          <span className="text-sm text-slate-600 block mb-2">Affected Columns</span>
                          <div className="flex flex-wrap gap-2">
                            {issue.columns.slice(0, 3).map((col) => (
                              <Badge key={col} variant="outline" className="text-xs">
                                {col}
                              </Badge>
                            ))}
                            {issue.columns.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{issue.columns.length - 3} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">AI Recommendations</h2>
          <Card className="p-6">
            <div className="space-y-4">
              {analysisData.recommendations && analysisData.recommendations.length > 0 ? (
                analysisData.recommendations.slice(0, 8).map((rec, idx) => (
                  <div key={idx} className="flex gap-4 pb-4 border-b last:border-b-0 last:pb-0">
                    <div className="flex-shrink-0 mt-1">
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-slate-900">Column:</span>
                        <code className="px-2 py-0.5 bg-slate-100 text-slate-900 rounded text-sm font-mono">
                          {rec.column}
                        </code>
                        {getSeverityBadge(rec.severity)}
                      </div>
                      <p className="text-sm text-slate-600 mb-2">
                        <span className="font-medium">Issue:</span> {rec.problem}
                      </p>
                      <p className="text-sm text-blue-700 bg-blue-50 p-3 rounded">
                        <span className="font-medium">Recommendation:</span> {rec.recommendation}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-slate-600">No recommendations needed. Your dataset is clean!</p>
              )}
            </div>
          </Card>
        </div>

        {/* Generated Cleaning Code */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-slate-900">Generated Cleaning Code</h2>
            <div className="flex gap-2">
              <Button
                variant={codeType === 'basic' ? 'default' : 'outline'}
                onClick={() => setCodeType('basic')}
              >
                Basic
              </Button>
              <Button
                variant={codeType === 'advanced' ? 'default' : 'outline'}
                onClick={() => setCodeType('advanced')}
              >
                Advanced (sklearn)
              </Button>
              <Button
                onClick={copyCode}
                variant="outline"
                className={codeCopied ? 'border-green-500 text-green-600' : ''}
              >
                {codeCopied ? (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy Code
                  </>
                )}
              </Button>
            </div>
          </div>

          <Card className="p-0 overflow-hidden">
            <div className="bg-slate-900 text-slate-100 p-6 overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="text-sm font-mono leading-relaxed">
                <code>{codeType === 'basic' ? analysisData.cleaning_code.basic : analysisData.cleaning_code.advanced}</code>
              </pre>
            </div>
          </Card>

          <p className="text-xs text-slate-500 mt-2">
            This code is ready to use. Simply copy and paste it into your Python environment.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}
