'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TriangleAlert as AlertTriangle, Copy, CircleCheck as CheckCircle2, CircleAlert as AlertCircle, Circle as XCircle } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';

const mockAnalysis = {
  issues: [
    {
      type: 'Missing Values',
      severity: 'high',
      affectedRows: 150,
      totalRows: 1250,
      percentage: 12,
      columns: ['email', 'age', 'city'],
      icon: AlertCircle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
    },
    {
      type: 'Duplicate Rows',
      severity: 'medium',
      affectedRows: 23,
      totalRows: 1250,
      percentage: 1.8,
      columns: ['customer_id', 'email'],
      icon: Copy,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
    },
    {
      type: 'Outliers',
      severity: 'low',
      affectedRows: 45,
      totalRows: 1250,
      percentage: 3.6,
      columns: ['age', 'purchase_amount'],
      icon: AlertTriangle,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    {
      type: 'Invalid Data Types',
      severity: 'high',
      affectedRows: 67,
      totalRows: 1250,
      percentage: 5.4,
      columns: ['signup_date', 'purchase_amount'],
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
    },
  ],
  recommendations: [
    {
      column: 'email',
      issue: '12% missing values',
      recommendation: 'Remove rows with missing email addresses or mark as "unknown" if email is not critical',
    },
    {
      column: 'age',
      issue: '8% missing values',
      recommendation: 'Fill with median value (35 years)',
    },
    {
      column: 'city',
      issue: '4% missing values',
      recommendation: 'Fill with most common value ("New York") or use "Unknown"',
    },
    {
      column: 'purchase_amount',
      issue: '3.6% outliers detected (values > $1000)',
      recommendation: 'Cap values at 95th percentile ($850) or investigate high-value purchases',
    },
    {
      column: 'signup_date',
      issue: '5.4% invalid date formats',
      recommendation: 'Convert to standard ISO format (YYYY-MM-DD) using pandas.to_datetime()',
    },
  ],
  cleaningCode: `import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('customer_data.csv')

# Handle missing values
df['age'].fillna(df['age'].median(), inplace=True)
df['city'].fillna('Unknown', inplace=True)
df = df.dropna(subset=['email'])  # Remove rows with missing email

# Remove duplicate rows
df = df.drop_duplicates(subset=['customer_id', 'email'], keep='first')

# Handle outliers in purchase_amount
upper_limit = df['purchase_amount'].quantile(0.95)
df['purchase_amount'] = df['purchase_amount'].clip(upper=upper_limit)

# Fix data type issues
df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
df['purchase_amount'] = pd.to_numeric(df['purchase_amount'], errors='coerce')

# Save cleaned dataset
df.to_csv('customer_data_cleaned.csv', index=False)

print(f"Cleaned dataset: {len(df)} rows")
print(f"Removed {1250 - len(df)} rows during cleaning")`,
};

export default function AnalysisPage() {
  const [codeCopied, setCodeCopied] = useState(false);

  const copyCode = () => {
    navigator.clipboard.writeText(mockAnalysis.cleaningCode);
    setCodeCopied(true);
    setTimeout(() => setCodeCopied(false), 2000);
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
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

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Data Quality Analysis</h1>
          <p className="text-slate-600">AI-powered insights into your dataset quality</p>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">Detected Issues</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {mockAnalysis.issues.map((issue, idx) => {
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
                      <span className="text-sm text-slate-600">Affected Rows</span>
                      <span className="font-semibold text-slate-900">
                        {issue.affectedRows} / {issue.totalRows} ({issue.percentage}%)
                      </span>
                    </div>

                    <div>
                      <span className="text-sm text-slate-600 block mb-2">Affected Columns</span>
                      <div className="flex flex-wrap gap-2">
                        {issue.columns.map((col) => (
                          <Badge key={col} variant="outline" className="text-xs">
                            {col}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4">AI Recommendations</h2>
          <Card className="p-6">
            <div className="space-y-4">
              {mockAnalysis.recommendations.map((rec, idx) => (
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
                    </div>
                    <p className="text-sm text-slate-600 mb-2">
                      <span className="font-medium">Issue:</span> {rec.issue}
                    </p>
                    <p className="text-sm text-blue-700 bg-blue-50 p-3 rounded">
                      <span className="font-medium">Recommendation:</span> {rec.recommendation}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-slate-900">Generated Cleaning Code</h2>
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

          <Card className="p-0 overflow-hidden">
            <div className="bg-slate-900 text-slate-100 p-6 overflow-x-auto">
              <pre className="text-sm font-mono leading-relaxed">
                <code>{mockAnalysis.cleaningCode}</code>
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
