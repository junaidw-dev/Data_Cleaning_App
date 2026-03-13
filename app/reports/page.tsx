'use client';

import { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Download, Loader, AlertCircle } from 'lucide-react';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';
import { useProjects, Project, Dataset } from '@/hooks/useDataApi';
import { useAuth } from '@/app/context/AuthContext';

interface DatasetWithProject extends Dataset {
  projectName: string;
}

export default function ReportsPage() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { listProjects } = useProjects();
  const { token } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [datasets, setDatasets] = useState<DatasetWithProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    let cancelled = false;

    const loadDatasets = async () => {
      setLoading(true);
      setError(null);
      try {
        const projectData = await listProjects();
        if (cancelled) return;
        setProjects(projectData);

        if (projectData.length === 0) {
          setDatasets([]);
          return;
        }

        const allDatasets: DatasetWithProject[] = [];

        for (const project of projectData) {
          try {
            const response = await fetch(
              `${apiBaseUrl}/api/projects/${project.id}/datasets`,
              {
                headers: { Authorization: `Bearer ${token}` },
              }
            );
            
            if (response.ok) {
              const projectDatasets = await response.json();
              projectDatasets.forEach((dataset: Dataset) => {
                allDatasets.push({
                  ...dataset,
                  projectName: project.name,
                });
              });
            }
          } catch (err) {
            console.error(`Error loading datasets for project ${project.id}:`, err);
          }
        }

        if (!cancelled) {
          setDatasets(
            allDatasets.sort(
              (a, b) =>
                new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
            )
          );
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to load reports');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadDatasets();
    return () => {
      cancelled = true;
    };
  }, [apiBaseUrl, listProjects, token]);

  const handleDownload = async (datasetId: string, format: 'html' | 'csv') => {
    try {
      setDownloading((prev) => ({ ...prev, [`${datasetId}-${format}`]: true }));

      const endpoint = format === 'html' 
        ? `/api/datasets/${datasetId}/report/html`
        : `/api/datasets/${datasetId}/download-cleaned`;

      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to download ${format.toUpperCase()} report`);
      }

      // Get filename from content-disposition header or use default
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `report-${datasetId}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+?)"/);
        if (filenameMatch) filename = filenameMatch[1];
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Download failed';
      setError(`Error: ${message}`);
    } finally {
      setDownloading((prev) => ({ ...prev, [`${datasetId}-${format}`]: false }));
    }
  };

  const projectNameById = useMemo(() => {
    return projects.reduce<Record<string, string>>((acc, project) => {
      acc[project.id] = project.name;
      return acc;
    }, {});
  }, [projects]);

  const recentDatasets = useMemo(() => {
    return datasets.slice(0, 10);
  }, [datasets]);

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Reports</h1>
            <p className="text-slate-600 mt-1">Download data quality reports and cleaned datasets</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="p-6 border border-slate-100">
              <p className="text-sm font-medium text-slate-600">Total Datasets</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">{datasets.length}</p>
            </Card>
            <Card className="p-6 border border-slate-100">
              <p className="text-sm font-medium text-slate-600">Available HTML Reports</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">{datasets.length}</p>
            </Card>
            <Card className="p-6 border border-slate-100">
              <p className="text-sm font-medium text-slate-600">Cleaned CSVs</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">{datasets.length}</p>
            </Card>
            <Card className="p-6 border border-slate-100">
              <p className="text-sm font-medium text-slate-600">Projects</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">{projects.length}</p>
            </Card>
          </div>

          {/* Error Message */}
          {error && (
            <Card className="p-4 mb-6 border border-red-200 bg-red-50">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-red-900">Error</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Reports Table */}
          <Card className="border border-slate-100 overflow-hidden">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-lg font-semibold text-slate-900">Datasets & Reports</h2>
            </div>

            {loading ? (
              <div className="p-12 text-center">
                <Loader className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-slate-600 font-medium">Loading reports...</p>
              </div>
            ) : recentDatasets.length === 0 ? (
              <div className="p-12 text-center">
                <FileText className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 mb-4">No datasets available yet.</p>
                <Button
                  onClick={() => window.location.href = '/upload'}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Upload Your First Dataset
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Dataset Name
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Project
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Size
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Uploaded
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Health Score
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-900">
                        Download
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {recentDatasets.map((dataset) => (
                      <tr key={dataset.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-blue-600 flex-shrink-0" />
                            <div>
                              <p className="text-sm font-medium text-slate-900">
                                {dataset.filename}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-slate-600">{dataset.projectName}</span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {Math.round(dataset.size_bytes / 1024)} KB
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {new Date(dataset.upload_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`text-xs font-semibold px-3 py-1 rounded-full ${
                              typeof dataset.health_score === 'number' && dataset.health_score >= 70
                                ? 'bg-green-100 text-green-700'
                                : typeof dataset.health_score === 'number' && dataset.health_score >= 50
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {typeof dataset.health_score === 'number'
                              ? `${Math.round(dataset.health_score)}%`
                              : '—'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownload(dataset.id, 'html')}
                              disabled={downloading[`${dataset.id}-html`]}
                              className="text-xs whitespace-nowrap"
                              title="Download HTML Report with data quality analysis"
                            >
                              {downloading[`${dataset.id}-html`] ? (
                                <>
                                  <Loader className="h-3 w-3 mr-1 animate-spin" />
                                  HTML
                                </>
                              ) : (
                                <>
                                  <Download className="h-3 w-3 mr-1" />
                                  HTML
                                </>
                              )}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownload(dataset.id, 'csv')}
                              disabled={downloading[`${dataset.id}-csv`]}
                              className="text-xs whitespace-nowrap"
                              title="Download cleaned CSV file"
                            >
                              {downloading[`${dataset.id}-csv`] ? (
                                <>
                                  <Loader className="h-3 w-3 mr-1 animate-spin" />
                                  CSV
                                </>
                              ) : (
                                <>
                                  <Download className="h-3 w-3 mr-1" />
                                  CSV
                                </>
                              )}
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {/* Info Section */}
          <Card className="p-6 mt-8 bg-blue-50 border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-3">About Your Reports</h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li>• <strong>HTML Report</strong> - Complete data quality analysis with statistics and visualizations</li>
              <li>• <strong>Cleaned CSV</strong> - Your dataset with data cleaning applied, ready to use</li>
              <li>• Reports are generated immediately and reflect your latest analysis</li>
              <li>• All data stays private and is processed securely</li>
            </ul>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
