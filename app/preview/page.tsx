'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Upload } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';

interface PreviewData {
  filename: string;
  columns: string[];
  rows: number;
  preview: Record<string, any>[];
}

export default function PreviewPage() {
  const router = useRouter();
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPreview = () => {
      try {
        setLoading(true);
        setError(null);

        // Get file from localStorage
        const storedFile = localStorage.getItem('uploadedFile');
        console.log("Stored file check:", storedFile ? "Found" : "Not found");
        
        if (!storedFile) {
          setError('No file found. Please upload a dataset first.');
          setLoading(false);
          return;
        }

        const fileData = JSON.parse(storedFile);
        const byteArray = new Uint8Array(fileData.data);
        const file = new File([byteArray], fileData.name, { type: fileData.type });

        console.log("Reconstructed file:", file.name, file.size);

        // Call upload endpoint to get preview
        const formData = new FormData();
        formData.append('file', file);

        fetch('http://127.0.0.1:9000/upload', {
          method: 'POST',
          body: formData,
        })
          .then((response) => {
            console.log("Response status:", response.status);
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then((data) => {
            console.log("Preview data received:", data);
            setPreviewData({
              filename: data.filename,
              columns: data.columns,
              rows: data.rows,
              preview: data.preview,
            });
            setLoading(false);
          })
          .catch((err) => {
            console.error('Preview error:', err);
            setError('Failed to load dataset preview. Please upload again.');
            setLoading(false);
          });
      } catch (err) {
        console.error('Parse error:', err);
        setError('Failed to process dataset. Please upload again.');
        setLoading(false);
      }
    };

    loadPreview();
  }, []);

  const getTypeColor = (value: any) => {
    if (value === null) return 'bg-slate-100 text-slate-700';
    if (typeof value === 'number') {
      return Number.isInteger(value) ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700';
    }
    if (typeof value === 'string') {
      if (!isNaN(Date.parse(value))) return 'bg-orange-100 text-orange-700';
      return 'bg-purple-100 text-purple-700';
    }
    return 'bg-slate-100 text-slate-700';
  };

  const getTypeLabel = (value: any) => {
    if (value === null) return 'null';
    if (typeof value === 'number') {
      return Number.isInteger(value) ? 'integer' : 'float';
    }
    if (typeof value === 'string') {
      if (!isNaN(Date.parse(value))) return 'date';
      return 'string';
    }
    return 'object';
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-slate-600">Loading dataset preview...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !previewData) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Dataset Preview</h1>
            <p className="text-slate-600">Review your dataset before analysis</p>
          </div>

          <Card className="p-8 text-center">
            <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-600 mb-2">{error || 'No dataset loaded'}</p>
            <Button
              onClick={() => router.push('/upload')}
              className="bg-blue-500 hover:bg-blue-600"
            >
              Upload Dataset
            </Button>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Dataset Preview</h1>
          <p className="text-slate-600">Review your dataset before analysis</p>
        </div>

        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">{previewData.filename}</h2>
              <p className="text-sm text-slate-600 mt-1">
                {previewData.rows.toLocaleString()} rows × {previewData.columns.length} columns
              </p>
            </div>
            <Button
              onClick={() => router.push('/analysis')}
              className="bg-blue-500 hover:bg-blue-600"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Analyze Dataset
            </Button>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Column Names</h3>
            <div className="flex flex-wrap gap-2">
              {previewData.columns.map((col, idx) => {
                // Get type from first non-null value in preview data for this column
                const typeLabel = previewData.preview[0]
                  ? getTypeLabel(previewData.preview[0][col])
                  : 'unknown';
                const typeColor = previewData.preview[0]
                  ? getTypeColor(previewData.preview[0][col])
                  : 'bg-slate-100 text-slate-700';

                return (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-sm text-slate-700 font-medium">{col}</span>
                    <Badge className={typeColor} variant="secondary">
                      {typeLabel}
                    </Badge>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto max-h-96">
              <table className="w-full">
                <thead className="bg-slate-50 border-b sticky top-0">
                  <tr>
                    {previewData.columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-xs font-semibold text-slate-900 uppercase tracking-wider whitespace-nowrap"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {previewData.preview.map((row, rowIdx) => (
                    <tr key={rowIdx} className="hover:bg-slate-50">
                      {previewData.columns.map((col) => {
                        const value = row[col];
                        return (
                          <td
                            key={`${rowIdx}-${col}`}
                            className="px-4 py-3 text-sm text-slate-700 whitespace-nowrap"
                          >
                            {value !== null && value !== undefined ? (
                              <span>{String(value)}</span>
                            ) : (
                              <span className="text-red-500 italic">null</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <p className="text-xs text-slate-500 mt-4">
            Showing all {previewData.rows.toLocaleString()} rows and {previewData.columns.length} columns
          </p>
        </Card>
      </div>
    </DashboardLayout>
  );
}
